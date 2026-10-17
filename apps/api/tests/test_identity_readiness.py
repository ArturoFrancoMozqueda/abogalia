"""Preflight negatives plus actual catalog inspection in the isolated SQL fixture."""

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import psycopg
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from jwt.algorithms import ECAlgorithm

pytest_plugins = ["storage_fixtures"]
SPEC = importlib.util.spec_from_file_location(
    "identity_readiness", Path(__file__).parents[3] / "scripts/check_identity_readiness.py"
)
readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readiness)


def public_jwks():
    key = ec.generate_private_key(ec.SECP256R1()).public_key()
    return {"keys": [json.loads(ECAlgorithm.to_jwk(key)) | {"kid": "synthetic", "alg": "ES256"}]}


def test_presence_never_accesses_values():
    class NamesOnly(dict):
        def __getitem__(self, _):
            raise AssertionError("Values must not be accessed")

        def get(self, *_):
            raise AssertionError("Values must not be accessed")

    result = readiness.presence(NamesOnly({readiness.NAMES[0]: None, "UNRELATED": None}))
    assert set(result) == set(readiness.NAMES)
    assert result[readiness.NAMES[0]] is True
    assert sum(result.values()) == 1


def test_default_no_connections(monkeypatch, capsys):
    def forbidden(*_, **__):
        raise AssertionError("Connection attempted")

    monkeypatch.setattr(psycopg, "connect", forbidden)
    assert readiness.main([]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "disabled"
    assert report["real_readiness"] == "pending"
    assert report["jwks"] == "not_executed"


@pytest.mark.parametrize("args", [["--inspect-local"], ["--inspect-local", "--socket", "relative"]])
def test_local_guard_before_connection(args, monkeypatch, capsys):
    def forbidden(*_, **__):
        raise AssertionError("Connection attempted")

    monkeypatch.setattr(psycopg, "connect", forbidden)
    assert readiness.main(args) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "local_catalog_unavailable"


def test_disabled_catalog_does_not_touch_connection():
    assert readiness.inspect_catalog(object(), readiness.RUNTIME)["status"] == "disabled"


def test_jwks_public_valid():
    assert all(readiness.jwks_checks(public_jwks(), readiness.JWKS_URL, enabled=True).values())


@pytest.mark.parametrize(
    "mutation",
    ["disabled", "destination", "private", "hs256", "empty", "duplicate", "malformed", "not_list"],
)
def test_jwks_fail_closed(mutation):
    document = public_jwks()
    target = readiness.JWKS_URL
    enabled = True
    if mutation == "disabled":
        enabled = False
    elif mutation == "destination":
        target = "https://unapproved.invalid/auth/v1/.well-known/jwks.json"
    elif mutation == "private":
        document["keys"][0]["d"] = "PUBLIC_INVALID_TEST_FIELD"
    elif mutation == "hs256":
        document["keys"][0]["alg"] = "HS256"
    elif mutation == "empty":
        document["keys"] = []
    elif mutation == "duplicate":
        document["keys"] *= 2
    elif mutation == "not_list":
        document["keys"] = {}
    else:
        document["keys"][0]["x"] = "invalid"
    assert not all(readiness.jwks_checks(document, target, enabled=enabled).values())


@pytest.mark.parametrize("role", [readiness.RUNTIME, readiness.PROBE])
def test_real_catalog_baseline(database, role):
    dsn = database.runtime_dsn if role == readiness.RUNTIME else database.probe_dsn
    with psycopg.connect(dsn) as conn:
        report = readiness.inspect_catalog(conn, role, enabled=True)
        assert conn.info.transaction_status == 0
    assert report["status"] == "catalog_passed"
    assert all(report["checks"].values())


@pytest.mark.parametrize(
    "mutation",
    [
        "role",
        "super",
        "membership",
        "schema_create",
        "rls",
        "policy",
        "column",
        "extra_table",
        "sequence",
        "function",
        "column_type",
        "missing_table",
    ],
)
def test_catalog_metadata_negatives(database, mutation):
    with psycopg.connect(database.runtime_dsn) as conn:
        snapshot = list(deepcopy(readiness.catalog_snapshot(conn, readiness.RUNTIME)))
    if mutation in ("role", "super"):
        role = list(snapshot[0])
        role[0 if mutation == "role" else 1] = "wrong_role" if mutation == "role" else True
        snapshot[0] = role
    elif mutation == "membership":
        snapshot[1] = True
    elif mutation == "schema_create":
        snapshot[2] = [(n, u, True if n == "identity" else c) for n, u, c in snapshot[2]]
    elif mutation == "sequence":
        snapshot[4] = [(s, n, u, True, w) for s, n, u, _, w in snapshot[4]]
    elif mutation == "function":
        snapshot[5] = True
    elif mutation == "missing_table":
        snapshot[3] = [row for row in snapshot[3] if row[1] != "app_sessions"]
    elif mutation == "extra_table":
        snapshot[3].append(
            ("other", "synthetic", readiness.OWNER, False, False, {"SELECT"}, [], [])
        )
    else:
        rows = [list(row) for row in snapshot[3]]
        row = next(row for row in rows if row[1] == "users")
        if mutation == "rls":
            row[4] = False
        elif mutation == "policy":
            row[7] = []
        else:
            columns = [list(column) for column in row[6]]
            columns[0][1 if mutation == "column_type" else 4] = (
                "text" if mutation == "column_type" else True
            )
            row[6] = columns
        snapshot[3] = rows
    assert not all(readiness.assess(snapshot, readiness.RUNTIME).values())


def test_probe_full_table_select_rejected(database):
    with psycopg.connect(database.probe_dsn) as conn:
        snapshot = list(deepcopy(readiness.catalog_snapshot(conn, readiness.PROBE)))
    rows = [list(row) for row in snapshot[3]]
    next(row for row in rows if row[0:2] == ["auth", "sessions"])[5] = {"SELECT"}
    snapshot[3] = rows
    assert readiness.assess(snapshot, readiness.PROBE)["table_grants"] is False


def test_catalog_failure_suppressed():
    report = readiness.inspect_catalog(object(), readiness.RUNTIME, enabled=True)
    assert report == {"status": "catalog_unavailable", "checks": {}}


def test_unknown_cli_input_never_echoed(capsys):
    assert readiness.main(["--unsupported", "PUBLIC_SYNTHETIC_INPUT"]) == 2
    output = capsys.readouterr()
    assert output.err == ""
    assert json.loads(output.out) == {"status": "invalid_arguments", "real_readiness": "pending"}


def test_pg_environment_guard(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("PGSERVICE", "PUBLIC_SYNTHETIC_NAME")

    def forbidden(*_, **__):
        raise AssertionError("Connection attempted")

    monkeypatch.setattr(psycopg, "connect", forbidden)
    assert readiness.main(["--inspect-local", "--socket", str(tmp_path)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "local_catalog_unavailable"


def test_separate_runtime_and_probe_databases(database):
    for role, dsn, keep_schema in (
        (readiness.RUNTIME, database.runtime_dsn, "identity"),
        (readiness.PROBE, database.probe_dsn, "auth"),
    ):
        with psycopg.connect(dsn) as conn:
            snapshot = list(readiness.catalog_snapshot(conn, role))
        snapshot[2] = [row for row in snapshot[2] if row[0] == keep_schema]
        snapshot[3] = [row for row in snapshot[3] if row[0] == keep_schema]
        snapshot[4] = [row for row in snapshot[4] if row[0] == keep_schema]
        assert all(readiness.assess(snapshot, role).values())


def test_read_only_transaction_verified(database):
    with psycopg.connect(database.runtime_dsn) as conn:

        class VerifyReadOnly:
            info = conn.info

            def transaction(self):
                return conn.transaction()

            def execute(self, statement, *args):
                result = conn.execute(statement, *args)
                if statement.startswith("SELECT"):
                    assert conn.execute("SHOW transaction_read_only").fetchone() == ("on",)
                return result

        report = readiness.inspect_catalog(VerifyReadOnly(), readiness.RUNTIME, enabled=True)
        assert report["status"] == "catalog_passed"


def test_preexisting_transaction_denied(database):
    with psycopg.connect(database.runtime_dsn) as conn:
        with conn.transaction():
            report = readiness.inspect_catalog(conn, readiness.RUNTIME, enabled=True)
            assert report["status"] == "catalog_unavailable"


@pytest.mark.parametrize("variable", ["PGHOSTADDR", "PGOPTIONS", "PGSERVICE"])
def test_libpq_redirect_names_denied(variable, monkeypatch, capsys, tmp_path):
    monkeypatch.setenv(variable, "PUBLIC_SYNTHETIC_CONFIG")
    assert readiness.main(["--inspect-local", "--socket", str(tmp_path)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "local_catalog_unavailable"


def test_private_fixture_socket_guard(tmp_path):
    parent = tmp_path / "abogalia-identity-tests-synthetic"
    parent.mkdir(mode=0o700)
    socket = parent / "socket"
    socket.mkdir(mode=0o700)
    assert readiness.local_socket_allowed(socket)
    parent.chmod(0o755)
    assert not readiness.local_socket_allowed(socket)
    parent.chmod(0o700)
    socket.chmod(0o755)
    assert not readiness.local_socket_allowed(socket)
    socket.chmod(0o700)
    link = parent / "linked"
    link.symlink_to(socket, target_is_directory=True)
    assert not readiness.local_socket_allowed(link)
    other = tmp_path / "not-a-fixture"
    other.mkdir(mode=0o700)
    assert not readiness.local_socket_allowed(other)


def test_real_local_cli(database, capsys):
    from psycopg.conninfo import conninfo_to_dict

    parts = conninfo_to_dict(database.runtime_dsn)
    assert (
        readiness.main(["--inspect-local", "--socket", parts["host"], "--port", parts["port"]]) == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "local_catalog_passed"
    assert report["real_readiness"] == "pending"


def test_cli_malicious_unknown_argument_suppressed(capsys):
    assert readiness.main(["--PUBLIC_SYNTHETIC\nINPUT"]) == 2
    output = capsys.readouterr()
    assert output.err == ""
    assert json.loads(output.out)["status"] == "invalid_arguments"


def test_tcp_enabled_fixture_denied(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(readiness, "local_socket_allowed", lambda _: True)

    class TcpConnection:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def execute(self, statement):
            assert statement == "SHOW listen_addresses"
            return self

        def fetchone(self):
            return ("localhost",)

    monkeypatch.setattr(psycopg, "connect", lambda **_: TcpConnection())
    assert readiness.main(["--inspect-local", "--socket", str(tmp_path)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "local_catalog_unavailable"


def test_socket_wrong_owner_denied(tmp_path, monkeypatch):
    parent = tmp_path / "abogalia-identity-tests-synthetic"
    parent.mkdir(mode=0o700)
    socket = parent / "socket"
    socket.mkdir(mode=0o700)
    monkeypatch.setattr(readiness.os, "getuid", lambda: -1)
    assert not readiness.local_socket_allowed(socket)


def test_unexpected_schema_create_denied(database):
    with psycopg.connect(database.runtime_dsn) as conn:
        snapshot = list(readiness.catalog_snapshot(conn, readiness.RUNTIME))
    snapshot[2] = [*snapshot[2], ("unexpected", True, True)]
    assert readiness.assess(snapshot, readiness.RUNTIME)["schema_usage_only"] is False
