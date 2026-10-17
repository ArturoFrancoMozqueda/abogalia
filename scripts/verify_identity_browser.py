"""Real local browser/API/PostgreSQL verification; Auth HTTP is synthetic, never live."""

import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
NODE_ROOT = Path("/Users/arturo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node")

BROWSER_KEYS = frozenset(
    {
        "invalid_login",
        "password_cleared_after_error",
        "valid_login",
        "account_visible",
        "storage_and_location_clean",
        "cookie_flags",
        "session_not_readable_by_javascript",
        "logout_status",
        "logged_out_session",
        "auth_urls_clean",
        "console_clean",
    }
)
BROWSER_STATUSES = frozenset({"passed", "failed", "browser_failed"})


# Node emits booleans only. Never serialize cookies, request bodies, headers, URL
# values, DOM containing MFA setup, screenshots or browser error messages.
BROWSER_SCRIPT = r"""
const {chromium}=require(process.argv[1]);
(async()=>{
 let browser;
 const checks={};
 try {
  browser=await chromium.launch({executablePath:process.argv[2],headless:true});
  const context=await browser.newContext();
  const page=await context.newPage();
  const badUrls=[];
  const badConsole=[];
  page.on('request',r=>{
   const u=new URL(r.url());
   // Record a boolean only; never retain URL or request body/headers.
   if (u.origin==='http://127.0.0.1:5191' && u.pathname.startsWith('/api/auth')) {
    if(u.search || u.hash || r.url().includes('synthetic-valid-password')) badUrls.push(true);
   }
  });
  page.on('console',m=>{
   const text=m.text();
   if(text.includes('synthetic-valid-password') || text.includes('access_token')
      || text.includes('refresh_token')) badConsole.push(true);
  });
  await page.goto('http://127.0.0.1:5191/acceso');
  await page.getByLabel('Correo electrónico',{exact:true}).fill('browser@example.invalid');
  await page.getByLabel('Contraseña',{exact:true}).fill('synthetic-invalid-password');
  const invalid=page.waitForResponse(r=>r.url().endsWith('/api/auth/login'));
  await page.getByRole('button',{name:'Entrar',exact:true}).click();
  checks.invalid_login=(await invalid).status()===401;
  await page.getByRole('alert').filter({hasText:'No pudimos iniciar sesión'}).waitFor();
  checks.password_cleared_after_error=await page.locator('input[name=password]').inputValue()==='';
  await page.getByLabel('Contraseña',{exact:true}).fill('synthetic-valid-password');
  const valid=page.waitForResponse(r=>r.url().endsWith('/api/auth/login'));
  await page.getByRole('button',{name:'Entrar',exact:true}).click();
  checks.valid_login=(await valid).status()===200;
  await page.waitForURL('http://127.0.0.1:5191/cuenta');
  await page.getByText('Sesión activa.',{exact:true}).waitFor();
  checks.account_visible=true;
  checks.storage_and_location_clean=await page.evaluate(()=>
   Object.keys(localStorage).length===0 && Object.keys(sessionStorage).length===0
   && !location.search && !location.hash);
  // Inspect ONLY metadata. No cookie.value accessor, serialization or output.
  checks.cookie_flags=(await context.cookies()).some(({name,httpOnly,secure,sameSite,path})=>
   name==='abogalia_session' && httpOnly && !secure && sameSite==='Strict' && path==='/');
  checks.session_not_readable_by_javascript=await page.evaluate(()=>
   !document.cookie.split(';').some(part=>part.trim().startsWith('abogalia_session=')));
  const logout=page.waitForResponse(r=>r.url().endsWith('/api/auth/logout'));
  await page.getByRole('button',{name:'Cerrar sesión en este dispositivo',exact:true}).click();
  checks.logout_status=(await logout).status()===204;
  await page.getByText('Sesión cerrada.',{exact:true}).waitFor();
  checks.logged_out_session=await page.evaluate(async()=>{
   const response=await fetch('/api/auth/session',{cache:'no-store',credentials:'same-origin'});
   const data=await response.json();
   return response.status===200 && data.authenticated===false;
  });
  Object.assign(checks,{auth_urls_clean:(badUrls.length===0),console_clean:(badConsole.length===0)});
  console.log(JSON.stringify({status:Object.values(checks).every(Boolean)?'passed':'failed',checks}));
 }catch{
  console.log(JSON.stringify({status:'browser_failed',checks,diagnostics:'suppressed'}));
 }finally{if(browser)await browser.close();}
})().catch(()=>{console.log(JSON.stringify({status:'browser_failed',diagnostics:'suppressed'}));});
"""


def free(port):
    with socket.socket() as connection:
        return connection.connect_ex(("127.0.0.1", port)) != 0


def main():
    report = {"status": "verification_failed", "diagnostics": "suppressed"}
    stage = "setup"
    vite = None
    server = None
    api_thread = None
    temporary_config = None
    temporary_passfile = None
    provider = None
    database_created = False
    source = None
    try:
        # Presence only: do not read runtime values or import the global app when
        # any live Identity configuration might exist in the caller environment.
        if any(name.startswith("ABOGALIA_") for name in os.environ):
            stage = "environment_guard"
            raise RuntimeError
        if not free(8091) or not free(5191):
            raise RuntimeError
        # Imports use the repository baseline. Launch with env -i as documented;
        # no dotenv is read and no live credentials are accepted by this runner.
        sys.path.insert(0, str(ROOT / "apps/api/src"))
        import httpx
        import jwt
        import psycopg
        import uvicorn
        from abogalia_api.identity.config import Settings
        from abogalia_api.identity.provider import SupabaseProvider
        from abogalia_api.identity.storage import (
            PostgresSessionProbe,
            PostgresSessionStore,
        )
        from abogalia_api.main import create_app
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives.asymmetric import ec
        from psycopg.conninfo import make_conninfo

        cluster = Path("/tmp/abogalia-pg-path").read_text().strip()
        pg_socket = Path(cluster) / "socket"
        if not pg_socket.is_absolute() or not pg_socket.is_dir():
            raise RuntimeError
        fd, passfile_name = tempfile.mkstemp(prefix="abogalia-browser-empty-passfile-")
        os.close(fd)
        temporary_passfile = Path(passfile_name)  # Empty mode0600, no real credential file.
        source = make_conninfo(
            host=str(pg_socket),
            port=54982,
            dbname="postgres",
            user="abogalia_test_owner",
            password="",
            passfile=str(temporary_passfile),
        )
        with psycopg.connect(source, autocommit=True) as conn:
            exists = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname='abogalia_browser_test'"
            ).fetchone()
            if exists:
                # Never overwrite an existing database from another run/task.
                raise RuntimeError
            for role in (
                "abogalia_identity_owner",
                "abogalia_identity_runtime",
                "abogalia_identity_probe",
            ):
                if not conn.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (role,)).fetchone():
                    raise RuntimeError
            conn.execute("CREATE DATABASE abogalia_browser_test OWNER abogalia_identity_owner")
            database_created = True
        admin = make_conninfo(source, dbname="abogalia_browser_test")
        runtime = make_conninfo(admin, user="abogalia_identity_runtime")
        probe_dsn = make_conninfo(admin, user="abogalia_identity_probe")
        with psycopg.connect(admin, autocommit=True) as conn:
            conn.execute((ROOT / "apps/api/migrations/001_identity.sql").read_text())
            conn.execute("CREATE SCHEMA auth AUTHORIZATION abogalia_identity_owner")
            conn.execute("CREATE TABLE auth.sessions(id uuid PRIMARY KEY,user_id uuid NOT NULL)")
            conn.execute("REVOKE ALL ON SCHEMA auth FROM PUBLIC")
            conn.execute("REVOKE ALL ON auth.sessions FROM PUBLIC")
            conn.execute("GRANT USAGE ON SCHEMA auth TO abogalia_identity_probe")
            conn.execute("GRANT SELECT(id,user_id) ON auth.sessions TO abogalia_identity_probe")
        stage = "api_start"
        settings = Settings(
            project_url="http://localhost:9999",
            publishable_key="sb_publishable_synthetic",
            csrf_key=secrets.token_bytes(32),
        )
        # Harness-only alternate ports authorized by A0. Never changes Settings
        # validation or application defaults (5190/8090).
        object.__setattr__(settings, "origin", "http://127.0.0.1:5191")
        key = ec.generate_private_key(ec.SECP256R1())
        public = json.loads(jwt.algorithms.ECAlgorithm.to_jwk(key.public_key()))
        public.update(kid="browser-synthetic", alg="ES256", use="sig")
        subject, session_id = str(uuid4()), str(uuid4())
        provider_counts = {"password": 0, "logout": 0}

        def provider_http(request):
            path = request.url.path.removeprefix("/auth/v1")
            if path == "/.well-known/jwks.json":
                return httpx.Response(200, json={"keys": [public]})
            if path == "/token":
                body = json.loads(request.content)
                if body.get("password") != "synthetic-valid-password":
                    return httpx.Response(400, json={"code": "invalid_credentials"})
                with psycopg.connect(admin) as conn:
                    conn.execute(
                        "INSERT INTO auth.sessions(id,user_id) VALUES(%s,%s) "
                        "ON CONFLICT DO NOTHING",
                        (session_id, subject),
                    )
                now = int(datetime.now(UTC).timestamp())
                token = jwt.encode(
                    {
                        "iss": settings.issuer,
                        "aud": "authenticated",
                        "sub": subject,
                        "session_id": session_id,
                        "iat": now,
                        "exp": now + 900,
                        "aal": "aal1",
                    },
                    key,
                    algorithm="ES256",
                    headers={"kid": "browser-synthetic"},
                )
                provider_counts["password"] += 1
                return httpx.Response(
                    200,
                    json={
                        "access_token": token,
                        "refresh_token": secrets.token_urlsafe(32),
                        "user": {
                            "id": subject,
                            "email": "browser@example.invalid",
                            "email_confirmed_at": datetime.now(UTC).isoformat(),
                        },
                    },
                )
            if path == "/user":
                return httpx.Response(200, json={"factors": []})
            if path == "/logout":
                with psycopg.connect(admin) as conn:
                    conn.execute("DELETE FROM auth.sessions WHERE id=%s", (session_id,))
                provider_counts["logout"] += 1
                return httpx.Response(204)
            return httpx.Response(503, json={})

        provider = SupabaseProvider(
            settings, httpx.Client(transport=httpx.MockTransport(provider_http))
        )
        store = PostgresSessionStore(runtime, Fernet.generate_key())
        probe = PostgresSessionProbe(probe_dsn)
        app = create_app(settings=settings, store=store, probe=probe, provider=provider)
        server = uvicorn.Server(
            uvicorn.Config(
                app,
                host="127.0.0.1",
                port=8091,
                access_log=False,
                log_config=None,
                log_level="critical",
            )
        )
        api_thread = threading.Thread(target=server.run, daemon=True)
        api_thread.start()
        deadline = time.monotonic() + 20
        while not server.started:
            if time.monotonic() > deadline:
                raise RuntimeError
            time.sleep(0.1)
        stage = "vite_start"
        node = NODE_ROOT / "bin/node"
        cli = ROOT / "apps/web/node_modules/@react-router/dev/bin.cjs"
        fd, name = tempfile.mkstemp(
            prefix="identity-browser-", suffix=".config.ts", dir=ROOT / "apps/web"
        )
        os.close(fd)
        temporary_config = Path(name)
        temporary_config.write_text(
            'import {reactRouter} from "@react-router/dev/vite";\n'
            'import {defineConfig} from "vite";\n'
            "export default defineConfig({envDir:false,plugins:[reactRouter()],"
            'server:{host:"127.0.0.1",port:5191,strictPort:true,'
            'proxy:{"/api":{target:"http://127.0.0.1:8091"}}}});\n'
        )
        clean_env = {
            "PATH": str(node.parent) + ":" + os.defpath,
            "LANG": "C",
            "LC_ALL": "C",
        }
        vite = subprocess.Popen(
            [
                str(node),
                str(cli),
                "dev",
                "--config",
                str(temporary_config),
                "--logLevel",
                "silent",
            ],
            cwd=ROOT / "apps/web",
            env=clean_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + 30
        with httpx.Client(trust_env=False) as check:
            while True:
                if vite.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError
                try:
                    if check.get("http://127.0.0.1:5191/acceso").status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.2)
        stage = "browser"
        candidates = sorted(
            (Path.home() / "Library/Caches/ms-playwright").glob(
                "chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell"
            )
        )
        if not candidates:
            raise RuntimeError
        playwright = NODE_ROOT / "node_modules/playwright"
        run = subprocess.run(
            [str(node), "-e", BROWSER_SCRIPT, str(playwright), str(candidates[-1])],
            env=clean_env,
            cwd=ROOT,
            capture_output=True,
            timeout=60,
            check=False,
        )
        result = json.loads(run.stdout.decode().strip())
        # No arbitrary status/field names can reach the public report. The entire
        # fixed browser contract must be present, even when a run reports failure.
        if (
            run.returncode != 0
            or not isinstance(result, dict)
            or result.get("status") not in BROWSER_STATUSES
            or not set(result).issubset({"status", "checks", "diagnostics"})
        ):
            raise RuntimeError
        raw_checks = result.get("checks")
        if (
            not isinstance(raw_checks, dict)
            or set(raw_checks) != BROWSER_KEYS
            or not all(type(value) is bool for value in raw_checks.values())
        ):
            raise RuntimeError
        checks = {name: raw_checks[name] for name in sorted(BROWSER_KEYS)}
        stage = "sql_persistence"
        with psycopg.connect(admin) as conn:
            sessions = conn.execute("SELECT count(*) FROM identity.app_sessions").fetchone()[0]
            auth_sessions = conn.execute("SELECT count(*) FROM auth.sessions").fetchone()[0]
            events = conn.execute(
                "SELECT count(*) FROM identity.audit WHERE action='session_deleted'"
            ).fetchone()[0]
        checks["sql_logout_persisted"] = sessions == 0 and auth_sessions == 0 and events >= 1
        checks["synthetic_provider_used"] = provider_counts == {
            "password": 1,
            "logout": 1,
        }
        report = {
            "status": "passed"
            if result.get("status") == "passed" and all(checks.values())
            else "failed",
            "checks": checks,
            "provider": "synthetic_http_transport",
            "database": "real_isolated_postgresql",
            "raw_diagnostics": "suppressed",
        }
    except Exception:  # noqa: BLE001 - Never expose browser/provider/SQL diagnostics.
        report = {
            "status": "verification_failed",
            "stage": stage,
            "diagnostics": "suppressed",
        }
    finally:
        cleanup = True
        if vite is not None:
            try:
                vite.terminate()
                try:
                    vite.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    vite.kill()
                    vite.wait(timeout=5)
            except Exception:  # noqa: BLE001 - Cleanup must not print diagnostics.
                cleanup = False
        try:
            if server is not None:
                server.should_exit = True
            if api_thread is not None:
                api_thread.join(timeout=10)
                cleanup = cleanup and not api_thread.is_alive()
        except Exception:  # noqa: BLE001 - Cleanup must not print diagnostics.
            cleanup = False
        if provider is not None:
            try:
                provider.client.close()
            except Exception:  # noqa: BLE001 - Cleanup must not print diagnostics.
                cleanup = False
        if database_created:
            try:
                import psycopg

                with psycopg.connect(source, autocommit=True) as conn:
                    conn.execute("DROP DATABASE abogalia_browser_test")
            except Exception:  # noqa: BLE001 - Cleanup must not print diagnostics.
                cleanup = False
        for artifact in (temporary_config, temporary_passfile):
            if artifact is not None:
                try:
                    artifact.unlink(missing_ok=True)
                except Exception:  # noqa: BLE001 - Cleanup must not print diagnostics.
                    cleanup = False
        try:
            cleanup = cleanup and (server is None or free(8091)) and (vite is None or free(5191))
        except Exception:  # noqa: BLE001 - Cleanup must not print diagnostics.
            cleanup = False
        report["owned_resources_cleaned"] = cleanup
        if not cleanup:
            report["status"] = "cleanup_failed"
    print(json.dumps(report))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    # Only fixed JSON evidence is emitted. libpq/browser child diagnostics are
    # intentionally suppressed too; no raw provider/SQL details can escape.
    with open(os.devnull, "w") as diagnostic_sink:
        os.dup2(diagnostic_sink.fileno(), 2)
        raise SystemExit(main())
