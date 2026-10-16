"""Synthetic injected production configuration; no provider, dotenv or database access."""

import asyncio
import json
import os
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from cryptography.fernet import Fernet

from abogalia_api import production

API = Path(__file__).parents[1]


@pytest.fixture
def values(monkeypatch):
    environment = {
        "ABOGALIA_ENVIRONMENT": "production",
        "ABOGALIA_IDENTITY_ENABLED": "0",
        "ABOGALIA_WEB_ORIGIN": "https://legalia-public.example.invalid",
    }
    monkeypatch.setattr(os, "environ", environment)
    return environment


def enable(values):
    values.update(
        {
            "ABOGALIA_IDENTITY_ENABLED": "1",
            "ABOGALIA_SUPABASE_URL": production.PROJECT,
            "ABOGALIA_SUPABASE_PUBLISHABLE_KEY": "sb_publishable_PUBLIC_SYNTHETIC",
            "ABOGALIA_CSRF_KEY": "PUBLIC_SYNTHETIC_ONLY_" * 2,
            "ABOGALIA_SESSION_CIPHER_KEY": Fernet.generate_key().decode(),
            "ABOGALIA_DATABASE_DSN": (
                "host=db.spohytnxscljtitvmdab.supabase.co port=5432 dbname=postgres "
                "user=abogalia_identity_runtime password=PUBLIC_SYNTHETIC_ONLY "
                "sslmode=verify-full sslrootcert=" + production.CA_PATH
            ),
        }
    )


def test_explicit_off_bootstrap_has_production_secure_cookies(values, monkeypatch):
    monkeypatch.delitem(sys.modules, "abogalia_api.main", raising=False)
    production.validate_environment()
    app = production.build_app()
    settings = app.state.identity.settings
    assert not app.debug and not settings.development_http and not settings.configured
    assert settings.origin == values["ABOGALIA_WEB_ORIGIN"]
    assert settings.session_cookie.startswith("__Host-")

    async def exercise():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app), base_url=settings.origin
        ) as client:
            assert (await client.get("/api/health")).status_code == 200
            assert (await client.get("/api/health/")).status_code == 404
            response = await client.get("/api/auth/session")
            assert response.status_code == 200 and response.json() == {"authenticated": False}
            assert response.headers["cache-control"] == "no-store"

    asyncio.run(exercise())


def test_enabled_configuration_preserves_project_roles_tls_and_cipher_without_connecting(
    values, monkeypatch
):
    import psycopg

    enable(values)
    monkeypatch.setattr(psycopg, "connect", lambda *a, **kw: pytest.fail("network not allowed"))
    production.validate_environment()


@pytest.mark.parametrize(
    "name,value",
    [
        ("ABOGALIA_ENVIRONMENT", "development"),
        ("ABOGALIA_ENVIRONMENT", ""),
        ("ABOGALIA_IDENTITY_ENABLED", ""),
        ("ABOGALIA_IDENTITY_ENABLED", "yes"),
        ("ABOGALIA_AUTH_EMAIL_READY", "yes"),
        ("WEB_CONCURRENCY", "2"),
        ("UVICORN_WORKERS", "1"),
        ("UVICORN_RELOAD", "true"),
        ("GUNICORN_CMD_ARGS", "--workers 2"),
        ("FORWARDED_ALLOW_IPS", "*"),
        ("PGHOSTADDR", "PUBLIC_SYNTHETIC"),
        ("PGSERVICE", "PUBLIC_SYNTHETIC"),
    ],
)
def test_invalid_modes_or_external_overrides_fail_before_app(values, name, value, capsys):
    values[name] = value
    code = production.main([], factory=lambda: pytest.fail("app must not load"))
    assert code == 2
    assert json.loads(capsys.readouterr().out) == {"status": "production_unavailable"}


@pytest.mark.parametrize(
    "origin",
    [
        "",
        "http://127.0.0.1:5190",
        "https://127.0.0.1",
        "https://localhost",
        "https://public.example.invalid/",
        "https://public.example.invalid/path",
        "https://public.example.invalid?secret=PUBLIC_SYNTHETIC",
        "https://public.example.invalid#fragment",
        "https://user:PUBLIC_SYNTHETIC@public.example.invalid",
        "https://*.example.invalid",
        "https://public.example.invalid:8080",
        "https://public.example.invalid:",
    ],
)
def test_exact_https_origin_required_even_when_disabled(values, origin):
    values["ABOGALIA_WEB_ORIGIN"] = origin
    with pytest.raises(production.ProductionUnavailable):
        production.validate_environment()


@pytest.mark.parametrize(
    "change",
    [
        "retired_project",
        "other_host",
        "elevated_role",
        "hostaddr",
        "options",
        "tls",
        "ca_system",
        "ca_macos",
        "missing_password",
        "cipher",
        "missing_csrf",
    ],
)
def test_bad_enabled_configuration_rejected_without_exposure(values, change):
    enable(values)
    dsn = values["ABOGALIA_DATABASE_DSN"]
    if change == "retired_project":
        values["ABOGALIA_SUPABASE_URL"] = "https://xggefantvuwpilksfdoy.supabase.co"
    elif change == "other_host":
        values["ABOGALIA_DATABASE_DSN"] = dsn.replace(
            "db.spohytnxscljtitvmdab.supabase.co", "unapproved.invalid"
        )
    elif change == "elevated_role":
        values["ABOGALIA_DATABASE_DSN"] = dsn.replace("abogalia_identity_runtime", "postgres")
    elif change in ("hostaddr", "options"):
        values["ABOGALIA_DATABASE_DSN"] += " " + change + "=PUBLIC_SYNTHETIC"
    elif change == "tls":
        values["ABOGALIA_DATABASE_DSN"] = dsn.replace("verify-full", "require")
    elif change in ("ca_system", "ca_macos"):
        values["ABOGALIA_DATABASE_DSN"] = dsn.replace(
            production.CA_PATH, "system" if change == "ca_system" else "/Users/private/ca.crt"
        )
    elif change == "missing_password":
        values["ABOGALIA_DATABASE_DSN"] = dsn.replace(" password=PUBLIC_SYNTHETIC_ONLY", "")
    elif change == "cipher":
        values["ABOGALIA_SESSION_CIPHER_KEY"] = "PUBLIC_SYNTHETIC_INVALID"
    else:
        del values["ABOGALIA_CSRF_KEY"]
    with pytest.raises(production.ProductionUnavailable) as error:
        production.validate_environment()
    assert (
        str(error.value) == "Production configuration unavailable" and error.value.__cause__ is None
    )


def test_native_python_and_exception_outputs_are_suppressed(values, capfd):
    def noisy_factory():
        print("PUBLIC_SYNTHETIC_PYTHON")
        os.write(1, b"PUBLIC_SYNTHETIC_NATIVE")
        os.write(2, b"PUBLIC_SYNTHETIC_NATIVE")
        raise RuntimeError("PUBLIC_SYNTHETIC_EXCEPTION")

    assert production.main([], factory=noisy_factory) == 2
    output = capfd.readouterr()
    assert output.err == "" and json.loads(output.out) == {"status": "production_unavailable"}


def test_no_arguments_or_diagnostic_payload_echo(values, capsys):
    assert production.main(["--workers", "PUBLIC_SYNTHETIC_ARGUMENT"]) == 2
    output = capsys.readouterr()
    assert "PUBLIC_SYNTHETIC_ARGUMENT" not in output.out + output.err


def test_server_fixed_single_process_no_proxy_or_dotenv(values, monkeypatch):
    import uvicorn

    calls = []
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    app = object()
    assert production.main([], factory=lambda: app) == 0
    assert calls == [
        (
            (app,),
            {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 1,
                "reload": False,
                "access_log": False,
                "log_config": None,
                "log_level": "critical",
                "env_file": None,
                "proxy_headers": False,
                "forwarded_allow_ips": "",
                "server_header": False,
            },
        )
    ]


def test_cached_app_cannot_reuse_another_runtime(values, monkeypatch):
    monkeypatch.setitem(sys.modules, "abogalia_api.main", SimpleNamespace(app=object()))
    with pytest.raises(production.ProductionUnavailable):
        production.build_app()


def test_packaging_digest_hash_lock_nonroot_and_no_secret_context():
    docker = (API / "Dockerfile").read_text()
    assert docker.startswith("FROM python:3.12.15-alpine3.24@sha256:")
    assert "--require-hashes --only-binary=:all:" in docker
    assert "USER 10001:10001" in docker and '"abogalia_api.production"' in docker
    assert "COPY . " not in docker and "ARG " not in docker
    ignore = (API / ".dockerignore").read_text().splitlines()
    rules = [line for line in ignore if line and not line.startswith("#")]
    assert rules[0] == "**" and "!src/**" not in rules
    assert not any("env" in line or "tests" in line or "venv" in line for line in rules[1:])
    assert (API / "certificates/supabase-prod-ca-2021.crt").is_file()


def test_fly_template_is_unassigned_single_vm_no_paid_extras():
    template = tomllib.loads((API / "fly.toml.example").read_text())
    assert "app" not in template and "primary_region" not in template
    assert template["vm"] == [{"cpu_kind": "shared", "cpus": 1, "memory": "1gb"}]
    assert template["http_service"]["internal_port"] == 8080
    assert template["http_service"]["force_https"] is True
    assert template["http_service"]["auto_stop_machines"] == "off"
    assert template["http_service"]["checks"][0]["path"] == "/api/health"
    assert template["deploy"]["strategy"] == "immediate"
    assert "mounts" not in template and "release_command" not in template.get("deploy", {})
