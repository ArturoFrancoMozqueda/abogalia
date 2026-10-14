"""Unit/HTTP contract tests only: in-memory store and mock GoTrue transport."""

import json
import secrets
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from threading import RLock
from uuid import uuid4

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from abogalia_api.identity.config import Settings
from abogalia_api.identity.contracts import StorageUnavailable
from abogalia_api.identity.provider import SupabaseProvider
from abogalia_api.identity.security import digest_reference
from abogalia_api.main import create_app


class MutableClock:
    def __init__(self):
        self.now = datetime.now(UTC).replace(microsecond=0)

    def __call__(self):
        return self.now


class InMemoryStore:
    """Test double, never runtime default and never proof of PostgreSQL isolation."""

    def __init__(self):
        self.rows = {}
        self.lock = RLock()
        self.revoked = {}
        self.unavailable = False

    def create(self, record):
        if self.unavailable:
            raise StorageUnavailable()
        with self.lock:
            if record.created_at <= self.revoked.get(
                record.subject, datetime.min.replace(tzinfo=UTC)
            ):
                raise StorageUnavailable()
            self.rows[record.digest] = deepcopy(record)

    def revoke_subject(self, subject):
        if self.unavailable:
            raise StorageUnavailable()
        with self.lock:
            self.rows = {k: v for k, v in self.rows.items() if v.subject != subject}

    @contextmanager
    def transaction(self, digest):
        if self.unavailable:
            raise StorageUnavailable()
        with self.lock:
            parent = self
            working = deepcopy(self.rows)

            class Transaction:
                record = working.get(digest)

                def save(self, record):
                    working.pop(digest, None)
                    working[record.digest] = deepcopy(record)
                    self.record = deepcopy(record)

                def delete(self):
                    if self.record is not None:
                        working.pop(self.record.digest, None)
                    self.record = None

                def revoke_subject(self, subject):
                    for key in list(working):
                        if working[key].subject == subject:
                            working.pop(key)

            yield Transaction()
            parent.rows = working


class Probe:
    def __init__(self):
        self.sessions = {}
        self.unavailable = False

    def active(self, session_id, subject, *, access_token):
        if self.unavailable:
            raise StorageUnavailable()
        return self.sessions.get(session_id) == subject


class MockGoTrue:
    def __init__(self, clock, probe):
        self.clock = clock
        self.probe = probe
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.jwk = json.loads(jwt.algorithms.ECAlgorithm.to_jwk(self.key.public_key()))
        self.jwk.update(kid="synthetic", alg="ES256", use="sig")
        self.subject = str(uuid4())
        self.session_id = str(uuid4())
        self.factor = str(uuid4())
        self.challenge_id = str(uuid4())
        self.calls = Counter()
        self.mode = "ok"
        self.assurance = "aal1"
        self.refreshes = 0
        self.token_lifetime = 900
        self.probe.sessions[self.session_id] = self.subject

    def issue(self, **overrides):
        now = int(self.clock().timestamp())
        claims = {
            "iss": "http://localhost:9999/auth/v1",
            "aud": "authenticated",
            "sub": self.subject,
            "session_id": self.session_id,
            "iat": now,
            "exp": now + self.token_lifetime,
            "aal": self.assurance,
        }
        claims.update(overrides)
        return jwt.encode(claims, self.key, algorithm="ES256", headers={"kid": "synthetic"})

    def tokens(self):
        return {
            "access_token": self.issue(),
            "refresh_token": secrets.token_urlsafe(32),
            "user": {
                "id": self.subject,
                "email": "person@example.invalid",
                "email_confirmed_at": self.clock().isoformat(),
            },
        }

    def handle(self, request):
        path = request.url.path.removeprefix("/auth/v1")
        self.calls[path] += 1
        if path == "/.well-known/jwks.json":
            return httpx.Response(200, json={"keys": [self.jwk]})
        if self.mode == "down" or (self.mode == "logout_down" and path == "/logout"):
            return httpx.Response(503, json={"private_diagnostic": "synthetic-marker"})
        if self.mode == "limited":
            return httpx.Response(429, json={})
        if path == "/token":
            if self.mode == "invalid":
                return httpx.Response(
                    400, json={"code": "invalid_credentials", "msg": "synthetic-marker"}
                )
            if request.url.params.get("grant_type") == "refresh_token":
                self.refreshes += 1
            return httpx.Response(200, json=self.tokens())
        if path in ("/signup", "/recover"):
            return httpx.Response(200, json={})
        if path == "/verify":
            return httpx.Response(200, json=self.tokens())
        if path == "/logout":
            if request.url.params.get("scope") == "global":
                self.probe.sessions.clear()
            else:
                self.probe.sessions.pop(self.session_id, None)
            return httpx.Response(204)
        if path == "/user":
            return httpx.Response(
                200,
                json={
                    "id": self.subject,
                    "email": "person@example.invalid",
                    "email_confirmed_at": self.clock().isoformat(),
                    "factors": [{"id": self.factor, "factor_type": "totp", "status": "verified"}],
                },
            )
        if path == "/factors":
            return httpx.Response(
                200,
                json={
                    "id": self.factor,
                    "totp": {
                        # Public markers simulate sensitive fields; no real MFA factor.
                        "secret": "synthetic-marker",
                        "uri": "synthetic-marker",
                        "qr_code": "marker",
                    },
                },
            )
        if path.endswith("/challenge"):
            return httpx.Response(
                200,
                json={
                    "id": self.challenge_id,
                    "expires_at": int((self.clock() + timedelta(minutes=5)).timestamp()),
                },
            )
        if path.endswith("/verify"):
            self.assurance = "aal2"
            return httpx.Response(200, json=self.tokens())
        return httpx.Response(404, json={})


@pytest.fixture
def rig():
    clock, store, probe = MutableClock(), InMemoryStore(), Probe()
    settings = Settings(
        project_url="http://localhost:9999",
        publishable_key="sb_publishable_synthetic",
        csrf_key=secrets.token_bytes(32),
        email_enabled=True,
    )
    mock = MockGoTrue(clock, probe)
    provider = SupabaseProvider(settings, httpx.Client(transport=httpx.MockTransport(mock.handle)))
    app = create_app(settings=settings, store=store, probe=probe, provider=provider, clock=clock)
    with TestClient(app) as client:
        yield client, app, store, probe, mock, clock


def bootstrap(client):
    response = client.get("/api/auth/csrf", headers={"Origin": "http://127.0.0.1:5190"})
    assert response.status_code == 200
    return {"Origin": "http://127.0.0.1:5190", "X-CSRF-Token": response.json()["csrf_token"]}


def sign_in(client):
    response = client.post(
        "/api/auth/login",
        headers=bootstrap(client),
        json={
            "email": "person@example.invalid",
            "password": "synthetic-public-marker",
        },
    )
    assert response.status_code == 200
    return response


def test_disabled_defaults_health_and_anonymous():
    with TestClient(create_app()) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/api/auth/session").json() == {"authenticated": False}
        assert (
            client.get(
                "/api/auth/csrf",
                headers={
                    "Origin": "http://127.0.0.1:5190",
                },
            ).status_code
            == 503
        )


def test_login_session_minimal_no_provider_credentials(rig):
    client, _, store, _, mock, _ = rig
    initial_cookie = None
    headers = bootstrap(client)
    initial_cookie = client.cookies.get("abogalia_session")
    response = client.post(
        "/api/auth/login",
        headers=headers,
        json={
            "email": "person@example.invalid",
            "password": "synthetic-public-marker",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"authenticated", "user"}
    assert set(data["user"]) == {"id", "email", "assurance"}
    assert data["user"]["id"] == mock.subject
    assert client.cookies.get("abogalia_session") != initial_cookie
    assert client.get("/api/auth/session").json() == data
    assert len(store.rows) == 1
    assert response.headers["cache-control"] == "no-store"
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=strict" in response.headers["set-cookie"]
    assert "access_token" not in response.text and "refresh_token" not in response.text


def test_register_recover_disabled_and_no_enumeration(rig):
    client, app, _, _, mock, _ = rig
    for path, payload in (
        ("register", {"email": "person@example.invalid", "password": "marker"}),
        ("recover", {"email": "person@example.invalid"}),
    ):
        response = client.post("/api/auth/" + path, headers=bootstrap(client), json=payload)
        assert response.status_code == 202 and response.json() == {"accepted": True}
    app.state.identity.settings = Settings(
        project_url="http://localhost:9999",
        publishable_key="sb_publishable_synthetic",
        csrf_key=app.state.identity.settings.csrf_key,
    )
    response = client.post(
        "/api/auth/recover", headers=bootstrap(client), json={"email": "absent@example.invalid"}
    )
    assert response.status_code == 503
    assert mock.calls["/recover"] == 1


def test_generic_validation_never_echoes_input(rig):
    client, _, _, _, mock, _ = rig
    response = client.post(
        "/api/auth/login",
        headers=bootstrap(client),
        json={
            "email": "synthetic-sensitive-marker",
            "password": "synthetic-sensitive-marker",
            "role": "admin",
        },
    )
    assert response.status_code == 422
    assert "synthetic-sensitive-marker" not in response.text
    assert set(response.json()) == {"error"}
    assert mock.calls["/token"] == 0


def test_bad_credentials_and_downstream_errors_are_sanitized(rig):
    client, _, _, _, mock, _ = rig
    for mode, expected in (("invalid", 401), ("down", 503), ("limited", 429)):
        headers = bootstrap(client)
        mock.mode = mode
        response = client.post(
            "/api/auth/login",
            headers=headers,
            json={
                "email": "person@example.invalid",
                "password": "synthetic-public-marker",
            },
        )
        assert response.status_code == expected
        assert "synthetic-marker" not in response.text
        mock.mode = "ok"


def test_expiry_polling_and_refresh(rig):
    client, _, store, _, mock, clock = rig
    sign_in(client)
    original_activity = next(iter(store.rows.values())).last_activity_at
    clock.now += timedelta(minutes=10)
    assert client.get("/api/auth/session").status_code == 200
    assert next(iter(store.rows.values())).last_activity_at == original_activity
    clock.now += timedelta(minutes=5)
    assert client.get("/api/auth/session").json()["authenticated"] is True
    assert mock.refreshes == 1
    clock.now += timedelta(minutes=15)
    assert client.get("/api/auth/session").json() == {"authenticated": False}
    assert not store.rows


def test_provider_and_storage_revocation_fail_closed(rig):
    client, _, store, probe, _, _ = rig
    sign_in(client)
    probe.unavailable = True
    assert client.get("/api/auth/session").status_code == 503
    probe.unavailable = False
    probe.sessions.clear()
    assert client.get("/api/auth/session").json() == {"authenticated": False}
    assert not store.rows


def test_logout_local_commits_before_provider_failure(rig):
    client, _, store, _, mock, _ = rig
    sign_in(client)
    headers = bootstrap(client)
    reference = client.cookies.get("abogalia_session")
    mock.mode = "logout_down"
    response = client.post("/api/auth/logout", headers=headers, json={"scope": "local"})
    assert response.status_code == 503
    assert digest_reference(reference) not in store.rows
    assert client.cookies.get("abogalia_session") is None


def test_global_logout_removes_all_subject_sessions(rig):
    client, app, store, _, mock, clock = rig
    sign_in(client)
    # Second independently authenticated session, same synthetic subject.
    clock.now += timedelta(seconds=1)
    app.state.identity.login(None, "person@example.invalid", "public-marker")
    assert len(store.rows) == 2
    response = client.post("/api/auth/logout", headers=bootstrap(client), json={"scope": "global"})
    assert response.status_code == 204
    assert not store.rows and not mock.probe.sessions


def test_mfa_closed_routes_and_foreign_factor(rig):
    client, _, _, _, mock, _ = rig
    sign_in(client)
    factors = client.get("/api/auth/mfa/factors")
    assert factors.status_code == 200 and factors.json()["factors"][0]["id"] == mock.factor
    response = client.post(
        "/api/auth/mfa/challenge", headers=bootstrap(client), json={"factor_id": str(uuid4())}
    )
    assert response.status_code == 403
    for operation in ("recover", "unenroll"):
        response = client.post("/api/auth/mfa/" + operation, headers=bootstrap(client), json={})
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FEATURE_UNAVAILABLE"


def test_mfa_verify_rotates_without_extending_absolute_lifetime(rig):
    client, _, store, _, mock, clock = rig
    sign_in(client)
    original_created = next(iter(store.rows.values())).created_at
    previous_cookie = client.cookies.get("abogalia_session")
    clock.now += timedelta(minutes=1)
    challenge = client.post(
        "/api/auth/mfa/challenge", headers=bootstrap(client), json={"factor_id": mock.factor}
    )
    assert challenge.status_code == 200
    response = client.post(
        "/api/auth/mfa/verify",
        headers=bootstrap(client),
        json={
            "factor_id": mock.factor,
            "challenge_id": challenge.json()["challenge_id"],
            "code": "000000",
        },
    )
    assert response.status_code == 200 and response.json()["user"]["assurance"] == "aal2"
    assert client.cookies.get("abogalia_session") != previous_cookie
    assert len(store.rows) == 1
    assert next(iter(store.rows.values())).created_at == original_created


def test_recovery_revokes_locals_and_never_authenticates(rig):
    client, app, store, _, _, _ = rig
    app.state.identity.login(None, "person@example.invalid", "marker")
    response = client.post(
        "/api/auth/recover/complete",
        headers=bootstrap(client),
        json={
            "email": "person@example.invalid",
            "code": "000000",
            "new_password": "marker-new",
        },
    )
    assert response.status_code == 204
    assert not store.rows
    assert client.get("/api/auth/session").json() == {"authenticated": False}


def test_cookie_secure_production_flags(rig):
    _, app, _, _, _, _ = rig
    settings = Settings(
        origin="https://abogalia.example.invalid",
        development_http=False,
        project_url="https://spohytnxscljtitvmdab.supabase.co",
        publishable_key="sb_publishable_synthetic",
        csrf_key=secrets.token_bytes(32),
    )
    service = app.state.identity
    with TestClient(create_app(settings=settings, provider=service.provider)) as client:
        response = client.get("/api/auth/csrf", headers={"Origin": settings.origin})
        assert response.status_code == 200
        flags = response.headers["set-cookie"]
        assert "__Host-abogalia_session" in flags
        assert "Secure" in flags and "HttpOnly" in flags and "Domain" not in flags


def test_absolute_expiry_even_after_recent_activity(rig):
    client, _, store, _, _, clock = rig
    sign_in(client)
    clock.now += timedelta(hours=12)
    for row in store.rows.values():
        row.last_activity_at = clock.now - timedelta(seconds=1)
    assert client.get("/api/auth/session").json() == {"authenticated": False}
    assert not store.rows


def test_mfa_cross_session_and_replay_reject_before_provider(rig):
    client, app, _, probe, mock, _ = rig
    sign_in(client)
    response = client.post(
        "/api/auth/mfa/challenge", headers=bootstrap(client), json={"factor_id": mock.factor}
    )
    assert response.status_code == 200
    body = {
        "factor_id": mock.factor,
        "challenge_id": response.json()["challenge_id"],
        "code": "000000",
    }
    mock.session_id = str(uuid4())
    probe.sessions[mock.session_id] = mock.subject
    sign_in(client)
    response = client.post("/api/auth/mfa/verify", headers=bootstrap(client), json=body)
    assert response.status_code == 403
    assert mock.calls[f"/factors/{mock.factor}/verify"] == 0
    response = client.post(
        "/api/auth/mfa/challenge", headers=bootstrap(client), json={"factor_id": mock.factor}
    )
    body["challenge_id"] = response.json()["challenge_id"]
    assert (
        client.post("/api/auth/mfa/verify", headers=bootstrap(client), json=body).status_code == 200
    )
    assert (
        client.post("/api/auth/mfa/verify", headers=bootstrap(client), json=body).status_code == 403
    )
    assert mock.calls[f"/factors/{mock.factor}/verify"] == 1


def test_storage_error_does_not_become_anonymous_success(rig):
    client, _, store, _, _, _ = rig
    sign_in(client)
    store.unavailable = True
    response = client.get("/api/auth/session")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "AUTH_UNAVAILABLE"


def test_csrf_and_session_polling_do_not_extend_idle_timeout(rig):
    client, _, store, _, _, clock = rig
    sign_in(client)
    initial = next(iter(store.rows.values())).last_activity_at
    for _ in range(3):
        clock.now += timedelta(minutes=5)
        bootstrap(client)
        assert client.get("/api/auth/session").json()["authenticated"] is True
        assert next(iter(store.rows.values())).last_activity_at == initial
    clock.now += timedelta(minutes=15)
    assert client.get("/api/auth/session").json() == {"authenticated": False}


def test_credential_runtime_objects_do_not_dump_values(rig):
    _, app, store, _, _, _ = rig
    app.state.identity.login(None, "person@example.invalid", "public-marker")
    record = next(iter(store.rows.values()))
    assert record.access_token not in repr(record)
    assert record.refresh_token not in repr(record)
    assert app.state.identity.settings.csrf_key.hex() not in repr(app.state.identity.settings)


def test_refresh_serialized_against_simultaneous_polling(rig):
    from concurrent.futures import ThreadPoolExecutor

    client, app, _, _, mock, clock = rig
    sign_in(client)
    reference = client.cookies.get("abogalia_session")
    clock.now += timedelta(minutes=15)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: app.state.identity.session(reference), range(2)))
    assert all(view["authenticated"] for view in results)
    assert mock.refreshes == 1


def test_pre_auth_expiry_rejects_replay(rig):
    client, _, _, _, mock, clock = rig
    headers = bootstrap(client)
    clock.now += timedelta(minutes=30)
    response = client.post(
        "/api/auth/login",
        headers=headers,
        json={
            "email": "person@example.invalid",
            "password": "public-marker",
        },
    )
    assert response.status_code == 403 and mock.calls["/token"] == 0


def test_provider_request_scopes_payloads_and_key(rig):
    _, app, _, _, _, _ = rig
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(204)

    provider = SupabaseProvider(
        app.state.identity.settings, httpx.Client(transport=httpx.MockTransport(handle))
    )
    provider.logout("synthetic-public-marker", "local")
    provider.logout("synthetic-public-marker", "global")
    assert [req.url.params["scope"] for req in seen] == ["local", "global"]
    assert all(
        req.headers.get("apikey") == app.state.identity.settings.publishable_key for req in seen
    )
    assert all(req.method == "POST" and req.url.path == "/auth/v1/logout" for req in seen)


def test_csrf_cookie_lifetime_never_extends_reference(rig):
    client, _, _, _, _, clock = rig
    bootstrap(client)
    clock.now += timedelta(minutes=10)
    response = client.get("/api/auth/csrf", headers={"Origin": "http://127.0.0.1:5190"})
    assert "Max-Age=1200" in response.headers["set-cookie"]


@pytest.mark.parametrize(
    "path,code,status",
    [
        ("register", "weak_password", 422),
        ("register", "email_exists", 202),
        ("register", "user_already_exists", 202),
        ("recover", "user_not_found", 202),
        ("recover", "email_address_not_authorized", 503),
        ("register", "email_address_not_authorized", 503),
        ("recover", "email_provider_disabled", 503),
        ("recover", "smtp_failure", 503),
        ("register", "unrecognized_failure", 503),
        ("recover", "invalid_credentials", 503),
    ],
)
def test_provider_email_error_allowlist_is_honest_and_sanitized(rig, path, code, status):
    client, app, _, _, mock, _ = rig
    original = mock.handle

    def handle(request):
        if request.url.path.endswith("/signup") or request.url.path.endswith("/recover"):
            return httpx.Response(422, json={"code": code, "msg": "synthetic-sensitive-marker"})
        return original(request)

    app.state.identity.provider.client = httpx.Client(transport=httpx.MockTransport(handle))
    body = {"email": "person@example.invalid"}
    if path == "register":
        body["password"] = "synthetic-public-marker"
    response = client.post("/api/auth/" + path, headers=bootstrap(client), json=body)
    assert response.status_code == status
    assert "synthetic-sensitive-marker" not in response.text
    if status == 202:
        assert response.json() == {"accepted": True}
    elif status == 422:
        assert response.json()["error"]["code"] == "INVALID_REQUEST"
    else:
        assert response.json()["error"]["code"] == "AUTH_UNAVAILABLE"


def test_definitive_refresh_rejection_commits_custody_deletion_before_401(rig):
    client, app, store, _, mock, clock = rig
    sign_in(client)
    reference = client.cookies.get("abogalia_session")
    original = mock.handle

    def handle(request):
        if request.url.params.get("grant_type") == "refresh_token":
            return httpx.Response(
                400, json={"code": "refresh_token_not_found", "msg": "synthetic-sensitive-marker"}
            )
        return original(request)

    app.state.identity.provider.client = httpx.Client(transport=httpx.MockTransport(handle))
    clock.now += timedelta(minutes=15)
    # Auth-required route gets 401; /session would normalize this to anonymous200.
    response = client.get("/api/auth/mfa/factors")
    assert response.status_code == 401
    assert digest_reference(reference) not in store.rows
    assert client.cookies.get("abogalia_session") is None
    assert "synthetic-sensitive-marker" not in response.text


def test_refresh_infrastructure_failure_preserves_row_but_never_grants_access(rig):
    client, _, store, _, mock, clock = rig
    sign_in(client)
    reference = client.cookies.get("abogalia_session")
    activity = next(iter(store.rows.values())).last_activity_at
    mock.mode = "down"
    clock.now += timedelta(minutes=15)
    response = client.get("/api/auth/mfa/factors")
    assert response.status_code == 503
    assert digest_reference(reference) in store.rows
    assert next(iter(store.rows.values())).last_activity_at == activity


@pytest.mark.parametrize("operation", ["enroll", "challenge"])
@pytest.mark.parametrize("change", ["revoked", "absolute_expired"])
def test_mfa_frontier_revocation_or_expiry_never_returns_secret(rig, operation, change):
    client, app, store, probe, mock, clock = rig
    sign_in(client)
    original = mock.handle

    def handle(request):
        response = original(request)
        if request.url.path.endswith("/factors") or request.url.path.endswith("/challenge"):
            if change == "revoked":
                probe.sessions.clear()
            else:
                clock.now += timedelta(hours=12)
        return response

    app.state.identity.provider.client = httpx.Client(transport=httpx.MockTransport(handle))
    payload = {} if operation == "enroll" else {"factor_id": mock.factor}
    response = client.post("/api/auth/mfa/" + operation, headers=bootstrap(client), json=payload)
    assert response.status_code == 401
    assert "synthetic-marker" not in response.text
    assert "totp" not in response.json()
    assert not store.rows
    assert client.cookies.get("abogalia_session") is None


def test_openapi_documents_minimal_union_and_uniform_errors():
    schema = create_app().openapi()
    for route in ("session", "login", "mfa/verify"):
        method = "get" if route == "session" else "post"
        responses = schema["paths"]["/api/auth/" + route][method]["responses"]
        success = responses["200"]["content"]["application/json"]["schema"]
        assert len(success["anyOf"]) == 2
        for status in ("403", "422", "429", "503"):
            assert responses[status]["content"]["application/json"]["schema"]["$ref"].endswith(
                "ErrorView"
            )
    assert "200" not in schema["paths"]["/api/auth/mfa/recover"]["post"]["responses"]
    for path in ("logout", "confirm", "recover/complete"):
        assert "content" not in schema["paths"]["/api/auth/" + path]["post"]["responses"]["204"]


def test_expired_csrf_bootstrap_commits_old_custody_cleanup(rig):
    client, _, store, _, _, clock = rig
    sign_in(client)
    clock.now += timedelta(minutes=30)
    bootstrap(client)
    assert not store.rows
    assert client.get("/api/auth/session").json() == {"authenticated": False}


def test_mfa_verify_frontier_revoke_after_rotation_deletes_current_digest(rig):
    client, _, store, probe, mock, _ = rig
    sign_in(client)
    challenge = client.post(
        "/api/auth/mfa/challenge", headers=bootstrap(client), json={"factor_id": mock.factor}
    )
    assert challenge.status_code == 200
    original = probe.active
    calls = 0

    def active(session_id, subject, *, access_token):
        nonlocal calls
        calls += 1
        if calls == 3:
            # Initial load and elevated JWT/probe succeed, then revoke at the
            # post-provider frontier AFTER tx.save changed the session digest.
            probe.sessions.clear()
        return original(session_id, subject, access_token=access_token)

    probe.active = active
    response = client.post(
        "/api/auth/mfa/verify",
        headers=bootstrap(client),
        json={
            "factor_id": mock.factor,
            "challenge_id": challenge.json()["challenge_id"],
            "code": "000000",
        },
    )
    assert response.status_code == 401
    assert calls == 3
    assert not store.rows
    assert client.cookies.get("abogalia_session") is None
    assert "access_token" not in response.text and "refresh_token" not in response.text


def test_auth_revoked_cookie_cannot_globally_delete_newer_session(rig):
    client, app, store, probe, mock, clock = rig
    sign_in(client)
    session_a = mock.session_id
    reference_a = client.cookies.get("abogalia_session")
    headers = bootstrap(client)
    clock.now += timedelta(seconds=1)
    mock.session_id = str(uuid4())
    probe.sessions[mock.session_id] = mock.subject
    reference_b, _ = app.state.identity.login(None, "person@example.invalid", "public-marker")
    probe.sessions.pop(session_a)
    response = client.post("/api/auth/logout", headers=headers, json={"scope": "global"})
    assert response.status_code == 401
    assert digest_reference(reference_a) not in store.rows
    assert digest_reference(reference_b) in store.rows
    assert mock.calls["/logout"] == 0
    assert app.state.identity.session(reference_b)["authenticated"] is True


def test_valid_global_logout_commit_survives_external_signout_failure(rig):
    client, app, store, probe, mock, clock = rig
    sign_in(client)
    clock.now += timedelta(seconds=1)
    mock.session_id = str(uuid4())
    probe.sessions[mock.session_id] = mock.subject
    app.state.identity.login(None, "person@example.invalid", "public-marker")
    assert len(store.rows) == 2
    mock.mode = "logout_down"
    response = client.post("/api/auth/logout", headers=bootstrap(client), json={"scope": "global"})
    assert response.status_code == 503
    assert not store.rows
    assert client.cookies.get("abogalia_session") is None
    assert mock.calls["/logout"] == 1


def test_global_logout_frontier_revocation_preserves_other_session(rig):
    client, app, store, probe, mock, clock = rig
    sign_in(client)
    session_a = mock.session_id
    reference_a = client.cookies.get("abogalia_session")
    headers = bootstrap(client)
    clock.now += timedelta(seconds=1)
    mock.session_id = str(uuid4())
    probe.sessions[mock.session_id] = mock.subject
    reference_b, _ = app.state.identity.login(None, "person@example.invalid", "public-marker")
    original = probe.active
    calls = 0

    def active(session_id, subject, *, access_token):
        nonlocal calls
        calls += 1
        if calls == 2:
            probe.sessions.pop(session_a)
        return original(session_id, subject, access_token=access_token)

    probe.active = active
    response = client.post("/api/auth/logout", headers=headers, json={"scope": "global"})
    assert response.status_code == 401
    assert calls == 2
    assert digest_reference(reference_a) not in store.rows
    assert digest_reference(reference_b) in store.rows
    assert mock.calls["/logout"] == 0


@pytest.mark.parametrize("action", ["foreign_factor", "incorrect_otp"])
def test_failed_action_commits_rotated_refresh_without_touching_activity(rig, action):
    client, app, store, _, mock, clock = rig
    sign_in(client)
    challenge_id = None
    if action == "incorrect_otp":
        clock.now += timedelta(minutes=14, seconds=29)
        challenge = client.post(
            "/api/auth/mfa/challenge", headers=bootstrap(client), json={"factor_id": mock.factor}
        )
        assert challenge.status_code == 200
        assert mock.refreshes == 0
        challenge_id = challenge.json()["challenge_id"]
        clock.now += timedelta(seconds=16)
    else:
        clock.now += timedelta(minutes=14, seconds=45)
    before = deepcopy(next(iter(store.rows.values())))
    if action == "foreign_factor":
        response = client.post(
            "/api/auth/mfa/challenge", headers=bootstrap(client), json={"factor_id": str(uuid4())}
        )
        assert response.status_code == 403
    else:
        original = mock.handle

        def handle(request):
            if request.url.path.endswith(f"/factors/{mock.factor}/verify"):
                return httpx.Response(
                    400,
                    json={"code": "mfa_verification_failed", "msg": "synthetic-sensitive-marker"},
                )
            return original(request)

        app.state.identity.provider.client = httpx.Client(transport=httpx.MockTransport(handle))
        response = client.post(
            "/api/auth/mfa/verify",
            headers=bootstrap(client),
            json={
                "factor_id": mock.factor,
                "challenge_id": challenge_id,
                "code": "000000",
            },
        )
        assert response.status_code == 401
    current = next(iter(store.rows.values()))
    assert mock.refreshes == 1
    assert bool(current.access_token != before.access_token)
    assert bool(current.refresh_token != before.refresh_token)
    assert current.last_activity_at == before.last_activity_at
    assert client.get("/api/auth/session").json()["authenticated"] is True
    assert mock.refreshes == 1
    assert "synthetic-sensitive-marker" not in response.text
