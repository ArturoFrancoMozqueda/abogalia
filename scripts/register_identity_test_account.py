"""One private test-account signup and OTP confirmation, using the existing mail budget."""

import importlib.util
import json
import logging
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "https://spohytnxscljtitvmdab.supabase.co"
CHECKS = (
    "request_accepted",
    "otp_verified",
    "identity_bound",
    "session_active",
    "original_unexpired",
    "local_revoked",
)


def helpers():
    spec = importlib.util.spec_from_file_location(
        "registration_pilot_helpers", ROOT / "scripts/run_identity_email_pilot.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def provider_factory(key):
    from abogalia_api.identity.config import Settings
    from abogalia_api.identity.provider import ProviderFailure, SupabaseProvider

    class ConfirmationProvider(SupabaseProvider):
        def _request(self, method, path, **kwargs):
            if (method, path) not in {
                ("POST", "/verify"),
                ("POST", "/logout"),
                ("GET", "/.well-known/jwks.json"),
            }:
                raise ProviderFailure()
            if path == "/verify" and kwargs.get("payload", {}).get("type") != "email":
                raise ProviderFailure()
            if path == "/logout" and kwargs.get("params") != {"scope": "local"}:
                raise ProviderFailure()
            return super()._request(method, path, **kwargs)

    return ConfirmationProvider(
        Settings(
            project_url=PROJECT,
            publishable_key=key,
            csrf_key=os.urandom(32),
            email_enabled=True,
        )
    )


def run(
    *,
    prompt,
    directory,
    env_file,
    clock=None,
    signup_factory=None,
    factory=provider_factory,
):
    from abogalia_api.identity.security import JWTVerifier
    from abogalia_api.identity.session_probe import ApiSessionProbe

    private = helpers()
    clock = clock or (lambda: datetime.now(UTC))
    checks = dict.fromkeys(CHECKS, False)
    status = "registration_pending"
    provider = pair = identity = verifier = probe = None
    password = confirmation = code = mailbox = None
    attempted = False
    cleanup = True
    try:
        if (
            prompt(
                "Cuenta APP sintética exclusiva en buzón autorizado, sin privilegios; "
                "máximo un correo del cupo existente. Escriba LISTO (oculto): "
            )
            != "LISTO"
        ):
            raise ValueError
        mailbox, digest = private.mailbox_hash(
            prompt("Buzón autorizado (entrada oculta): ")
        )
        password = prompt("Contraseña nueva (entrada oculta): ")
        confirmation = prompt("Repita contraseña nueva (entrada oculta): ")
        if (
            not isinstance(password, str)
            or not 8 <= len(password) <= 256
            or any(ord(char) < 32 for char in password)
            or password != confirmation
        ):
            raise ValueError
        # Only a wholly absent directory may initialize; never repair/reset an existing one.
        try:
            directory.lstat()
        except FileNotFoundError:
            answers = iter([mailbox])
            private.run(
                "initialize",
                directory=directory,
                env_file=env_file,
                prompt=lambda message: (
                    next(answers) if "Buzón" in message else prompt(message)
                ),
                clock=lambda: clock().timestamp(),
            )
        answers = iter([mailbox, password])
        result = private.run(
            "signup",
            directory=directory,
            env_file=env_file,
            prompt=lambda _: next(answers),
            clock=lambda: clock().timestamp(),
            factory=signup_factory or private.provider_factory,
        )
        password = confirmation = None
        if result["status"] != "accepted":
            cleanup = False
            raise ValueError
        checks["request_accepted"] = True
        code = prompt(
            "Solicitud aceptada no prueba entrega. Revise su buzón privado e introduzca "
            "OTP de confirmación de seis dígitos (oculto; nunca chat/captura): "
        )
        if not isinstance(code, str) or not re.fullmatch(r"[0-9]{6}", code):
            raise ValueError
        with private.marker_lock(directory):
            marker = private.read_marker(directory, int(clock().timestamp()))
            if marker["mailbox_hash"] != digest:
                raise ValueError
        provider = factory(private.publishable_key(env_file))
        if provider.settings.project_url != PROJECT:
            raise ValueError
        # A timeout/invalid response may have consumed OTP and created a session.
        cleanup = False
        pair = provider.verify_code(mailbox, code, "email")
        code = None
        checks["otp_verified"] = True
        verifier = JWTVerifier(provider.settings, provider.jwks)
        probe = ApiSessionProbe(provider.settings, provider, clock)
        identity = verifier.verify(pair.access_token, clock())
        checks["identity_bound"] = (
            identity.subject == pair.subject and pair.email.lower() == mailbox
        )
        if not checks["identity_bound"]:
            raise ValueError
        checks["session_active"] = probe.active(
            identity.provider_session_id,
            identity.subject,
            access_token=pair.access_token,
        )
        if not checks["session_active"]:
            raise ValueError
    except (Exception, KeyboardInterrupt):
        pass
    finally:
        # Exactly one local closure attempt for a known returned pair; never retry.
        if pair is not None and provider is not None and not attempted:
            attempted = True
            try:
                provider.logout(pair.access_token, "local")
                actual = (
                    verifier.verify(pair.access_token, clock()) if verifier else None
                )
                checks["original_unexpired"] = actual is not None and actual == identity
                if checks["identity_bound"] and checks["original_unexpired"]:
                    checks["local_revoked"] = (
                        probe.active(
                            identity.provider_session_id,
                            identity.subject,
                            access_token=pair.access_token,
                        )
                        is False
                    )
                    checks["original_unexpired"] &= (
                        verifier.verify(pair.access_token, clock()) == identity
                    )
                cleanup = checks["local_revoked"] and checks["original_unexpired"]
            except (Exception, KeyboardInterrupt):
                cleanup = False
        if provider is not None:
            try:
                provider.client.close()
            except (Exception, KeyboardInterrupt):
                cleanup = False
        password = confirmation = code = mailbox = pair = None
    if all(checks.values()) and cleanup:
        status = "verified"
    if not cleanup:
        status = "cleanup_failed"
    return {"status": status, "checks": checks, "cleanup": cleanup}


def main(argv=None):
    result = {
        "status": "registration_unavailable",
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
                directory=ROOT / ".identity-pilot",
                env_file=ROOT / ".env",
            )
    except (Exception, KeyboardInterrupt):
        pass
    finally:
        logging.disable(previous)
    print(json.dumps(result))
    return 0 if result["status"] == "verified" else 2


if __name__ == "__main__":
    raise SystemExit(main())
