"""HTTP Identity with real isolated PostgreSQL custody/probe and synthetic GoTrue.

Run through scripts/run_identity_tests.py: no provider, production DSN, password,
real identity, or InMemoryStore participates in these acceptance cases. Assertions
are boolean to keep pytest diagnostics from rendering ephemeral credentials.
"""

import os
import secrets
from dataclasses import dataclass
from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import httpx
import psycopg
import pytest
from fastapi.testclient import TestClient
from test_auth import MockGoTrue, bootstrap, sign_in

from abogalia_api.identity.config import Settings
from abogalia_api.identity.provider import SupabaseProvider
from abogalia_api.identity.security import digest_reference
from abogalia_api.identity.storage import PostgresSessionProbe, PostgresSessionStore
from abogalia_api.main import create_app

pytest_plugins = ["storage_fixtures"]


class SQLAuthSessions:
    """Mock gateway session changes are stored in synthetic auth.sessions SQL.

    Production PostgresSessionProbe reads this table under its restricted role;
    the mapping is only a bridge for MockGoTrue, never a mock revocation probe.
    """

    def __init__(self, database):
        self.database = database
        self.subjects = set()

    def connect(self):
        return psycopg.connect(
            self.database.admin_dsn, autocommit=True, passfile=os.devnull, password=""
        )

    def __setitem__(self, session_id, subject):
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO auth.sessions(id, user_id) VALUES (%s, %s) "
                "ON CONFLICT (id) DO UPDATE SET user_id = EXCLUDED.user_id",
                (session_id, subject),
            )
        self.subjects.add(subject)

    def get(self, session_id, default=None):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT user_id FROM auth.sessions WHERE id = %s", (session_id,)
            ).fetchone()
        return str(row[0]) if row else default

    def pop(self, session_id, default=None):
        with self.connect() as conn:
            row = conn.execute(
                "DELETE FROM auth.sessions WHERE id = %s RETURNING user_id", (session_id,)
            ).fetchone()
        return str(row[0]) if row else default

    def clear(self):
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM auth.sessions WHERE user_id = ANY(%s::uuid[])",
                (sorted(self.subjects),),
            )


@dataclass(repr=False)
class SQLRig:
    client: TestClient
    app: object
    store: PostgresSessionStore
    probe: PostgresSessionProbe
    mock: MockGoTrue
    clock: object
    database: object
    provider_sessions: SQLAuthSessions

    def connect(self):
        return psycopg.connect(
            self.database.admin_dsn, autocommit=True, passfile=os.devnull, password=""
        )

    def count_sessions(self):
        with self.connect() as conn:
            return conn.execute("SELECT count(*) FROM identity.app_sessions").fetchone()[0]

    def record(self, reference):
        with self.store.transaction(digest_reference(reference)) as tx:
            return tx.record


@pytest.fixture
def sql_rig(isolated_database, clock):
    sessions = SQLAuthSessions(isolated_database)
    mock = MockGoTrue(clock, SimpleNamespace(sessions=sessions))
    settings = Settings(
        project_url="http://localhost:9999",
        publishable_key="sb_publishable_synthetic",
        csrf_key=secrets.token_bytes(32),
        email_enabled=True,
    )
    transport = httpx.Client(transport=httpx.MockTransport(mock.handle))
    provider = SupabaseProvider(settings, transport)
    store = PostgresSessionStore(isolated_database.runtime_dsn, isolated_database.key, clock)
    probe = PostgresSessionProbe(isolated_database.probe_dsn)
    app = create_app(settings=settings, store=store, probe=probe, provider=provider, clock=clock)
    with TestClient(app) as client:
        yield SQLRig(client, app, store, probe, mock, clock, isolated_database, sessions)
    provider.client.close()
    transport.close()


@pytest.mark.parametrize("provider_failure", [False, True])
def test_sql_login_ciphertext_and_local_logout_commit(sql_rig, provider_failure):
    rig = sql_rig
    response = sign_in(rig.client)
    reference = rig.client.cookies.get("abogalia_session")
    record = rig.record(reference)
    assert bool(record is not None and rig.count_sessions() == 1)
    assert bool(set(response.json()) == {"authenticated", "user"})
    assert bool(set(response.json()["user"]) == {"id", "email", "assurance"})
    with rig.connect() as conn:
        ciphertext = bytes(
            conn.execute(
                "SELECT secret_ciphertext FROM identity.app_sessions WHERE digest = %s",
                (record.digest,),
            ).fetchone()[0]
        )
    assert bool(record.access_token.encode() not in ciphertext)
    assert bool(record.refresh_token.encode() not in ciphertext)
    assert bool(record.email.encode() not in ciphertext)
    assert bool(rig.probe.active(record.provider_session_id, record.subject))
    if provider_failure:
        rig.mock.mode = "logout_down"
    result = rig.client.post(
        "/api/auth/logout", headers=bootstrap(rig.client), json={"scope": "local"}
    )
    assert bool(result.status_code == (503 if provider_failure else 204))
    assert bool(rig.count_sessions() == 0)
    assert bool(rig.client.cookies.get("abogalia_session") is None)
    assert bool(rig.client.get("/api/auth/session").json() == {"authenticated": False})


def test_sql_upstream_revoked_cookie_cannot_global_logout_newer_session(sql_rig):
    rig = sql_rig
    sign_in(rig.client)
    old_provider_session = rig.mock.session_id
    rig.clock.now += timedelta(seconds=1)
    rig.mock.session_id = str(uuid4())
    rig.provider_sessions[rig.mock.session_id] = rig.mock.subject
    with TestClient(rig.app) as newer_client:
        sign_in(newer_client)
        newer_reference = newer_client.cookies.get("abogalia_session")
        assert bool(rig.count_sessions() == 2)
        rig.provider_sessions.pop(old_provider_session)
        response = rig.client.post(
            "/api/auth/logout", headers=bootstrap(rig.client), json={"scope": "global"}
        )
        assert bool(response.status_code == 401)
        assert bool(response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED")
        assert bool(rig.mock.calls["/logout"] == 0)
        assert bool(rig.count_sessions() == 1)
        assert bool(rig.record(newer_reference) is not None)
        assert bool(newer_client.get("/api/auth/session").json()["authenticated"])


def test_sql_refresh_rejection_commits_credential_deletion(sql_rig):
    rig = sql_rig
    sign_in(rig.client)
    reference = rig.client.cookies.get("abogalia_session")
    original = rig.mock.handle

    def rejected_refresh(request):
        if request.url.params.get("grant_type") == "refresh_token":
            return httpx.Response(400, json={"code": "refresh_token_not_found"})
        return original(request)

    rig.app.state.identity.provider.client = httpx.Client(
        transport=httpx.MockTransport(rejected_refresh)
    )
    rig.clock.now += timedelta(minutes=15)
    result = rig.client.get("/api/auth/mfa/factors")
    assert bool(result.status_code == 401)
    assert bool(rig.count_sessions() == 0 and rig.record(reference) is None)
    assert bool(rig.client.cookies.get("abogalia_session") is None)


@pytest.mark.parametrize("action", ["foreign_factor", "invalid_otp"])
def test_sql_successful_refresh_survives_failed_action_without_activity_touch(sql_rig, action):
    rig = sql_rig
    sign_in(rig.client)
    reference = rig.client.cookies.get("abogalia_session")
    challenge_id = None
    if action == "invalid_otp":
        # A live challenge spans the token expiration so verify, not challenge
        # expiry, is what rejects the code after successful refresh.
        rig.clock.now += timedelta(minutes=14)
        challenge = rig.client.post(
            "/api/auth/mfa/challenge",
            headers=bootstrap(rig.client),
            json={"factor_id": rig.mock.factor},
        )
        assert bool(challenge.status_code == 200)
        challenge_id = challenge.json()["challenge_id"]
    before = rig.record(reference)
    rig.clock.now += timedelta(minutes=1 if action == "invalid_otp" else 15)
    if action == "foreign_factor":
        result = rig.client.post(
            "/api/auth/mfa/challenge",
            headers=bootstrap(rig.client),
            json={"factor_id": str(uuid4())},
        )
        expected = 403
    else:
        original = rig.mock.handle

        def invalid_otp(request):
            if request.url.path.endswith("/verify"):
                return httpx.Response(400, json={"code": "mfa_verification_failed"})
            return original(request)

        rig.app.state.identity.provider.client = httpx.Client(
            transport=httpx.MockTransport(invalid_otp)
        )
        result = rig.client.post(
            "/api/auth/mfa/verify",
            headers=bootstrap(rig.client),
            json={
                "factor_id": rig.mock.factor,
                "challenge_id": challenge_id,
                "code": "000000",
            },
        )
        expected = 401
    assert bool(result.status_code == expected)
    after = rig.record(reference)
    assert bool(after is not None and before is not None)
    assert bool(after.refresh_token != before.refresh_token)
    assert bool(after.access_token != before.access_token)
    assert bool(after.last_activity_at == before.last_activity_at)
    assert bool(after.token_expires_at > before.token_expires_at)
    assert bool(rig.mock.refreshes == 1)
    assert bool(rig.client.get("/api/auth/session").json()["authenticated"])
    assert bool(rig.mock.refreshes == 1)
    persisted = rig.record(reference)
    assert bool(persisted.refresh_token == after.refresh_token)
    assert bool(persisted.last_activity_at == before.last_activity_at)


@pytest.mark.parametrize("revoke_at_frontier", [False, True])
def test_sql_mfa_rotation_and_frontier_deletion_of_new_digest(
    sql_rig, monkeypatch, revoke_at_frontier
):
    from abogalia_api.identity.storage import _Transaction

    rig = sql_rig
    sign_in(rig.client)
    original_reference = rig.client.cookies.get("abogalia_session")
    original_record = rig.record(original_reference)
    challenge = rig.client.post(
        "/api/auth/mfa/challenge",
        headers=bootstrap(rig.client),
        json={"factor_id": rig.mock.factor},
    )
    assert bool(challenge.status_code == 200)
    rotated_digests = []
    save = _Transaction.save

    def save_then_revoke(transaction, record):
        save(transaction, record)
        if record.digest != original_record.digest and record.assurance == "aal2":
            rotated_digests.append(record.digest)
            if revoke_at_frontier:
                rig.provider_sessions.pop(rig.mock.session_id)

    monkeypatch.setattr(_Transaction, "save", save_then_revoke)
    result = rig.client.post(
        "/api/auth/mfa/verify",
        headers=bootstrap(rig.client),
        json={
            "factor_id": rig.mock.factor,
            "challenge_id": challenge.json()["challenge_id"],
            "code": "000000",
        },
    )
    assert bool(rotated_digests)
    assert bool(rig.record(original_reference) is None)
    if revoke_at_frontier:
        assert bool(result.status_code == 401)
        assert bool(set(result.json()) == {"error"})
        assert bool(rig.count_sessions() == 0)
        assert bool(rig.client.cookies.get("abogalia_session") is None)
        with rig.store.transaction(rotated_digests[0]) as tx:
            assert bool(tx.record is None)
    else:
        assert bool(result.status_code == 200 and result.json()["user"]["assurance"] == "aal2")
        new_reference = rig.client.cookies.get("abogalia_session")
        assert bool(new_reference != original_reference)
        rotated = rig.record(new_reference)
        assert bool(rotated is not None and rotated.assurance == "aal2")
        assert bool(rotated.created_at == original_record.created_at)
        assert bool(rig.count_sessions() == 1)
