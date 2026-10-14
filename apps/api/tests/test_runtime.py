"""Runtime configuration tests with generated keys and no provider/DB connections."""

from unittest.mock import patch

import psycopg
import pytest
from cryptography.fernet import Fernet

from abogalia_api.identity import runtime
from abogalia_api.identity.storage import PostgresSessionProbe, PostgresSessionStore
from abogalia_api.main import create_app

pytest_plugins = ["storage_fixtures"]

MARKER = "PUBLIC_SYNTHETIC_CONFIGURATION_DO_NOT_FORWARD"


def configuration():
    return {
        "ABOGALIA_IDENTITY_ENABLED": "1",
        "ABOGALIA_ENVIRONMENT": "production",
        "ABOGALIA_WEB_ORIGIN": "https://public-synthetic.example.invalid",
        "ABOGALIA_SUPABASE_URL": "https://spohytnxscljtitvmdab.supabase.co",
        "ABOGALIA_SUPABASE_PUBLISHABLE_KEY": "sb_publishable_" + MARKER,
        "ABOGALIA_CSRF_KEY": MARKER,
        "ABOGALIA_DATABASE_DSN": (
            "host=db.spohytnxscljtitvmdab.supabase.co dbname=postgres "
            "user=abogalia_identity_runtime sslmode=verify-full"
        ),
        "ABOGALIA_AUTH_SESSION_CHECK_DSN": (
            "host=db.spohytnxscljtitvmdab.supabase.co dbname=postgres "
            "user=abogalia_identity_probe sslmode=verify-full"
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
    for host, user in (
        ("db.spohytnxscljtitvmdab.supabase.co", role),
        ("aws-0-us-east-1.pooler.supabase.com", role + ".spohytnxscljtitvmdab"),
        ("aws-1-us-east-1.pooler.supabase.com", role + ".spohytnxscljtitvmdab"),
    ):
        assert (
            runtime.validate_dsn(
                f"host={host} dbname=postgres port=5432 user={user} sslmode=verify-full", role
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


def test_retired_auth_project_fails_closed_without_connecting():
    values = configuration()
    values["ABOGALIA_SUPABASE_URL"] = "https://xggefantvuwpilksfdoy.supabase.co"
    assert_closed(values)


@pytest.mark.parametrize(
    "field,role",
    [
        ("ABOGALIA_DATABASE_DSN", "abogalia_identity_runtime"),
        ("ABOGALIA_AUTH_SESSION_CHECK_DSN", "abogalia_identity_probe"),
    ],
)
@pytest.mark.parametrize("retired", ["direct", "pooler", "direct_uppercase", "host_list"])
def test_retired_database_project_fails_closed(field, role, retired):
    values = configuration()
    host = "db.xggefantvuwpilksfdoy.supabase.co"
    user = role
    if retired == "pooler":
        host = "aws-0-us-east-1.pooler.supabase.com"
        user += ".xggefantvuwpilksfdoy"
    elif retired == "direct_uppercase":
        host = host.upper()
    elif retired == "host_list":
        host += ",db.spohytnxscljtitvmdab.supabase.co"
    values[field] = f"host={host} dbname=postgres user={user}"
    assert_closed(values)


@pytest.mark.parametrize("field", ["ABOGALIA_DATABASE_DSN", "ABOGALIA_AUTH_SESSION_CHECK_DSN"])
@pytest.mark.parametrize(
    "change",
    [
        "host",
        "multi_host",
        "ip",
        "loopback",
        "socket",
        "database",
        "transaction",
        "port_list",
        "tls_missing",
        "tls_require",
        "tls_disable",
        "hostaddr",
        "service",
        "options",
        "passfile",
        "sslkey",
        "sslcert",
        "role",
        "other_project_pooler",
    ],
)
def test_remote_confinement_rejects_unapproved_destination_and_overrides(field, change):
    values = configuration()
    role = (
        "abogalia_identity_runtime"
        if field == "ABOGALIA_DATABASE_DSN"
        else "abogalia_identity_probe"
    )
    parts = {
        "host": "db.spohytnxscljtitvmdab.supabase.co",
        "dbname": "postgres",
        "user": role,
        "port": "5432",
        "sslmode": "verify-full",
    }
    replacements = {
        "host": ("host", "unapproved.invalid"),
        "multi_host": ("host", "db.spohytnxscljtitvmdab.supabase.co,unapproved.invalid"),
        "ip": ("host", "192.0.2.1"),
        "loopback": ("host", "127.0.0.1"),
        "socket": ("host", "/public/synthetic/socket"),
        "database": ("dbname", "other"),
        "transaction": ("port", "6543"),
        "port_list": ("port", "5432,6543"),
        "tls_require": ("sslmode", "require"),
        "tls_disable": ("sslmode", "disable"),
        "role": ("user", "abogalia_identity_owner"),
        "other_project_pooler": ("user", role + ".unapproved"),
    }
    if change == "tls_missing":
        del parts["sslmode"]
    elif change in replacements:
        name, value = replacements[change]
        parts[name] = value
    else:
        parts[change] = "PUBLIC_SYNTHETIC_ONLY"
    values[field] = psycopg.conninfo.make_conninfo(**parts)
    assert_closed(values)


@pytest.mark.parametrize(
    "name", ["PGHOSTADDR", "PGSERVICE", "PGOPTIONS", "PGSSLMODE", "PGPASSWORD"]
)
def test_inherited_libpq_setting_name_rejected_without_reading_values(name):
    values = configuration()
    values[name] = MARKER
    assert_closed(values)


def local_fixture_dsn(tmp_path, role="abogalia_identity_runtime"):
    parent = tmp_path / "abogalia-identity-tests-synthetic"
    parent.mkdir(mode=0o700)
    socket = parent / "socket"
    socket.mkdir(mode=0o700)
    return psycopg.conninfo.make_conninfo(
        host=str(socket), port="54983", dbname="abogalia_storage_test", user=role
    ), socket


@pytest.mark.parametrize("role", runtime.ROLES)
def test_local_fixture_requires_python_opt_in_and_no_connection(tmp_path, role):
    dsn, _ = local_fixture_dsn(tmp_path, role)
    with patch.object(psycopg, "connect", side_effect=AssertionError("No connection permitted")):
        with pytest.raises(ValueError):
            runtime.validate_dsn(dsn, role)
        assert runtime.validate_dsn(dsn, role, allow_local_fixture=True) is None


@pytest.mark.parametrize(
    "change",
    [
        "permissions",
        "parent_permissions",
        "owner",
        "symlink",
        "prefix",
        "database",
        "password",
        "role",
        "pooler_role",
        "remote",
        "port",
        "truthy_flag",
    ],
)
def test_local_fixture_guard_negative(tmp_path, monkeypatch, change):
    role = runtime.ROLES[0]
    dsn, socket = local_fixture_dsn(tmp_path)
    flag = True
    parts = psycopg.conninfo.conninfo_to_dict(dsn)
    if change == "permissions":
        socket.chmod(0o755)
    elif change == "parent_permissions":
        socket.parent.chmod(0o755)
    elif change == "owner":
        monkeypatch.setattr(runtime.os, "getuid", lambda: -1)
    elif change == "symlink":
        target = socket.parent / "target"
        socket.rename(target)
        socket.symlink_to(target, target_is_directory=True)
    elif change == "prefix":
        parts["host"] = str(tmp_path)
    elif change == "database":
        parts["dbname"] = "postgres"
    elif change == "password":
        parts["password"] = ""
    elif change == "role":
        parts["user"] = "abogalia_identity_owner"
    elif change == "pooler_role":
        parts["user"] += ".spohytnxscljtitvmdab"
    elif change == "remote":
        parts["host"] = "db.spohytnxscljtitvmdab.supabase.co"
    elif change == "port":
        parts["port"] = "543"
    else:
        flag = 1
    with pytest.raises(ValueError) as error:
        runtime.validate_dsn(
            psycopg.conninfo.make_conninfo(**parts), role, allow_local_fixture=flag
        )
    assert str(error.value) == "Identity runtime configuration unavailable"


def test_development_environment_cannot_enable_local_fixture(tmp_path):
    values = configuration()
    values["ABOGALIA_ENVIRONMENT"] = "development"
    values["ABOGALIA_WEB_ORIGIN"] = "http://127.0.0.1:5190"
    values["ABOGALIA_DATABASE_DSN"], _ = local_fixture_dsn(tmp_path)
    values["ABOGALIA_LOCAL_FIXTURE"] = "1"
    assert_closed(values)


def test_existing_isolated_sql_fixture_is_accepted_only_with_opt_in(database):
    for dsn, role in (
        (database.runtime_dsn, runtime.ROLES[0]),
        (database.probe_dsn, runtime.ROLES[1]),
    ):
        original = psycopg.conninfo.conninfo_to_dict(dsn)
        fixture = psycopg.conninfo.make_conninfo(
            **{name: original[name] for name in ("host", "port", "dbname", "user")}
        )
        with pytest.raises(ValueError):
            runtime.validate_dsn(fixture, role)
        assert runtime.validate_dsn(fixture, role, allow_local_fixture=True) is None
