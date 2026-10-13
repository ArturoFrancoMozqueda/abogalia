import secrets

import pytest
from test_auth import bootstrap, sign_in

from abogalia_api.identity.config import Settings
from abogalia_api.identity.security import CSRF, random_reference
from abogalia_api.identity.service import AuthError

pytest_plugins = ["test_auth"]


def test_signed_double_submit_is_bound_to_reference_and_kind():
    csrf = CSRF(secrets.token_bytes(32))
    reference = random_reference()
    token = csrf.create(reference, "preauth")
    assert csrf.valid(token, reference, "preauth")
    assert not csrf.valid(token, random_reference(), "preauth")
    assert not csrf.valid(token, reference, "session")
    assert not csrf.valid(token + "modified", reference, "preauth")
    assert not CSRF(secrets.token_bytes(32)).valid(token, reference, "preauth")


@pytest.mark.parametrize(
    "abuse", ["missing", "origin", "null", "cookie", "header", "query", "bearer"]
)
def test_mutations_reject_abuse_before_provider(rig, abuse):
    client, _, _, _, mock, _ = rig
    headers = bootstrap(client)
    if abuse == "missing":
        headers.pop("X-CSRF-Token")
    elif abuse == "origin":
        headers["Origin"] = "https://other.example.invalid"
    elif abuse == "null":
        headers["Origin"] = "null"
    elif abuse == "header":
        headers["X-CSRF-Token"] = "public-marker"
    elif abuse == "cookie":
        client.cookies.clear()
    elif abuse == "bearer":
        headers["Authorization"] = "Bearer public-marker"
    path = "/api/auth/login" + ("?token=public-marker" if abuse == "query" else "")
    response = client.post(
        path,
        headers=headers,
        json={
            "email": "person@example.invalid",
            "password": "public-marker",
        },
    )
    assert response.status_code == 403
    assert mock.calls["/token"] == 0
    assert "public-marker" not in response.text
    assert response.headers["cache-control"] == "no-store"


def test_csrf_rotation_and_cross_session_replay(rig):
    client, app, _, _, mock, _ = rig
    old_headers = bootstrap(client)
    sign_in(client)
    response = client.post("/api/auth/logout", headers=old_headers, json={"scope": "local"})
    assert response.status_code == 403
    assert mock.calls["/logout"] == 0
    # Same header/cookie injected together still cannot defeat HMAC binding.
    token = old_headers["X-CSRF-Token"]
    reference = client.cookies.get("abogalia_session")
    with pytest.raises(AuthError):
        app.state.identity.validate_csrf(reference, token, token)


def test_oversize_and_invalid_json_no_echo(rig):
    client, _, _, _, mock, _ = rig
    headers = bootstrap(client)
    headers["Content-Type"] = "application/json"
    for body in ("synthetic-sensitive-marker" * 500, '{"password":'):
        response = client.post("/api/auth/login", headers=headers, content=body)
        assert response.status_code == 422
        assert "synthetic-sensitive-marker" not in response.text
    assert mock.calls["/token"] == 0


def test_origin_and_destination_configuration_rejects_unsafe_values():
    for configuration in (
        {"origin": "http://other.example.invalid"},
        {"development_http": False},
        {"project_url": "https://kova.example.invalid"},
        {"project_url": "https://xggefantvuwpilksfdoy.supabase.co@evil.example.invalid"},
        {"publishable_key": "sb_secret_public-marker"},
    ):
        with pytest.raises(ValueError):
            Settings(**configuration)


def test_access_log_filter_drops_auth_queries_before_formatting():
    import logging

    from abogalia_api.identity.logging import AuthAccessFilter

    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        "",
        1,
        '%s - "%s %s HTTP/%s" %d',
        ("127.0.0.1", "GET", "/api/auth/session?code=public-marker", "1.1", 403),
        None,
    )
    assert not AuthAccessFilter().filter(record)
    record.args = ("127.0.0.1", "GET", "/api/%61uth/session?code=public-marker", "1.1", 403)
    assert not AuthAccessFilter().filter(record)
    record.args = ("127.0.0.1", "GET", "/api/health", "1.1", 200)
    assert AuthAccessFilter().filter(record)
