"""Retention CLI boundaries plus actual PostgreSQL read-only/apply behavior."""

import importlib.util
import json
import os
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest

pytest_plugins = ["storage_fixtures", "test_professional_contexts_storage"]
SCRIPT = Path(__file__).parents[3] / "scripts/run_identity_retention.py"
spec = importlib.util.spec_from_file_location("identity_retention_runner", SCRIPT)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def source_env():
    return {"ABOGALIA_TEST_POSTGRES_DSN": os.environ.get("ABOGALIA_TEST_POSTGRES_DSN")}


@pytest.mark.parametrize(
    "args",
    [
        ["--apply"],
        ["--retired-subject", "public-synthetic-id"],
        ["--retired-file", "public-synthetic-file"],
        ["--dsn", "public-synthetic-config"],
        ["--appl"],
    ],
)
def test_rejects_claims_and_unconfirmed_apply_before_connection(args, monkeypatch):
    monkeypatch.setattr(runner, "local_dsn", lambda _: pytest.fail("No connection allowed"))
    report, code = runner.run(args, environ={})
    assert bool(
        code == 2 and report == {"status": "retention_runner_failed", "diagnostics": "suppressed"}
    )


@pytest.mark.parametrize(
    "source",
    [
        None,
        "host=remote.invalid port=54983 dbname=postgres user=abogalia_test_owner",
        "host=/tmp/socket port=54983 dbname=production user=abogalia_test_owner",
        "host=/tmp/socket port=54983 dbname=postgres user=abogalia_identity_runtime",
        "service=public-synthetic-config",
        "host=/tmp/socket port=54983 dbname=postgres user=abogalia_test_owner password=PUBLIC",
        "host=/tmp/socket port=54983 dbname=postgres user=abogalia_test_owner options=PUBLIC",
    ],
)
def test_invalid_destination_redacted(source):
    report, code = runner.run([], environ={"ABOGALIA_TEST_POSTGRES_DSN": source})
    assert bool(code == 2 and "PUBLIC" not in json.dumps(report))
    assert bool(set(report) == {"status", "diagnostics"})


def test_requires_private_socket_and_parent(tmp_path):
    cluster = tmp_path / "abogalia-identity-tests-synthetic"
    cluster.mkdir(mode=0o700)
    socket = cluster / "socket"
    socket.mkdir(mode=0o700)
    source = f"host={socket} port=54983 dbname=postgres user=abogalia_test_owner"
    assert bool("abogalia_storage_test" in runner.local_dsn(source))
    socket.chmod(0o755)
    with pytest.raises(runner.RetentionError):
        runner.local_dsn(source)
    socket.chmod(0o700)
    cluster.chmod(0o755)
    with pytest.raises(runner.RetentionError):
        runner.local_dsn(source)


def test_exception_details_never_returned(monkeypatch):
    def fail(_):
        raise RuntimeError("PUBLIC_SYNTHETIC_DIAGNOSTIC")

    monkeypatch.setattr(runner, "local_dsn", fail)
    report, code = runner.run([], environ={})
    assert bool(code == 2 and "PUBLIC_SYNTHETIC_DIAGNOSTIC" not in json.dumps(report))


@pytest.mark.parametrize("name", ["PGHOSTADDR", "PGSERVICE", "PGOPTIONS", "PGPASSWORD"])
def test_implicit_libpq_environment_rejected_without_reading_values(name, monkeypatch):
    monkeypatch.setenv(name, "PUBLIC_SYNTHETIC_CONFIGURATION")
    monkeypatch.setattr(runner, "local_dsn", lambda _: pytest.fail("No connection allowed"))
    report, code = runner.run([], environ={})
    assert bool(code == 2 and "PUBLIC_SYNTHETIC_CONFIGURATION" not in json.dumps(report))


def seed_due(isolated_database, store, clock):
    from storage_fixtures import make_record

    store.create(make_record(clock))
    clock.now += timedelta(minutes=30)
    with psycopg.connect(isolated_database.admin_dsn, password="", passfile=os.devnull) as conn:
        for days in (30, 29):
            conn.execute(
                "INSERT INTO identity.users(subject, state, created_at, closed_at) "
                "VALUES (%s, 'closed', %s, %s)",
                (str(uuid4()), clock() - timedelta(days=40), clock() - timedelta(days=days)),
            )
        for days in (90, 89):
            conn.execute(
                "INSERT INTO identity.audit(subject, action, occurred_at) VALUES (%s, %s, %s)",
                (str(uuid4()), "session_deleted", clock() - timedelta(days=days)),
            )


def totals(database):
    with psycopg.connect(database.admin_dsn, password="", passfile=os.devnull) as conn:
        return tuple(
            conn.execute(query).fetchone()[0]
            for query in (
                "SELECT count(*) FROM identity.app_sessions",
                "SELECT count(*) FROM identity.users",
                "SELECT count(*) FROM identity.audit",
            )
        )


def test_default_preview_read_only_exact_boundaries(
    isolated_database, store, clock, monkeypatch, professional_database
):
    seed_due(isolated_database, store, clock)
    before = totals(isolated_database)
    original = psycopg.Connection.execute
    writes = []

    def observe(conn, query, *args, **kwargs):
        if isinstance(query, str) and query.startswith("SELECT count(*) FROM identity."):
            assert bool(original(conn, "SHOW transaction_read_only").fetchone()[0] == "on")
            assert bool(
                original(conn, "SELECT current_user").fetchone()[0] == "abogalia_identity_owner"
            )
        if isinstance(query, str) and query.startswith(("DELETE", "UPDATE", "INSERT")):
            writes.append(True)
        return original(conn, query, *args, **kwargs)

    monkeypatch.setattr(psycopg.Connection, "execute", observe)
    report, code = runner.run([], environ=source_env(), clock=clock)
    monkeypatch.setattr(psycopg.Connection, "execute", original)
    assert bool(code == 0 and report["status"] == "dry_run")
    assert bool(
        report["counts"]
        == {
            "sessions": 1,
            "accounts": 0,
            "audit_events": 1,
            "blocked_accounts": 1,
            "retention_compliant": False,
            "professional_drafts": 0,
            "professional_events": 0,
            "blocked_accounts_missing_proof": 1,
            "blocked_accounts_dependencies": 0,
            "professional_schema": "ready",
        }
    )
    assert bool(not writes and totals(isolated_database) == before)


def test_apply_cleans_independently_preserves_accounts_and_idempotent(
    isolated_database, store, clock, professional_database
):
    seed_due(isolated_database, store, clock)
    report, code = runner.run(["--apply", "--isolated-local"], environ=source_env(), clock=clock)
    assert bool(code == 3 and report["status"] == "applied")
    assert bool(
        report["counts"]
        == {
            "sessions": 1,
            "accounts": 0,
            "audit_events": 1,
            "blocked_accounts": 1,
            "retention_compliant": False,
            "professional_drafts": 0,
            "professional_events": 0,
            "blocked_accounts_missing_proof": 1,
            "blocked_accounts_dependencies": 0,
            "professional_schema": "ready",
        }
    )
    assert bool(totals(isolated_database) == (0, 3, 2))
    again, code = runner.run(["--apply", "--isolated-local"], environ=source_env(), clock=clock)
    assert bool(code == 3 and again["counts"]["sessions"] == 0)
    assert bool(again["counts"]["audit_events"] == 0 and totals(isolated_database) == (0, 3, 2))


def test_empty_apply_success_without_auth_claim(isolated_database, clock, professional_database):
    report, code = runner.run(["--apply", "--isolated-local"], environ=source_env(), clock=clock)
    assert bool(code == 0 and report["counts"]["retention_compliant"])
    assert bool(report["counts"]["accounts"] == 0)
