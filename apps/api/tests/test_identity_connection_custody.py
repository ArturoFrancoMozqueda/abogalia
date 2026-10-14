"""Internal connection guards; synthetic configuration, no certificate/key files."""

from unittest.mock import patch

import psycopg
import pytest
from cryptography.fernet import Fernet

from abogalia_api.identity import storage
from abogalia_api.identity.contracts import StorageUnavailable

DSN = (
    "host=db.spohytnxscljtitvmdab.supabase.co dbname=postgres "
    "user=abogalia_identity_runtime sslmode=verify-full"
)
SUBJECT = "00000000-0000-0000-0000-000000000001"
SID = "00000000-0000-0000-0000-000000000002"


def operate(kind):
    if kind == "store":
        with storage.PostgresSessionStore(DSN, Fernet.generate_key()).transaction("0" * 64):
            pytest.fail("No real connection allowed")
    elif kind == "probe":
        storage.PostgresSessionProbe(DSN).active(SID, SUBJECT)
    else:
        storage.PostgresIdentityMaintenance(DSN).purge(retired_subjects=set())


@pytest.mark.parametrize("kind", ["store", "probe", "maintenance"])
def test_internal_sslcertmode_and_no_implicit_password_passfile(kind):
    calls = []

    def captured(*args, **kwargs):
        calls.append((args, kwargs))
        raise psycopg.OperationalError("PUBLIC_SYNTHETIC_DIAGNOSTIC")

    with patch.object(storage.psycopg, "connect", captured):
        with pytest.raises(StorageUnavailable) as error:
            operate(kind)
    assert bool(len(calls) == 1)
    args, kwargs = calls[0]
    assert bool(kwargs["sslcertmode"] == "disable")
    assert bool(kwargs["password"] == "" and kwargs["passfile"] == storage.os.devnull)
    assert bool(psycopg.conninfo.conninfo_to_dict(args[0])["sslmode"] == "verify-full")
    assert bool(str(error.value) == "" and error.value.__cause__ is None)


@pytest.mark.parametrize("kind", ["store", "probe", "maintenance"])
@pytest.mark.parametrize("version", [159999, 0, None, True, "PUBLIC_SYNTHETIC_VERSION"])
def test_unsupported_client_fails_before_connect_without_fallback(kind, version):
    with (
        patch.object(storage.psycopg.pq, "version", return_value=version),
        patch.object(storage.psycopg, "connect") as connect,
        pytest.raises(StorageUnavailable) as error,
    ):
        operate(kind)
    assert bool(not connect.called and str(error.value) == "")


@pytest.mark.parametrize("version", [160000, 170011, 180006])
def test_supported_client_internal_guard(version):
    with patch.object(storage.psycopg.pq, "version", return_value=version):
        kwargs = storage._credentials(DSN)
    assert bool(kwargs["sslcertmode"] == "disable")


def test_parser_and_version_errors_sanitized_without_connection():
    for target in ("version", "parser"):
        with (
            patch.object(storage.psycopg, "connect") as connect,
            patch.object(
                storage.psycopg.pq if target == "version" else storage,
                "version" if target == "version" else "conninfo_to_dict",
                side_effect=RuntimeError("PUBLIC_SYNTHETIC_PRIVATE_DIAGNOSTIC"),
            ),
            pytest.raises(StorageUnavailable) as error,
        ):
            operate("probe")
        assert bool(not connect.called and str(error.value) == "")
