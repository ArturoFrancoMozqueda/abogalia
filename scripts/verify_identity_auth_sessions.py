"""Private TTY acceptance of fixed-project Auth revocation; no email or runtime activation."""

import importlib.util
import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "https://spohytnxscljtitvmdab.supabase.co"
CHECKS = (
    "initial_sessions_valid",
    "distinct_sessions_same_subject",
    "local_original_unexpired",
    "local_revoked",
    "local_isolation",
    "global_sessions_valid",
    "global_originals_unexpired",
    "global_revoked_both",
    "original_local_still_revoked",
)


def helpers():
    spec = importlib.util.spec_from_file_location(
        "auth_acceptance_pilot_helpers", ROOT / "scripts/run_identity_email_pilot.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def provider_factory(key):
    from abogalia_api.identity.config import Settings
    from abogalia_api.identity.provider import ProviderFailure, SupabaseProvider

    class AcceptanceProvider(SupabaseProvider):
        def _request(self, method, path, **kwargs):
            if (method, path) not in {
                ("GET", "/.well-known/jwks.json"),
                ("POST", "/token"),
                ("POST", "/logout"),
            }:
                raise ProviderFailure()
            if path == "/token" and kwargs.get("params") != {"grant_type": "password"}:
                raise ProviderFailure()
            if path == "/logout" and kwargs.get("params", {}).get("scope") not in (
                "local",
                "global",
            ):
                raise ProviderFailure()
            return super()._request(method, path, **kwargs)

    settings = Settings(
        project_url=PROJECT,
        publishable_key=key,
        csrf_key=os.urandom(32),
    )
    return AcceptanceProvider(settings)


def run(*, prompt, key_loader, factory=provider_factory, clock=None):
    """Injection is for synthetic tests; CLI alone supplies private runtime inputs."""
    from abogalia_api.identity.security import JWTVerifier
    from abogalia_api.identity.session_probe import ApiSessionProbe

    private = helpers()
    checks = dict.fromkeys(CHECKS, False)
    sessions = []
    attempted = set()
    confirmed_closed = set()
    provider = None
    cleanup = True
    status = "verification_pending"
    clock = clock or (lambda: datetime.now(UTC))
    try:
        if (
            prompt(
                "Cuenta APP sintética confirmada/exclusiva, no administrativa; "
                "cierre global autorizado. Escriba LISTO: "
            )
            != "LISTO"
        ):
            raise ValueError
        mailbox, _ = private.mailbox_hash(prompt("Buzón de prueba (entrada oculta): "))
        password = prompt("Contraseña de prueba (entrada oculta): ")
        if (
            not isinstance(password, str)
            or not 8 <= len(password) <= 256
            or any(ord(char) < 32 for char in password)
        ):
            raise ValueError
        provider = factory(key_loader())
        if provider.settings.project_url != PROJECT:
            raise ValueError
        verifier = JWTVerifier(provider.settings, provider.jwks)
        probe = ApiSessionProbe(provider.settings, provider, clock)

        def login():
            nonlocal cleanup
            try:
                pair = provider.login(mailbox, password)
            except (Exception, KeyboardInterrupt):
                cleanup = False
                raise
            # Keep every returned token for best-effort cleanup even if binding fails.
            sessions.append(pair)
            identity = verifier.verify(pair.access_token, clock())
            if identity.subject != pair.subject or pair.email.lower() != mailbox:
                raise ValueError
            return pair, identity

        def active(session):
            pair, identity = session
            result = probe.active(
                identity.provider_session_id,
                identity.subject,
                access_token=pair.access_token,
            )
            verifier.verify(pair.access_token, clock())
            if result is False:
                confirmed_closed.add(id(pair))
            return result

        def original_valid(session):
            pair, identity = session
            return verifier.verify(pair.access_token, clock()) == identity

        def logout(session, scope):
            nonlocal cleanup
            pair, _ = session
            # A failed/ambiguous request is never retried by finally.
            attempted.add(id(pair))
            try:
                provider.logout(pair.access_token, scope)
            except (Exception, KeyboardInterrupt):
                cleanup = False
                raise

        a, b = login(), login()
        checks["initial_sessions_valid"] = active(a) and active(b)
        checks["distinct_sessions_same_subject"] = (
            a[1].subject == b[1].subject
            and a[1].provider_session_id != b[1].provider_session_id
        )
        if not all(checks[name] for name in CHECKS[:2]):
            raise ValueError
        logout(a, "local")
        checks["local_original_unexpired"] = original_valid(a)
        checks["local_revoked"] = active(a) is False
        checks["local_isolation"] = active(b) is True
        if not all(checks[name] for name in CHECKS[:5]):
            raise ValueError
        # A is already revoked. C gives global logout two *live* sessions B/C.
        c = login()
        checks["global_sessions_valid"] = (
            c[1].subject == b[1].subject
            and c[1].provider_session_id != b[1].provider_session_id
            and active(b)
            and active(c)
        )
        if not checks["global_sessions_valid"]:
            raise ValueError
        logout(b, "global")
        checks["global_originals_unexpired"] = original_valid(b) and original_valid(c)
        checks["global_revoked_both"] = active(b) is False and active(c) is False
        checks["original_local_still_revoked"] = active(a) is False
        # Expiry crossing a negative request cannot masquerade as revocation evidence.
        checks["global_originals_unexpired"] &= original_valid(b) and original_valid(c)
        checks["local_original_unexpired"] &= original_valid(a)
        if all(checks.values()):
            status = "verified"
            attempted.update(id(pair) for pair in sessions)
    except (Exception, KeyboardInterrupt):
        pass
    finally:
        if provider is not None:
            for pair in sessions:
                if id(pair) not in attempted:
                    attempted.add(id(pair))
                    try:
                        provider.logout(pair.access_token, "local")
                        identity = verifier.verify(pair.access_token, clock())
                        if (
                            probe.active(
                                identity.provider_session_id,
                                identity.subject,
                                access_token=pair.access_token,
                            )
                            is False
                        ):
                            verifier.verify(pair.access_token, clock())
                            confirmed_closed.add(id(pair))
                    except (Exception, KeyboardInterrupt):
                        cleanup = False
            if any(id(pair) not in confirmed_closed for pair in sessions):
                cleanup = False
            try:
                provider.client.close()
            except (Exception, KeyboardInterrupt):
                cleanup = False
        # Strings cannot be securely zeroized by Python; no persistence is performed.
        mailbox, password = None, None
    if not cleanup:
        status = "cleanup_failed"
    return {"status": status, "checks": checks, "cleanup": cleanup}


def main(argv=None):
    result = {
        "status": "verification_unavailable",
        "checks": dict.fromkeys(CHECKS, False),
        "cleanup": False,
    }
    previous = logging.root.manager.disable
    try:
        if (sys.argv[1:] if argv is None else argv) != ["--run"]:
            raise ValueError
        if not sys.stdin.isatty() or not sys.stderr.isatty():
            raise ValueError
        sys.path.insert(0, str(ROOT / "apps/api/src"))
        private = helpers()
        logging.disable(sys.maxsize)
        with private.launcher_helpers().silent_diagnostics():
            result = run(
                prompt=private.private_prompt,
                key_loader=lambda: private.publishable_key(ROOT / ".env"),
            )
    except (Exception, KeyboardInterrupt):
        pass
    finally:
        logging.disable(previous)
    print(json.dumps(result))
    return 0 if result["status"] == "verified" else 2


if __name__ == "__main__":
    raise SystemExit(main())
