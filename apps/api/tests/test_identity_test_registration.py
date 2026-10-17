"""Registration uses private synthetic files, ephemeral JWT and mock HTTP; no emails."""

import importlib.util
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

SPEC = importlib.util.spec_from_file_location(
    "test_account_registration",
    Path(__file__).parents[3] / "scripts/register_identity_test_account.py",
)
registration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registration)
MAIL = "public-synthetic@example.invalid"
PASSWORD = "PUBLIC_SYNTHETIC_PASSWORD_ONLY"


@pytest.fixture
def rig(tmp_path):
    private = registration.helpers()
    directory = tmp_path / "marker"
    env_file = tmp_path / "synthetic-config"
    env_file.write_text("ABOGALIA_SUPABASE_PUBLISHABLE_KEY=sb_publishable_PUBLIC_SYNTHETIC\n")
    env_file.chmod(0o600)
    now = [datetime.now(UTC)]
    calls = []
    state = {"mode": "normal", "live": False}
    key = ec.generate_private_key(ec.SECP256R1())
    jwk = json.loads(jwt.algorithms.ECAlgorithm.to_jwk(key.public_key()))
    jwk.update(kid="synthetic", alg="ES256", use="sig")
    subject, sid = str(uuid4()), str(uuid4())

    def handle(request):
        calls.append((request.method, request.url.path))
        assert request.url.host == "spohytnxscljtitvmdab.supabase.co"
        assert request.url.scheme == "https"
        path = request.url.path
        if path.endswith("/signup"):
            assert json.loads(request.content) == {"email": MAIL, "password": PASSWORD}
            marker = private.read_marker(directory, int(now[0].timestamp()))
            assert marker["reserved"] >= 1  # Durable reserve before transport.
            if state["mode"] == "duplicate":
                return httpx.Response(422, json={"code": "user_already_exists"})
            if state["mode"] == "signup_timeout":
                raise httpx.ReadTimeout("PUBLIC_SYNTHETIC_ERROR")
            return httpx.Response(200, json={"user": {"id": subject}})
        if path.endswith("/verify"):
            assert json.loads(request.content) == {
                "email": MAIL,
                "token": "123456",
                "type": "email",
            }
            if state["mode"] == "invalid_otp":
                return httpx.Response(403, json={"code": "otp_expired"})
            if state["mode"] == "verify_timeout":
                raise httpx.ReadTimeout("PUBLIC_SYNTHETIC_ERROR")
            state["live"] = True
            stamp = int(now[0].timestamp())
            raw = jwt.encode(
                {
                    "iss": registration.PROJECT + "/auth/v1",
                    "aud": "authenticated",
                    "iat": stamp,
                    "exp": stamp + 900,
                    "sub": subject,
                    "session_id": sid,
                    "aal": "aal1",
                },
                key,
                algorithm="ES256",
                headers={"kid": "synthetic"},
            )
            return httpx.Response(
                200,
                json={
                    "access_token": raw,
                    "refresh_token": "PUBLIC_SYNTHETIC_REFRESH",
                    "user": {"id": subject, "email": MAIL, "email_confirmed_at": "synthetic"},
                },
            )
        if path.endswith("/.well-known/jwks.json"):
            return httpx.Response(200, json={"keys": [jwk]})
        if path.endswith("/user"):
            if state["live"]:
                return httpx.Response(200, json={"id": subject})
            if state["mode"] == "generic_forbidden":
                return httpx.Response(403, json={"code": "generic"})
            return httpx.Response(403, json={"code": "session_not_found"})
        assert path.endswith("/logout") and dict(request.url.params) == {"scope": "local"}
        if state["mode"] == "logout_timeout":
            raise httpx.ReadTimeout("PUBLIC_SYNTHETIC_ERROR")
        if state["mode"] == "expiry":
            now[0] += timedelta(seconds=901)
        if state["mode"] != "ignores_logout":
            state["live"] = False
        return httpx.Response(204)

    def provider_factory(value):
        provider = registration.provider_factory(value)
        provider.client.close()
        provider.client = httpx.Client(transport=httpx.MockTransport(handle))
        return provider

    def signup_factory(value):
        return private.provider_factory(value, transport=httpx.MockTransport(handle))

    def invoke(answers=None):
        # Account attestation, mailbox, password twice, SMTP initialization, OTP.
        inputs = iter(answers or ["LISTO", MAIL, PASSWORD, PASSWORD, "LISTO", "123456"])
        return registration.run(
            prompt=lambda _: next(inputs),
            directory=directory,
            env_file=env_file,
            clock=lambda: now[0],
            signup_factory=signup_factory,
            factory=provider_factory,
        )

    return invoke, directory, now, state, calls, private


def test_signup_confirm_bound_session_and_observed_cleanup(rig):
    invoke, directory, now, _, calls, private = rig
    result = invoke()
    assert result == {
        "status": "verified",
        "checks": dict.fromkeys(registration.CHECKS, True),
        "cleanup": True,
    }
    assert sum(path.endswith("/signup") for _, path in calls) == 1
    assert sum(path.endswith("/verify") for _, path in calls) == 1
    assert sum(path.endswith("/logout") for _, path in calls) == 1
    assert private.read_marker(directory, int(now[0].timestamp()))["reserved"] == 1
    content = (directory / "authorization.json").read_text()
    assert MAIL not in content and PASSWORD not in content and "123456" not in content
    assert all(type(value) is bool for value in result["checks"].values())


@pytest.mark.parametrize(
    "mode",
    [
        "invalid_otp",
        "verify_timeout",
        "logout_timeout",
        "ignores_logout",
        "generic_forbidden",
        "expiry",
        "duplicate",
        "signup_timeout",
    ],
)
def test_fail_closed_no_resend_or_ambiguous_cleanup(rig, mode):
    invoke, directory, now, state, calls, private = rig
    state["mode"] = mode
    result = invoke()
    assert result["status"] == "cleanup_failed" and result["cleanup"] is False
    assert sum(path.endswith("/signup") for _, path in calls) == 1
    assert sum(path.endswith("/verify") for _, path in calls) <= 1
    assert sum(path.endswith("/logout") for _, path in calls) <= 1
    assert private.read_marker(directory, int(now[0].timestamp()))["reserved"] == 1
    assert "PUBLIC_SYNTHETIC" not in json.dumps(result)


@pytest.mark.parametrize("kind", ["expired", "cap", "corrupt", "missing_marker"])
def test_existing_directory_never_reset_or_repaired(rig, kind):
    invoke, directory, now, _, calls, private = rig
    directory.mkdir(mode=0o700)
    if kind != "missing_marker":
        stamp = int(now[0].timestamp())
        data = {
            "scope": "identity-pilot",
            "project": registration.PROJECT,
            "mailbox_hash": private.mailbox_hash(MAIL)[1],
            "created": stamp - 120,
            "expires": stamp - 120 + private.TTL,
            "reserved": 0,
            "last": 0,
            "smtp_ready": True,
        }
        if kind == "expired":
            data.update(created=stamp - private.TTL, expires=stamp)
        if kind == "cap":
            data.update(reserved=6, last=stamp - 60)
        if kind == "corrupt":
            data["smtp_ready"] = False
        private.write_marker(directory, data, initialize=True)
    before = (directory / "authorization.json").read_bytes() if kind != "missing_marker" else None
    result = invoke()
    assert result["status"] != "verified" and not calls
    assert (
        (directory / "authorization.json").read_bytes() if kind != "missing_marker" else None
    ) == before


def test_password_typo_or_attestation_failure_before_reserve(rig):
    invoke, directory, _, _, calls, _ = rig
    assert invoke(["LISTO", MAIL, PASSWORD, "PUBLIC_OTHER_PASSWORD"])["status"] != "verified"
    assert not directory.exists() and not calls
    assert invoke(["NO"])["status"] != "verified"
    assert not directory.exists() and not calls


def test_existing_valid_marker_preserves_original_window_and_count(rig):
    invoke, directory, now, _, _, private = rig
    private.run(
        "initialize",
        directory=directory,
        env_file=Path("unused"),
        prompt=lambda message: MAIL if "Buzón" in message else "LISTO",
        clock=lambda: now[0].timestamp(),
    )
    marker = private.read_marker(directory, int(now[0].timestamp()))
    marker.update(
        reserved=2,
        last=int(now[0].timestamp()) - 60,
        created=marker["created"] - 120,
        expires=marker["expires"] - 120,
    )
    private.write_marker(directory, marker)
    assert invoke(["LISTO", MAIL, PASSWORD, PASSWORD, "123456"])["status"] == "verified"
    after = private.read_marker(directory, int(now[0].timestamp()))
    assert (
        after["reserved"] == 3
        and after["created"] == marker["created"]
        and after["expires"] == marker["expires"]
    )


def test_no_tty_or_value_arguments_reaches_private_config(monkeypatch, capsys):
    monkeypatch.setattr(registration, "helpers", lambda: pytest.fail("private runtime reached"))
    assert registration.main(["--password=PUBLIC_SYNTHETIC_ARGUMENT"]) == 2
    monkeypatch.setattr(registration.sys.stdin, "isatty", lambda: False)
    assert registration.main(["--run"]) == 2
    output = capsys.readouterr()
    assert "PUBLIC_SYNTHETIC" not in output.out + output.err and not output.err


def test_native_and_python_output_suppressed(monkeypatch, capfd):
    import os

    private = registration.helpers()
    monkeypatch.setattr(registration.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(registration.sys.stderr, "isatty", lambda: True)
    monkeypatch.setattr(registration, "helpers", lambda: private)

    def fake_run(**kwargs):
        print("PUBLIC_SYNTHETIC_PYTHON")
        os.write(1, b"PUBLIC_SYNTHETIC_NATIVE")
        os.write(2, b"PUBLIC_SYNTHETIC_NATIVE")
        raise RuntimeError("PUBLIC_SYNTHETIC_ERROR")

    monkeypatch.setattr(registration, "run", fake_run)
    assert registration.main(["--run"]) == 2
    output = capfd.readouterr()
    assert "PUBLIC_SYNTHETIC" not in output.out + output.err and not output.err


def test_otp_format_invalid_never_calls_verify_and_no_resend(rig):
    invoke, _, _, _, calls, _ = rig
    result = invoke(["LISTO", MAIL, PASSWORD, PASSWORD, "LISTO", "PUBLIC_INVALID_OTP"])
    assert result["status"] == "registration_pending"
    assert result["checks"]["request_accepted"] and not result["checks"]["otp_verified"]
    assert sum(path.endswith("/signup") for _, path in calls) == 1
    assert not any(path.endswith("/verify") for _, path in calls)


def test_smtp_attestation_required_before_initialization_or_send(rig):
    invoke, directory, _, _, calls, _ = rig
    result = invoke(["LISTO", MAIL, PASSWORD, PASSWORD, "NO"])
    assert result["status"] != "verified" and not calls
    assert not (directory / "authorization.json").exists()


def test_confirmation_gateway_forbids_other_actions_and_wrong_type():
    from abogalia_api.identity.provider import ProviderFailure

    provider = registration.provider_factory("sb_publishable_PUBLIC_SYNTHETIC")

    def forbidden_transport(request):
        pytest.fail("forbidden operation reached HTTP transport")

    provider.client.close()
    provider.client = httpx.Client(transport=httpx.MockTransport(forbidden_transport))
    with pytest.raises(ProviderFailure):
        provider.verify_code(MAIL, "123456", "recovery")
    with pytest.raises(ProviderFailure):
        provider.login(MAIL, PASSWORD)
    with pytest.raises(ProviderFailure):
        provider.logout("PUBLIC_SYNTHETIC_ACCESS", "global")
    provider.client.close()
