"""Synthetic signatures and HTTP transport only; no real account or email operations."""

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

SPEC = importlib.util.spec_from_file_location(
    "auth_acceptance", Path(__file__).parents[3] / "scripts/verify_identity_auth_sessions.py"
)
harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness)
MAIL = "synthetic-acceptance@example.invalid"
PASSWORD = "PUBLIC_SYNTHETIC_PASSWORD_ONLY"


@pytest.fixture
def rig():
    from abogalia_api.identity.provider import SupabaseProvider

    key = ec.generate_private_key(ec.SECP256R1())
    public = json.loads(jwt.algorithms.ECAlgorithm.to_jwk(key.public_key()))
    public.update(kid="synthetic", alg="ES256", use="sig")
    subject = str(uuid4())
    now = [datetime.now(UTC)]
    live, calls, pairs = set(), [], []
    state = {"mode": "normal", "closed": False}

    def transport(request):
        calls.append((request.method, request.url.path, request.url.params.get("scope")))
        assert request.url.host == "spohytnxscljtitvmdab.supabase.co"
        assert request.url.scheme == "https"
        path = request.url.path
        if path.endswith("/.well-known/jwks.json"):
            return httpx.Response(200, json={"keys": [public]})
        if path.endswith("/token"):
            if state["mode"] == "login_fail":
                raise httpx.ReadTimeout("PUBLIC_SYNTHETIC_DIAGNOSTIC")
            assert dict(request.url.params) == {"grant_type": "password"}
            assert json.loads(request.content) == {"email": MAIL, "password": PASSWORD}
            sid = str(uuid4())
            live.add(sid)
            stamp = int(now[0].timestamp())
            raw = jwt.encode(
                {
                    "iss": harness.PROJECT + "/auth/v1",
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
            pairs.append(raw)
            return httpx.Response(
                200,
                json={
                    "access_token": raw,
                    "refresh_token": "PUBLIC_SYNTHETIC_REFRESH",
                    "user": {"id": subject, "email": MAIL, "email_confirmed_at": "synthetic"},
                },
            )
        raw = request.headers["authorization"].removeprefix("Bearer ")
        claims = jwt.decode(raw, key.public_key(), algorithms=["ES256"], audience="authenticated")
        sid = claims["session_id"]
        if path.endswith("/user"):
            if state["mode"] == "unavailable":
                return httpx.Response(503)
            if sid not in live:
                if state["mode"] == "generic_forbidden":
                    return httpx.Response(403, json={"code": "generic"})
                return httpx.Response(403, json={"code": "session_not_found"})
            return httpx.Response(200, json={"id": subject})
        assert path.endswith("/logout")
        if state["mode"] == "logout_timeout":
            raise httpx.ReadTimeout("PUBLIC_SYNTHETIC_DIAGNOSTIC")
        if state["mode"] == "expiry":
            from datetime import timedelta

            now[0] += timedelta(seconds=901)
        if state["mode"] != "ignores_logout":
            if request.url.params["scope"] == "global":
                if state["mode"] == "global_is_local":
                    live.discard(sid)
                else:
                    live.clear()
            else:
                live.discard(sid)
        return httpx.Response(204)

    provider = harness.provider_factory("sb_publishable_PUBLIC_SYNTHETIC")
    provider.client.close()
    provider.client = httpx.Client(transport=httpx.MockTransport(transport))
    assert isinstance(provider, SupabaseProvider)

    def invoke(answers=None):
        inputs = iter(answers or ["LISTO", MAIL, PASSWORD])
        return harness.run(
            prompt=lambda _: next(inputs),
            key_loader=lambda: "sb_publishable_PUBLIC_SYNTHETIC",
            factory=lambda _: provider,
            clock=lambda: now[0],
        )

    return invoke, state, calls, live, provider, pairs


def test_full_original_token_revocation_and_scope_isolation(rig):
    invoke, _, calls, live, provider, pairs = rig
    result = invoke()
    assert result == {
        "status": "verified",
        "checks": dict.fromkeys(harness.CHECKS, True),
        "cleanup": True,
    }
    assert len(pairs) == 3 and not live and provider.client.is_closed
    assert [scope for _, path, scope in calls if path.endswith("/logout")] == ["local", "global"]
    assert sum(path.endswith("/token") for _, path, _ in calls) == 3
    assert set(result["checks"]) == set(harness.CHECKS)
    assert all(type(value) is bool for value in result["checks"].values())
    assert MAIL not in json.dumps(result) and PASSWORD not in json.dumps(result)


@pytest.mark.parametrize("mode", ["ignores_logout", "generic_forbidden", "unavailable", "expiry"])
def test_no_false_acceptance_and_finally_closes_owned_sessions(rig, mode):
    invoke, state, _, _, provider, _ = rig
    state["mode"] = mode
    result = invoke()
    assert result["status"] != "verified"
    assert not all(result["checks"].values())
    assert provider.client.is_closed


def test_login_timeout_not_retried_or_echoed(rig):
    invoke, state, calls, _, provider, _ = rig
    state["mode"] = "login_fail"
    result = invoke()
    assert result["status"] == "cleanup_failed"
    assert len(calls) == 1 and provider.client.is_closed
    assert "DIAGNOSTIC" not in json.dumps(result)


def test_logout_timeout_no_retry_same_session(rig):
    invoke, state, calls, _, _, _ = rig
    state["mode"] = "logout_timeout"
    result = invoke()
    assert result["status"] != "verified"
    # A scenario attempt, then B cleanup; A is never retried.
    assert sum(path.endswith("/logout") for _, path, _ in calls) == 2


@pytest.mark.parametrize("answers", [["NO"], ["LISTO", MAIL, "short"]])
def test_private_attestation_and_password_validation_before_network(rig, answers):
    invoke, _, calls, _, _, _ = rig
    assert invoke(answers)["status"] == "verification_pending"
    assert not calls


def test_cli_refuses_arguments_and_non_tty_without_loading_private_file(monkeypatch, capsys):
    monkeypatch.setattr(harness, "helpers", lambda: pytest.fail("private file path reached"))
    assert harness.main(["--password=PUBLIC_SYNTHETIC_ARGUMENT"]) == 2
    monkeypatch.setattr(harness.sys.stdin, "isatty", lambda: False)
    assert harness.main(["--run"]) == 2
    output = capsys.readouterr()
    assert "PUBLIC_SYNTHETIC_ARGUMENT" not in output.out + output.err
    assert not output.err


def test_gateway_cannot_send_mail_or_refresh(rig):
    from abogalia_api.identity.provider import ProviderFailure

    _, _, calls, _, provider, _ = rig
    with pytest.raises(ProviderFailure):
        provider.register(MAIL, PASSWORD)
    with pytest.raises(ProviderFailure):
        provider.recover(MAIL)
    with pytest.raises(ProviderFailure):
        provider.refresh("PUBLIC_SYNTHETIC_REFRESH")
    provider.client.close()
    assert not calls


def test_cli_suppresses_native_python_and_logging_output(monkeypatch, capfd):
    import os

    private = harness.helpers()
    monkeypatch.setattr(harness.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(harness.sys.stderr, "isatty", lambda: True)
    monkeypatch.setattr(harness, "helpers", lambda: private)

    def fake_run(**kwargs):
        print("PUBLIC_SYNTHETIC_PYTHON_DIAGNOSTIC")
        os.write(1, b"PUBLIC_SYNTHETIC_NATIVE_DIAGNOSTIC")
        os.write(2, b"PUBLIC_SYNTHETIC_NATIVE_DIAGNOSTIC")
        raise RuntimeError("PUBLIC_SYNTHETIC_EXCEPTION")

    monkeypatch.setattr(harness, "run", fake_run)
    assert harness.main(["--run"]) == 2
    output = capfd.readouterr()
    assert "PUBLIC_SYNTHETIC" not in output.out + output.err
    assert json.loads(output.out)["status"] == "verification_unavailable"
    assert output.err == ""


def test_logout_ambiguous_failure_is_reported_as_cleanup_failed(rig):
    invoke, state, _, _, _, _ = rig
    state["mode"] = "logout_timeout"
    assert invoke()["status"] == "cleanup_failed"


def test_close_failure_is_redacted(rig, monkeypatch):
    invoke, _, _, _, provider, _ = rig

    def fail_close():
        raise RuntimeError("PUBLIC_SYNTHETIC_CLOSE_ERROR")

    monkeypatch.setattr(provider.client, "close", fail_close)
    result = invoke()
    assert result["status"] == "cleanup_failed" and result["cleanup"] is False
    assert "PUBLIC_SYNTHETIC" not in json.dumps(result)


@pytest.mark.parametrize("mode", ["ignores_logout", "generic_forbidden", "unavailable", "expiry"])
def test_cleanup_requires_observed_absence_with_valid_original_token(rig, mode):
    invoke, state, _, _, _, _ = rig
    state["mode"] = mode
    result = invoke()
    assert result["cleanup"] is False and result["status"] == "cleanup_failed"


def test_global_local_only_scope_cannot_pass_or_claim_cleanup(rig):
    invoke, state, _, live, _, _ = rig
    state["mode"] = "global_is_local"
    result = invoke()
    assert result["status"] != "verified"
    assert result["checks"]["global_revoked_both"] is False
    # C was not attempted by global B; finally may close C once locally.
    assert not live
