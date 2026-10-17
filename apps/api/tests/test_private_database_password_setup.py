"""Synthetic private files and fake connections only; no remote password changes."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

SPEC = importlib.util.spec_from_file_location(
    "private_database_setup",
    Path(__file__).resolve().parents[3] / "scripts/configure_identity_database_password.py",
)
SETUP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SETUP)
PUBLIC_ADMIN = "PUBLIC_SYNTHETIC_ADMIN"
PUBLIC_RUNTIME = "PUBLIC_SYNTHETIC_RUNTIME"


def private_file(tmp_path, text):
    path = tmp_path / ".env.database-setup"
    path.write_text(text)
    path.chmod(0o600)
    return path


def test_private_input_literal_without_shell_interpolation_or_echo(tmp_path, capsys):
    value = "PUBLIC_SYNTHETIC_$`;&|_LITERAL"
    source = private_file(tmp_path, SETUP.NAME + "=" + value + "\n")
    assert bool(SETUP.private_password(source) == value)
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("problem", ["empty", "extra", "mode", "symlink", "hardlink", "size"])
def test_private_input_rejects_unsafe_file_without_output(tmp_path, problem, capsys):
    source = private_file(tmp_path, SETUP.NAME + "=" + PUBLIC_ADMIN + "\n")
    if problem == "empty":
        source.write_text(SETUP.NAME + "=\n")
    elif problem == "extra":
        source.write_text(SETUP.NAME + "=" + PUBLIC_ADMIN + "\nOTHER=PUBLIC\n")
    elif problem == "mode":
        source.chmod(0o644)
    elif problem == "symlink":
        linked = tmp_path / "link"
        linked.symlink_to(source)
        source = linked
    elif problem == "hardlink":
        (tmp_path / "link").hardlink_to(source)
    else:
        source.write_text(SETUP.NAME + "=" + "P" * 5000)
    with pytest.raises((SETUP.SetupUnavailable, OSError)):
        SETUP.private_password(source)
    assert capsys.readouterr() == ("", "")


class Connection:
    def __init__(self, admin, guard=True):
        self.admin, self.guard = admin, guard
        self.statements = []
        self.pgconn = SimpleNamespace(encrypt_password=self.encrypt)

    def encrypt(self, password, role, algorithm):
        assert bool(password == PUBLIC_RUNTIME.encode())
        assert role == SETUP.ROLE.encode() and algorithm == b"scram-sha-256"
        return b"PUBLIC_SYNTHETIC_SCRAM_VERIFIER"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, statement, parameters=None):
        self.statements.append(statement)
        if str(statement).startswith("SELECT current_user"):
            value = ("postgres" if self.admin else SETUP.ROLE, "postgres")
        elif "pg_roles" in str(statement):
            value = (self.guard,)
        else:
            assert "ALTER ROLE" in statement.as_string()
            assert bool(PUBLIC_RUNTIME not in statement.as_string())
            assert bool(PUBLIC_ADMIN not in statement.as_string())
            value = None
        return SimpleNamespace(fetchone=lambda: value)


def test_fixed_tls_role_and_private_output_no_env_reads(tmp_path, monkeypatch, capsys):
    output = tmp_path / ".env.database-runtime"
    application_env = tmp_path / ".env"
    application_env.write_text("PUBLIC_SYNTHETIC_UNTOUCHED")
    monkeypatch.setattr(SETUP.secrets, "token_urlsafe", lambda count: PUBLIC_RUNTIME)
    connections = []

    def connect(**kwargs):
        assert kwargs["sslmode"] == "verify-full" and kwargs["sslcertmode"] == "disable"
        assert kwargs["host"] == SETUP.HOST and kwargs["port"] == 5432
        assert kwargs["passfile"] == "/dev/null" and kwargs["dbname"] == "postgres"
        admin = kwargs["user"] == "postgres." + SETUP.PROJECT
        assert bool(kwargs["password"] == (PUBLIC_ADMIN if admin else PUBLIC_RUNTIME))
        conn = Connection(admin)
        connections.append(conn)
        return conn

    SETUP.configure(PUBLIC_ADMIN, connect=connect, output=output)
    assert len(connections) == 2 and output.stat().st_mode & 0o777 == 0o600
    assert application_env.read_text() == "PUBLIC_SYNTHETIC_UNTOUCHED"
    assert output.read_text().startswith("ABOGALIA_DATABASE_DSN=host=" + SETUP.HOST)
    assert bool(PUBLIC_ADMIN not in output.read_text())
    with pytest.raises(SETUP.SetupUnavailable):
        SETUP.configure(PUBLIC_ADMIN, connect=lambda **kwargs: pytest.fail(), output=output)
    assert capsys.readouterr() == ("", "")


def test_unsafe_runtime_role_denies_password_change(tmp_path):
    conn = Connection(True, guard=False)
    with pytest.raises(SETUP.SetupUnavailable):
        SETUP.configure(PUBLIC_ADMIN, connect=lambda **kwargs: conn, output=tmp_path / "runtime")
    assert not (tmp_path / "runtime").exists()
    assert not any("ALTER ROLE" in str(statement) for statement in conn.statements)


def test_altered_ca_rejected_before_any_connection(tmp_path, monkeypatch):
    fake = tmp_path / "public-ca.crt"
    fake.write_text("PUBLIC_SYNTHETIC_WRONG_CA")
    monkeypatch.setattr(SETUP, "CA", fake)
    with pytest.raises(SETUP.SetupUnavailable):
        SETUP.configure(
            PUBLIC_ADMIN, connect=lambda **kwargs: pytest.fail(), output=tmp_path / "runtime"
        )


@pytest.mark.parametrize("failure", ["write", "fsync"])
def test_private_candidate_failure_prevents_alter(tmp_path, monkeypatch, failure):
    monkeypatch.setattr(SETUP.secrets, "token_urlsafe", lambda count: PUBLIC_RUNTIME)
    conn = Connection(True)
    if failure == "write":

        def fail_write(*args):
            raise OSError("PUBLIC_SYNTHETIC_WRITE_FAILURE")

        monkeypatch.setattr(SETUP, "write_runtime_file", fail_write)
    else:

        def fail_sync(*args):
            raise OSError("PUBLIC_SYNTHETIC_SYNC_FAILURE")

        monkeypatch.setattr(SETUP.os, "fsync", fail_sync)
    with pytest.raises(OSError):
        SETUP.configure(PUBLIC_ADMIN, connect=lambda **kwargs: conn, output=tmp_path / "runtime")
    assert not any("ALTER ROLE" in str(statement) for statement in conn.statements)


@pytest.mark.parametrize("failure", ["commit", "runtime_login"])
def test_uncertain_outcome_preserves_candidate_and_refuses_retry(tmp_path, monkeypatch, failure):
    output = tmp_path / "runtime"
    monkeypatch.setattr(SETUP.secrets, "token_urlsafe", lambda count: PUBLIC_RUNTIME)

    class CommitFailure(Connection):
        def __exit__(self, *args):
            raise OSError("PUBLIC_SYNTHETIC_COMMIT_FAILURE")

    def connect(**kwargs):
        if kwargs["user"] == "postgres." + SETUP.PROJECT:
            return CommitFailure(True) if failure == "commit" else Connection(True)
        raise OSError("PUBLIC_SYNTHETIC_LOGIN_FAILURE")

    with pytest.raises(OSError):
        SETUP.configure(PUBLIC_ADMIN, connect=connect, output=output)
    assert output.exists() and output.stat().st_mode & 0o777 == 0o600
    with pytest.raises(SETUP.SetupUnavailable):
        SETUP.configure(PUBLIC_ADMIN, connect=lambda **kwargs: pytest.fail(), output=output)


def test_main_never_prints_failure_values_and_removes_inherited_pg(tmp_path, monkeypatch, capsys):
    import logging

    import psycopg

    source = private_file(tmp_path, SETUP.NAME + "=" + PUBLIC_ADMIN + "\n")
    monkeypatch.setattr(SETUP, "INPUT", source)
    monkeypatch.setattr(SETUP.sys, "argv", ["configure_identity_database_password.py"])
    monkeypatch.setenv("PGPASSWORD", "PUBLIC_SYNTHETIC_INHERITED")
    monkeypatch.setenv("PGSERVICE", "PUBLIC_SYNTHETIC_SERVICE")

    def fail_connect(**kwargs):
        assert not any(name.startswith("PG") for name in SETUP.os.environ)
        raise OSError(PUBLIC_ADMIN)

    monkeypatch.setattr(psycopg, "connect", fail_connect)
    previous = logging.root.manager.disable
    try:
        assert SETUP.main() == 2
    finally:
        logging.disable(previous)
    output = capsys.readouterr()
    assert output.err == ""
    assert output.out == '{"status": "setup_unavailable", "diagnostics": "suppressed"}\n'


def test_generated_conninfo_matches_approved_runtime_contract(tmp_path):
    from psycopg.conninfo import conninfo_to_dict

    from abogalia_api.identity.runtime import validate_dsn

    output = tmp_path / "runtime"
    SETUP.write_runtime_file(output, PUBLIC_RUNTIME)
    name, dsn = output.read_text().strip().split("=", 1)
    assert name == "ABOGALIA_DATABASE_DSN"
    validate_dsn(dsn, SETUP.ROLE)
    assert conninfo_to_dict(dsn)["sslrootcert"] == str(SETUP.CA)


pytest_plugins = ["storage_fixtures"]


def test_role_membership_guard_against_real_isolated_postgresql(isolated_database):
    import os

    import psycopg

    with psycopg.connect(
        isolated_database.admin_dsn, password="", passfile=os.devnull, autocommit=True
    ) as conn:
        assert conn.execute(SETUP.ROLE_SAFETY_SQL, (SETUP.ROLE,)).fetchone() == (True,)
        conn.execute("GRANT pg_read_all_data TO abogalia_identity_runtime")
        try:
            assert conn.execute(SETUP.ROLE_SAFETY_SQL, (SETUP.ROLE,)).fetchone() == (False,)
        finally:
            conn.execute("REVOKE pg_read_all_data FROM abogalia_identity_runtime")
        assert conn.execute(SETUP.ROLE_SAFETY_SQL, (SETUP.ROLE,)).fetchone() == (True,)
