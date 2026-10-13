"""Runtime configuration tests with generated keys and no provider/DB connections."""

from unittest.mock import patch

import psycopg
import pytest
from cryptography.fernet import Fernet

from abogalia_api.identity import runtime
from abogalia_api.identity.storage import PostgresSessionProbe, PostgresSessionStore
from abogalia_api.main import create_app

MARKER = "PUBLIC_SYNTHETIC_CONFIGURATION_DO_NOT_FORWARD"


def configuration():
    return {
        "ABOGALIA_IDENTITY_ENABLED": "1",
        "ABOGALIA_ENVIRONMENT": "production",
        "ABOGALIA_WEB_ORIGIN": "https://public-synthetic.example.invalid",
        "ABOGALIA_SUPABASE_URL": "https://xggefantvuwpilksfdoy.supabase.co",
        "ABOGALIA_SUPABASE_PUBLISHABLE_KEY": "sb_publishable_" + MARKER,
        "ABOGALIA_CSRF_KEY": MARKER,
        "ABOGALIA_DATABASE_DSN": (
            "host=/public/synthetic/socket dbname=synthetic user=abogalia_identity_runtime"
        ),
        "ABOGALIA_AUTH_SESSION_CHECK_DSN": (
            "host=/public/synthetic/socket dbname=synthetic user=abogalia_identity_probe"
        ),
        "ABOGALIA_SESSION_CIPHER_KEY": Fernet.generate_key().decode(),
    }


def assert_closed(values):
    with (
        patch.object(runtime.os, "environ", values),
        patch.object(psycopg, "connect", side_effect=AssertionError("No connection permitted")),
        pytest.raises(RuntimeError) as error,
    ):
        runtime.load_runtime()
    assert bool(str(error.value) == "Identity runtime configuration unavailable")
    assert bool(MARKER not in str(error.value))
    assert error.value.__suppress_context__


def test_disabled_identity_ignores_other_product_variables_and_returns_no_custody():
    values = {
        "SUPABASE_URL": "https://public-unrelated.example.invalid",
        "DATABASE_URL": MARKER,
        "PGPASSWORD": MARKER,
        "ABOGALIA_DATABASE_DSN": MARKER,
    }
    with (
        patch.object(runtime.os, "environ", values),
        patch.object(psycopg, "connect", side_effect=AssertionError("No connection permitted")),
    ):
        settings, store, probe = runtime.load_runtime()
    assert not settings.configured
    assert store is None and probe is None


@pytest.mark.parametrize(
    "missing",
    [
        "ABOGALIA_WEB_ORIGIN",
        "ABOGALIA_SUPABASE_URL",
        "ABOGALIA_SUPABASE_PUBLISHABLE_KEY",
        "ABOGALIA_CSRF_KEY",
        "ABOGALIA_DATABASE_DSN",
        "ABOGALIA_SESSION_CIPHER_KEY",
        "ABOGALIA_AUTH_SESSION_CHECK_DSN",
    ],
)
def test_missing_required_configuration_raises_fixed_redacted_error(missing):
    values = configuration()
    values.pop(missing)
    # Missing configuration raises directly; no underlying value diagnostic exists.
    with patch.object(runtime.os, "environ", values), pytest.raises(RuntimeError) as error:
        runtime.load_runtime()
    assert bool(str(error.value) == "Identity runtime configuration unavailable")
    assert bool(MARKER not in str(error.value))


@pytest.mark.parametrize(
    "dsn",
    [
        "dbname=synthetic user=abogalia_identity_runtime",
        "host=/public/synthetic/socket user=abogalia_identity_runtime",
        "host=/public/synthetic/socket dbname=synthetic",
        "host=/public/synthetic/socket dbname=synthetic user=abogalia_identity_owner",
        "host=/public/synthetic/socket dbname=synthetic user=abogalia_identity_probe",
        "host=/public/synthetic/socket dbname=synthetic "
        "user=abogalia_identity_runtime service=synthetic",
        "host=/public/synthetic/socket dbname=synthetic "
        "user=abogalia_identity_runtime options=synthetic",
        "host=/public/synthetic/socket dbname=synthetic "
        "user=abogalia_identity_runtime passfile=/synthetic",
        "host=/public/synthetic/socket dbname=synthetic user=abogalia_identity_runtime.foreign",
    ],
)
def test_runtime_dsn_rejects_missing_explicit_destination_elevation_and_external_defaults(dsn):
    values = configuration()
    values["ABOGALIA_DATABASE_DSN"] = dsn
    assert_closed(values)


def test_probe_rejects_runtime_dsn_even_when_destination_matches():
    values = configuration()
    values["ABOGALIA_AUTH_SESSION_CHECK_DSN"] = values["ABOGALIA_DATABASE_DSN"]
    assert_closed(values)


@pytest.mark.parametrize("role", ["abogalia_identity_runtime", "abogalia_identity_probe"])
def test_only_approved_role_and_pooler_qualification_are_accepted(role):
    for user in (role, role + ".xggefantvuwpilksfdoy"):
        assert (
            runtime.validate_dsn(
                "host=/public/synthetic/socket dbname=synthetic user=" + user, role
            )
            is None
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("ABOGALIA_WEB_ORIGIN", "http://127.0.0.1:5190"),
        ("ABOGALIA_WEB_ORIGIN", "https://public-synthetic.example.invalid?marker=" + MARKER),
        ("ABOGALIA_SUPABASE_URL", "https://unapproved.example.invalid"),
        ("ABOGALIA_SUPABASE_PUBLISHABLE_KEY", MARKER),
        ("ABOGALIA_CSRF_KEY", "short-public-value"),
        ("ABOGALIA_SESSION_CIPHER_KEY", MARKER),
    ],
)
def test_invalid_origin_destination_and_key_configuration_fail_closed_without_outputs(field, value):
    values = configuration()
    values[field] = value
    assert_closed(values)


def test_enabled_runtime_constructs_separate_dependencies_without_connecting_or_repr_values():
    with (
        patch.object(runtime.os, "environ", configuration()),
        patch.object(psycopg, "connect", side_effect=AssertionError("No connection permitted")),
    ):
        settings, store, probe = runtime.load_runtime()
    assert settings.configured and not settings.development_http
    assert isinstance(store, PostgresSessionStore)
    assert isinstance(probe, PostgresSessionProbe)
    assert bool(MARKER not in repr(settings) + repr(store) + repr(probe))


def test_explicit_development_http_only_accepts_approved_loopback_origin():
    values = configuration()
    values["ABOGALIA_ENVIRONMENT"] = "development"
    values["ABOGALIA_WEB_ORIGIN"] = "http://127.0.0.1:5190"
    with patch.object(runtime.os, "environ", values):
        settings, _, _ = runtime.load_runtime()
    assert settings.development_http
    values["ABOGALIA_WEB_ORIGIN"] = "http://public-synthetic.example.invalid"
    assert_closed(values)


def test_default_app_factory_does_not_swallow_invalid_enabled_runtime():
    with (
        patch.object(runtime.os, "environ", {"ABOGALIA_IDENTITY_ENABLED": "1"}),
        pytest.raises(RuntimeError) as error,
    ):
        create_app()
    assert bool(str(error.value) == "Identity runtime configuration unavailable")
