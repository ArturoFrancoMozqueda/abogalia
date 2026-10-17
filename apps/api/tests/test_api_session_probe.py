"""Synthetic signed JWTs and isolated HTTP transport; no real provider acceptance."""

from datetime import timedelta
from uuid import uuid4

import httpx
import jwt
import pytest
from test_auth import MockGoTrue, MutableClock, Probe

from abogalia_api.identity.config import Settings
from abogalia_api.identity.contracts import StorageUnavailable
from abogalia_api.identity.provider import SupabaseProvider
from abogalia_api.identity.session_probe import ApiSessionProbe

PROJECT = "https://spohytnxscljtitvmdab.supabase.co"


class MockAPIAuth(MockGoTrue):
    def issue(self, **overrides):
        return super().issue(**({"iss": PROJECT + "/auth/v1"} | overrides))

    def handle(self, request):
        if request.url.path == "/auth/v1/user":
            self.calls["/user"] += 1
            if self.mode == "probe_unavailable":
                return httpx.Response(503, json={})
            if self.mode == "probe_forbidden":
                return httpx.Response(403, json={"code": "unrecognized"})
            try:
                raw = request.headers["authorization"].removeprefix("Bearer ")
                claims = jwt.decode(
                    raw,
                    self.key.public_key(),
                    algorithms=["ES256"],
                    audience="authenticated",
                    issuer=PROJECT + "/auth/v1",
                    options={"verify_exp": False, "verify_iat": False},
                )
                if self.probe.sessions.get(claims["session_id"]) != claims["sub"]:
                    return httpx.Response(401, json={"code": "session_not_found"})
                return httpx.Response(
                    200,
                    json={
                        "id": claims["sub"],
                        "email": "person@example.invalid",
                        "email_confirmed_at": self.clock().isoformat(),
                        "factors": [
                            {"id": self.factor, "factor_type": "totp", "status": "verified"}
                        ],
                    },
                )
            except Exception:
                return httpx.Response(401, json={"code": "bad_jwt"})
        return super().handle(request)


@pytest.fixture
def api_probe():
    clock = MutableClock()
    mock = MockAPIAuth(clock, Probe())
    settings = Settings(
        project_url=PROJECT,
        publishable_key="sb_publishable_synthetic",
        csrf_key=b"PUBLIC_SYNTHETIC_MARKER" * 2,
        email_enabled=True,
    )
    client = httpx.Client(transport=httpx.MockTransport(mock.handle))
    provider = SupabaseProvider(settings, client)
    probe = ApiSessionProbe(settings, provider, clock)
    yield probe, mock, client, clock
    client.close()


def test_verified_session_no_positive_cache(api_probe):
    probe, mock, _, _ = api_probe
    token = mock.issue()
    assert probe.active(mock.session_id, mock.subject, access_token=token) is True
    assert probe.active(mock.session_id, mock.subject, access_token=token) is True
    assert mock.calls["/user"] == 2
    mock.probe.sessions.clear()
    assert probe.active(mock.session_id, mock.subject, access_token=token) is False
    assert mock.calls["/user"] == 3


@pytest.mark.parametrize(
    "change", ["sid", "subject", "missing_sid", "nil_sid", "expired", "signature", "unsigned"]
)
def test_unverified_or_unbound_token_never_calls_user(api_probe, change):
    probe, mock, _, clock = api_probe
    token = mock.issue()
    sid, subject = mock.session_id, mock.subject
    if change == "sid":
        sid = str(uuid4())
    elif change == "subject":
        subject = str(uuid4())
    elif change == "missing_sid":
        token = mock.issue(session_id=None)
    elif change == "nil_sid":
        token = mock.issue(session_id="00000000-0000-0000-0000-000000000000")
    elif change == "expired":
        clock.now += timedelta(minutes=16)
    elif change == "signature":
        token = token[:-8] + "INVALID_"
    else:
        token = jwt.encode({"sub": subject}, "", algorithm="none")
    with pytest.raises(StorageUnavailable):
        probe.active(sid, subject, access_token=token)
    assert mock.calls["/user"] == 0


@pytest.mark.parametrize(
    "status,body,definitive",
    [
        (401, {"code": "session_not_found"}, True),
        (401, {"error_code": "user_not_found"}, True),
        (403, {"code": "session_not_found"}, True),
        (403, {"code": "user_not_found"}, True),
        (403, {"code": "unrecognized"}, False),
        (401, {"code": "bad_jwt"}, False),
        (401, {"code": "unrecognized"}, False),
        (429, {}, False),
        (503, {}, False),
        (302, {}, False),
        (200, [], False),
        (200, {"id": "invalid"}, False),
        (200, {"id": str(uuid4())}, False),
    ],
)
def test_provider_result_allowlist(api_probe, status, body, definitive):
    probe, mock, client, _ = api_probe
    original = mock.handle
    client._transport = httpx.MockTransport(
        lambda request: (
            httpx.Response(status, json=body)
            if request.url.path.endswith("/user")
            else original(request)
        )
    )
    if definitive:
        assert probe.active(mock.session_id, mock.subject, access_token=mock.issue()) is False
    else:
        with pytest.raises(StorageUnavailable) as error:
            probe.active(mock.session_id, mock.subject, access_token=mock.issue())
        assert str(error.value) == ""


@pytest.mark.parametrize("failure", ["timeout", "malformed", "large", "redirect"])
def test_transport_bound_failures_redacted(api_probe, failure, caplog):
    probe, mock, client, _ = api_probe
    original = mock.handle
    calls = []

    def transport(request):
        if not request.url.path.endswith("/user"):
            return original(request)
        calls.append(True)
        if failure == "timeout":
            raise httpx.ReadTimeout("PUBLIC_SYNTHETIC_DIAGNOSTIC")
        if failure == "malformed":
            return httpx.Response(200, content=b"PUBLIC_SYNTHETIC_INVALID_JSON")
        if failure == "redirect":
            return httpx.Response(302, headers={"Location": "https://unapproved.invalid"})
        return httpx.Response(200, content=b"x" * 65537)

    client._transport = httpx.MockTransport(transport)
    with pytest.raises(StorageUnavailable):
        probe.active(mock.session_id, mock.subject, access_token=mock.issue())
    assert calls == [True]
    assert "PUBLIC_SYNTHETIC_DIAGNOSTIC" not in caplog.text


def test_request_isolated_from_client_state(api_probe):
    probe, mock, client, _ = api_probe
    seen = []
    original = mock.handle
    client.headers["X-Synthetic-State"] = "PUBLIC_SYNTHETIC"
    client.cookies.set("synthetic", "PUBLIC_SYNTHETIC")

    def transport(request):
        if request.url.path.endswith("/user"):
            seen.append(request)
        return original(request)

    client._transport = httpx.MockTransport(transport)
    assert probe.active(mock.session_id, mock.subject, access_token=mock.issue())
    assert len(seen) == 1
    request = seen[0]
    assert str(request.url) == PROJECT + "/auth/v1/user"
    assert "cookie" not in request.headers and "X-Synthetic-State" not in request.headers
    assert request.content == b"" and request.url.query == b""
    assert "authorization" in request.headers and "apikey" in request.headers


def test_api_probe_forbids_local_destination():
    with pytest.raises(StorageUnavailable):
        ApiSessionProbe(Settings(project_url="http://localhost:9999"))


def test_null_sid_cannot_authorize_even_when_expected_matches(api_probe):
    probe, mock, _, _ = api_probe
    nil = "00000000-0000-0000-0000-000000000000"
    with pytest.raises(StorageUnavailable):
        probe.active(nil, mock.subject, access_token=mock.issue(session_id=nil))
    assert mock.calls["/user"] == 0
