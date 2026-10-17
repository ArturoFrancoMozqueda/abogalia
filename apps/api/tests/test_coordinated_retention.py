"""Coordinated retention against real isolated PostgreSQL; no provider evidence."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from uuid import uuid4

import psycopg
import pytest
from test_identity_retention_runner import runner, source_env
from test_professional_contexts_storage import actor_connection, create, record

from abogalia_api.identity.contracts import StorageUnavailable
from abogalia_api.identity.storage import PostgresIdentityMaintenance
from abogalia_api.professional_contexts.domain import DraftFields
from abogalia_api.professional_contexts.storage import PostgresProfessionalContextStore

pytest_plugins = ["storage_fixtures", "test_professional_contexts_storage"]


def connect(database):
    return psycopg.connect(database.admin_dsn, passfile=os.devnull, password="", autocommit=True)


def maintenance(database, clock):
    return PostgresIdentityMaintenance(database.maintenance_dsn, clock)


def close(database, subject, when):
    with connect(database) as conn:
        conn.execute(
            "UPDATE identity.users SET state='closed',closed_at=%s WHERE subject=%s",
            (when, subject),
        )


def totals(database):
    with connect(database) as conn:
        return conn.execute(
            "SELECT (SELECT count(*) FROM identity.users),"
            "(SELECT count(*) FROM identity.app_sessions),"
            "(SELECT count(*) FROM identity.audit),"
            "(SELECT count(*) FROM identity.professional_drafts),"
            "(SELECT count(*) FROM identity.professional_events)"
        ).fetchone()


@pytest.mark.parametrize("apply", [False, True])
def test_absent_schema_explicit_failure_before_any_cleanup(isolated_database, store, clock, apply):
    record(store, clock)
    clock.now += timedelta(days=100)
    with pytest.raises(StorageUnavailable):
        maintenance(isolated_database, clock).purge(retired_subjects=set())
    args = ["--apply", "--isolated-local"] if apply else []
    report, code = runner.run(args, environ=source_env(), clock=clock)
    assert code == 2 and report == {
        "status": "professional_schema_unavailable",
        "professional_schema": "absent",
        "diagnostics": "suppressed",
    }
    with connect(isolated_database) as conn:
        assert conn.execute("SELECT count(*) FROM identity.app_sessions").fetchone() == (1,)
        assert conn.execute("SELECT count(*) FROM identity.audit").fetchone() == (1,)


def test_partial_schema_explicit_failure_no_writes(professional_database, store, clock):
    db = professional_database
    value = record(store, clock)
    create(db, value.subject, clock)
    before = totals(db)
    with connect(db) as conn:
        conn.execute("ALTER TABLE identity.professional_events RENAME TO retention_hidden_events")
        try:
            with pytest.raises(StorageUnavailable):
                maintenance(db, clock).purge(retired_subjects=set())
            report, code = runner.run(
                ["--apply", "--isolated-local"], environ=source_env(), clock=clock
            )
            assert code == 2 and report["professional_schema"] == "partial"
        finally:
            conn.execute(
                "ALTER TABLE identity.retention_hidden_events RENAME TO professional_events"
            )
    assert totals(db) == before


def test_exact_30_90_boundaries_preview_is_read_only_apply_idempotent(
    professional_database, store, clock, monkeypatch
):
    db, now = professional_database, clock()
    values = []
    for index, delta in enumerate((-1, 0, 1)):
        clock.now = now - timedelta(days=30) + timedelta(microseconds=delta)
        value = record(store, clock, str(index))
        values.append(value)
        create(db, value.subject, clock)
    clock.now = now
    with connect(db) as conn:
        for delta in (-1, 0, 1):
            conn.execute(
                "INSERT INTO identity.professional_events "
                "(actor_user_id,profile_id,context_id,transition,occurred_at,"
                "profile_version,context_version) "
                "VALUES (%s,%s,%s,'draft_created',%s,1,1)",
                (
                    uuid4(),
                    uuid4(),
                    uuid4(),
                    now - timedelta(days=90) + timedelta(microseconds=delta),
                ),
            )
    before = totals(db)
    execute = psycopg.Connection.execute
    writes = []

    def observe(conn, query, *args, **kwargs):
        if isinstance(query, str) and query.startswith("SELECT count(*) FROM identity."):
            assert execute(conn, "SHOW transaction_read_only").fetchone() == ("on",)
        if isinstance(query, str) and query.startswith(("DELETE", "UPDATE", "INSERT")):
            writes.append(True)
        return execute(conn, query, *args, **kwargs)

    monkeypatch.setattr(psycopg.Connection, "execute", observe)
    report, code = runner.run([], environ=source_env(), clock=clock)
    monkeypatch.setattr(psycopg.Connection, "execute", execute)
    assert code == 0 and not writes and totals(db) == before
    assert report["counts"]["professional_drafts"] == 2
    assert report["counts"]["professional_events"] == 2
    report, code = runner.run(["--apply", "--isolated-local"], environ=source_env(), clock=clock)
    assert code == 0 and report["counts"]["professional_drafts"] == 2
    assert report["counts"]["professional_events"] == 2
    assert totals(db)[3:] == (1, 4)  # Three newer creation events plus one at90d-1us.
    again = maintenance(db, clock).purge(retired_subjects=set())
    assert again.professional_drafts == again.professional_events == 0


def test_withdrawal_cutoff_does_not_use_old_creation_date(professional_database, store, clock):
    db, now = professional_database, clock()
    clock.now -= timedelta(days=100)
    value = record(store, clock)
    create(db, value.subject, clock)
    clock.now = now - timedelta(days=29)
    with actor_connection(db, value.subject) as conn:
        scoped = PostgresProfessionalContextStore(conn, subject=value.subject, clock=clock)
        withdrawn = scoped.withdraw(expected_version=1, expected_context_version=1)
    clock.now = now
    assert maintenance(db, clock).purge(retired_subjects=set()).professional_drafts == 0
    clock.now = withdrawn.profile.withdrawn_at + timedelta(days=30)
    assert maintenance(db, clock).purge(retired_subjects=set()).professional_drafts == 1
    assert totals(db)[4] == 1  # Recent withdrawal event remains for90d.


def test_missing_proof_never_deletes_account_but_due_profile_and_custody_are_cleaned(
    professional_database, store, clock
):
    db = professional_database
    value = record(store, clock)
    create(db, value.subject, clock)
    close(db, value.subject, clock())
    clock.now += timedelta(days=30)
    result = maintenance(db, clock).purge(retired_subjects=set())
    assert result.professional_drafts == 1 and result.sessions == 1
    assert (
        result.accounts == 0
        and result.blocked_accounts == result.blocked_accounts_missing_proof == 1
    )
    assert not result.retention_compliant and totals(db)[3:] == (0, 1)
    with connect(db) as conn:
        assert conn.execute(
            "SELECT state FROM identity.users WHERE subject=%s", (value.subject,)
        ).fetchone() == ("closed",)
    report, code = runner.run(["--apply", "--isolated-local"], environ=source_env(), clock=clock)
    assert code == 3 and report["counts"]["accounts"] == 0


def test_confirmed_synthetic_account_recent_profile_blocks_without_rolling_back_other_cleanup(
    professional_database, store, clock
):
    db = professional_database
    value = record(store, clock)
    other = record(store, clock, "other")
    # Synthetic recent dependent data models a closure path that was not coordinated.
    clock.now += timedelta(days=29)
    create(db, value.subject, clock)
    close(db, value.subject, clock() - timedelta(days=29))
    clock.now += timedelta(days=1)
    with connect(db) as conn:
        conn.execute(
            "INSERT INTO identity.audit(subject,action,occurred_at) "
            "VALUES (%s,'session_deleted',%s)",
            (other.subject, clock() - timedelta(days=90)),
        )
    result = maintenance(db, clock).purge(retired_subjects={value.subject})
    assert result.accounts == 0 and result.blocked_accounts == 1
    assert result.blocked_accounts_dependencies == 1 and result.blocked_accounts_missing_proof == 0
    assert result.sessions == 2 and result.audit_events == 1 and not result.retention_compliant
    assert totals(db)[1] == 0 and totals(db)[3] == 1


def test_unexpected_fk_only_blocks_one_account_preserves_prior_cleanup(
    professional_database, store, clock
):
    db = professional_database
    a, b = record(store, clock), record(store, clock, "other")
    create(db, a.subject, clock)
    close(db, a.subject, clock())
    close(db, b.subject, clock())
    clock.now += timedelta(days=100)
    with connect(db) as conn:
        conn.execute(
            "CREATE TABLE identity.retention_synthetic_dependency "
            "(subject uuid REFERENCES identity.users(subject) ON DELETE RESTRICT)"
        )
        conn.execute(
            "INSERT INTO identity.retention_synthetic_dependency VALUES (%s)", (a.subject,)
        )
        try:
            result = maintenance(db, clock).purge(retired_subjects={a.subject, b.subject})
            assert result.sessions == 2 and result.audit_events == 2
            assert result.professional_events == result.professional_drafts == 1
            assert result.accounts == 1 and result.blocked_accounts_dependencies == 1
            assert result.blocked_accounts == 1 and not result.retention_compliant
            assert totals(db) == (1, 0, 0, 0, 0)
        finally:
            conn.execute("DROP TABLE identity.retention_synthetic_dependency")
    again = maintenance(db, clock).purge(retired_subjects={a.subject})
    assert again.accounts == 1 and again.retention_compliant
    assert maintenance(db, clock).purge(retired_subjects=set()).accounts == 0


def test_pending_edit_wins_cutoff_recheck_without_deadlock(
    professional_database, store, clock, monkeypatch
):
    db = professional_database
    value = record(store, clock)
    create(db, value.subject, clock)
    clock.now += timedelta(days=30)
    with connect(db) as conn:
        conn.execute("DELETE FROM identity.app_sessions WHERE subject=%s", (value.subject,))
    worker_waiting = Event()
    execute = psycopg.Connection.execute

    def observe(conn, query, *args, **kwargs):
        if isinstance(query, str) and query.startswith("SELECT u.subject FROM identity.users u"):
            worker_waiting.set()
        return execute(conn, query, *args, **kwargs)

    monkeypatch.setattr(psycopg.Connection, "execute", observe)

    # Keep executor outside the editing transaction so shutdown cannot wait under lock.
    with ThreadPoolExecutor(max_workers=1) as pool:
        with actor_connection(db, value.subject) as conn:
            conn.execute(
                "SELECT subject FROM identity.users WHERE subject=%s FOR UPDATE", (value.subject,)
            )
            future = pool.submit(maintenance(db, clock).purge, retired_subjects=set())
            assert worker_waiting.wait(5)
            updated = PostgresProfessionalContextStore(
                conn, subject=value.subject, clock=clock
            ).edit(DraftFields("PUBLIC_REAL_EDIT"), expected_version=1)
            assert updated.profile.profile_version == 2
        result = future.result(timeout=10)
    assert result.professional_drafts == 0 and totals(db)[3] == 1
