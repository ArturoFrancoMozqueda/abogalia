"""Synthetic GoTrue formats; no network, secrets, real accounts or email."""

import httpx
import pytest

from abogalia_api.identity.config import Settings
from abogalia_api.identity.provider import ProviderFailure, SupabaseProvider


@pytest.fixture
def settings():
    return Settings(
        project_url="https://spohytnxscljtitvmdab.supabase.co",
        publishable_key="sb_publishable_SYNTHETIC_ONLY",
        csrf_key=b"PUBLIC_SYNTHETIC_ONLY" * 2,
    )


@pytest.mark.parametrize(
    "payload,kind",
    [
        ({"code": "invalid_credentials"}, "rejected"),
        ({"code": 400, "error_code": "invalid_credentials"}, "rejected"),
        ({"code": 422, "error_code": "weak_password"}, "weak"),
        ({"code": 400, "msg": "Invalid login credentials"}, "unavailable"),
        ({"code": 400, "error_code": []}, "unavailable"),
        ({"code": "unknown", "error_code": "invalid_credentials"}, "unavailable"),
    ],
)
def test_login_uses_stable_category_and_never_message(settings, payload, kind):
    client = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(400, json=payload))
    )
    provider = SupabaseProvider(settings, client)
    with pytest.raises(ProviderFailure) as failure:
        provider.login("synthetic@example.invalid", "PUBLIC_SYNTHETIC_ONLY")
    assert failure.value.kind == kind
    assert str(failure.value) == "Identity provider operation failed"


@pytest.mark.parametrize(
    "payload,absent",
    [
        ({"code": 403, "error_code": "session_not_found"}, True),
        ({"code": 403, "error_code": "user_not_found"}, True),
        ({"code": 403, "error_code": "bad_jwt"}, False),
        ({"code": 403, "msg": "session_not_found"}, False),
        ({"code": "unknown", "error_code": "session_not_found"}, False),
    ],
)
def test_session_absence_still_requires_allowlisted_category(settings, payload, absent):
    client = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(403, json=payload))
    )
    provider = SupabaseProvider(settings, client)
    if absent:
        assert provider.session_subject("PUBLIC_SYNTHETIC_ONLY") is None
    else:
        with pytest.raises(ProviderFailure):
            provider.session_subject("PUBLIC_SYNTHETIC_ONLY")
