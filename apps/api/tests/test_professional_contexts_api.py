"""Professional first increment: SQL real isolated, synthetic signed HTTP Auth."""

from contextlib import contextmanager
from datetime import timedelta
from uuid import uuid4

import pytest
from test_auth import bootstrap, sign_in

from abogalia_api.professional_contexts.storage import PostgresProfessionalContextStore

pytest_plugins = ["test_identity_integration", "test_professional_contexts_storage"]
FIELDS = {"display_name": "PUBLIC_SYNTHETIC_PERSON", "declared_area": "PUBLIC_SYNTHETIC_AREA"}


@pytest.fixture
def professional_rig(professional_database, sql_rig):
    assert bool(professional_database is sql_rig.database)
    sql_rig.mock.assurance = "aal2"
    assert bool(sign_in(sql_rig.client).status_code == 200)
    return sql_rig


def counts(rig):
    with rig.connect() as conn:
        return conn.execute(
            "SELECT (SELECT count(*) FROM identity.professional_drafts), "
            "(SELECT count(*) FROM identity.professional_events)"
        ).fetchone()


def post(rig, path="/api/professional/profile", body=None):
    return rig.client.post(
        path, headers=bootstrap(rig.client), json=FIELDS if body is None else body
    )


def test_create_read_edit_contexts_withdraw_versions_and_no_permissions(professional_rig):
    rig = professional_rig
    empty = rig.client.get("/api/professional/profile")
    assert bool(
        empty.status_code == 200 and empty.json() == {"profile": None, "practice_context": None}
    )
    created = post(rig)
    assert bool(created.status_code == 201)
    data = created.json()
    assert bool(set(data) == {"profile", "practice_context"})
    assert bool(data["profile"]["state"] == "draft" and data["profile"]["publication"] == "private")
    assert bool(
        data["profile"]["review"] is None
        and data["profile"]["allowed_actions"] == ["edit", "withdraw"]
    )
    assert bool(data["practice_context"]["state"] == "preparing")
    assert bool(
        data["practice_context"]["capabilities"]
        == data["practice_context"]["allowed_actions"]
        == []
    )
    assert bool(post(rig).status_code == 409 and counts(rig) == (1, 1))
    edited = rig.client.patch(
        "/api/professional/profile",
        headers=bootstrap(rig.client),
        json={"expected_version": 1, "fields": {"display_name": "PUBLIC_EDIT"}},
    )
    assert bool(edited.status_code == 200 and edited.json()["profile"]["version"] == 2)
    assert bool(edited.json()["practice_context"]["version"] == 1)
    assert bool(edited.json()["practice_context"]["title"] == "PUBLIC_EDIT")
    contexts = rig.client.get("/api/professional/contexts?limit=1")
    assert bool(contexts.status_code == 200 and contexts.json()["next_cursor"] is None)
    assert bool(len(contexts.json()["contexts"]) == 1)
    stale = post(
        rig,
        "/api/professional/profile/withdraw",
        {"expected_version": 2, "expected_context_version": 2},
    )
    assert bool(stale.status_code == 409 and counts(rig) == (1, 2))
    withdrawn = post(
        rig,
        "/api/professional/profile/withdraw",
        {"expected_version": 2, "expected_context_version": 1},
    )
    assert bool(withdrawn.status_code == 200)
    assert bool(withdrawn.json()["profile"]["state"] == "withdrawn")
    assert bool(withdrawn.json()["practice_context"]["state"] == "closed")
    assert bool(withdrawn.json()["profile"]["allowed_actions"] == [])
    repeated = post(
        rig,
        "/api/professional/profile/withdraw",
        {"expected_version": 3, "expected_context_version": 2},
    )
    assert bool(repeated.status_code == 200 and counts(rig) == (1, 3))
    assert bool(post(rig).status_code == 409)


def test_mfa_required_without_persisting_professional_data(professional_database, sql_rig):
    rig = sql_rig
    sign_in(rig.client)
    result = post(rig)
    assert bool(result.status_code == 403 and result.json()["error"]["code"] == "MFA_REQUIRED")
    assert bool(counts(rig) == (0, 0))


@pytest.mark.parametrize(
    "body",
    [
        {"display_name": "PUBLIC", "owner_user_id": "PUBLIC"},
        {"display_name": "PUBLIC", "state": "enabled"},
        {"display_name": "PUBLIC", "registration_number": "PUBLIC"},
        {"display_name": None},
        {"display_name": " "},
        {"display_name": "PUBLIC\x00"},
        {"display_name": "x" * 121},
        {"display_name": "PUBLIC", "declared_area": "x" * 241},
    ],
)
def test_strict_minimal_fields_reject_without_input_echo(professional_rig, body):
    rig = professional_rig
    result = post(rig, body=body)
    assert bool(result.status_code == 422 and set(result.json()) == {"error"})
    assert bool(counts(rig) == (0, 0) and "PUBLIC" not in result.text)


@pytest.mark.parametrize(
    "body",
    [
        {"expected_version": True, "fields": {"declared_area": None}},
        {"expected_version": 1, "fields": {}},
        {"expected_version": 1, "fields": {"display_name": None}},
        {"expected_version": 1, "fields": {"legal_name": "PUBLIC"}},
    ],
)
def test_patch_strict_version_and_partial_shape(professional_rig, body):
    rig = professional_rig
    post(rig)
    result = rig.client.patch("/api/professional/profile", headers=bootstrap(rig.client), json=body)
    assert bool(result.status_code == 422 and counts(rig) == (1, 1))


@pytest.mark.parametrize(
    "problem", ["csrf", "origin", "bearer", "query", "oversize", "content_type"]
)
def test_transport_guards_no_effects(professional_rig, problem):
    rig = professional_rig
    headers = bootstrap(rig.client)
    path = "/api/professional/profile"
    if problem == "csrf":
        headers.pop("X-CSRF-Token")
    elif problem == "origin":
        headers["Origin"] = "https://unapproved.invalid"
    elif problem == "bearer":
        headers["Authorization"] = "PUBLIC_SYNTHETIC"
    elif problem == "query":
        path += "?public=marker"
    elif problem == "content_type":
        headers["Content-Type"] = "text/plain"
    body = FIELDS if problem != "oversize" else {"display_name": "x" * 8193}
    result = rig.client.post(path, headers=headers, json=body)
    assert bool(result.status_code in (403, 422) and counts(rig) == (0, 0))
    assert bool(result.headers["Cache-Control"] == "no-store")
    assert bool(result.headers["Referrer-Policy"] == "no-referrer")


@pytest.mark.parametrize(
    "route",
    [
        "profile/submit",
        "profile/publication",
        "firms",
        "invitations/PUBLIC/accept",
        "contexts/PUBLIC/activate",
        "reviews/PUBLIC/decision",
    ],
)
def test_future_families_not_fake_enabled(professional_rig, route):
    rig = professional_rig
    post(rig)
    result = post(rig, "/api/professional/" + route, {})
    assert bool(
        result.status_code == 403 and result.json()["error"]["code"] == "FEATURE_UNAVAILABLE"
    )
    assert bool(counts(rig) == (1, 1))


def test_actor_cannot_read_or_edit_another_owner_by_body_or_path(professional_rig):
    rig = professional_rig
    post(rig)
    first = rig.mock.subject
    rig.mock.subject = str(uuid4())
    rig.mock.session_id = str(uuid4())
    rig.provider_sessions[rig.mock.session_id] = rig.mock.subject
    sign_in(rig.client)
    empty = rig.client.get("/api/professional/profile")
    assert bool(empty.status_code == 200 and empty.json()["profile"] is None)
    editing = rig.client.patch(
        "/api/professional/profile",
        headers=bootstrap(rig.client),
        json={"expected_version": 1, "fields": {"display_name": "PUBLIC_ATTACK"}},
    )
    assert bool(editing.status_code == 404 and counts(rig) == (1, 1))
    assert bool(first not in editing.text)


@pytest.mark.parametrize("failure", ["revoked", "infra", "expiry", "sql_error"])
def test_business_rollback_at_auth_frontier_preserves_refresh_correctly(
    professional_rig, monkeypatch, failure
):
    rig = professional_rig
    reference = rig.client.cookies.get("abogalia_session")
    before = rig.record(reference)
    rig.clock.now += timedelta(minutes=14, seconds=40)
    original = PostgresProfessionalContextStore.create

    def create_then_fail(store, fields):
        aggregate = original(store, fields)
        if failure == "revoked":
            rig.provider_sessions.pop(rig.mock.session_id)
        elif failure == "infra":
            rig.mock.mode = "probe_unavailable"
        elif failure == "expiry":
            rig.clock.now += timedelta(hours=12)
        else:
            store._conn.execute("SELECT 1 / 0")
        return aggregate

    monkeypatch.setattr(PostgresProfessionalContextStore, "create", create_then_fail)
    result = post(rig)
    assert bool(result.status_code == (401 if failure in ("revoked", "expiry") else 503))
    assert bool(counts(rig) == (0, 0))
    after = rig.record(reference)
    if failure in ("revoked", "expiry"):
        assert bool(after is None and rig.count_sessions() == 0)
    else:
        assert bool(after is not None and after.access_token != before.access_token)
        assert bool(after.refresh_token != before.refresh_token and rig.count_sessions() == 1)
        assert bool(after.last_activity_at == before.last_activity_at)
        rig.mock.mode = "ok"
        assert bool(
            rig.client.get("/api/auth/session").status_code == 200 and rig.mock.refreshes == 1
        )


def test_success_reuses_identity_business_connection_and_updates_activity(
    professional_rig, monkeypatch
):
    from abogalia_api.identity.storage import _Transaction

    rig = professional_rig
    identity_connections, professional_connections = [], []
    business = _Transaction.business
    initialize = PostgresProfessionalContextStore.__init__

    @contextmanager
    def observed_business(transaction):
        with business(transaction) as conn:
            identity_connections.append(conn)
            yield conn

    def observed_professional(store, conn, **kwargs):
        professional_connections.append(conn)
        initialize(store, conn, **kwargs)

    rig.clock.now += timedelta(seconds=10)
    headers = bootstrap(rig.client)
    monkeypatch.setattr(_Transaction, "business", observed_business)
    monkeypatch.setattr(PostgresProfessionalContextStore, "__init__", observed_professional)
    result = rig.client.post("/api/professional/profile", headers=headers, json=FIELDS)
    assert bool(result.status_code == 201)
    assert bool(len(identity_connections) == len(professional_connections) == 1)
    assert bool(identity_connections[0] is professional_connections[0])
    reference = rig.client.cookies.get("abogalia_session")
    assert bool(rig.record(reference).last_activity_at == rig.clock())
