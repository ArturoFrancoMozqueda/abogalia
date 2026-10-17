from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from threading import Event

import psycopg
import pytest
from cryptography.fernet import Fernet

from abogalia_api.identity.contracts import StorageUnavailable
from abogalia_api.identity.storage import (
    PostgresIdentityMaintenance,
    PostgresSessionProbe,
    PostgresSessionStore,
)

pytest_plugins = ["storage_fixtures", "test_professional_contexts_storage"]


def make_record(clock, **kwargs):
    # Import after pytest loads the fixture plugin, avoiding rewrite warnings.
    from storage_fixtures import make_record as factory

    return factory(clock, **kwargs)


def test_real_runtime_is_not_owner_or_bypass_and_force_rls(isolated_database):
    with psycopg.connect(isolated_database.runtime_dsn) as conn:
        row = conn.execute(
            "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"
        ).fetchone()
        assert bool(row == (False, False))
        rows = conn.execute(
            "SELECT relrowsecurity AND relforcerowsecurity, "
            "pg_get_userbyid(relowner) != current_user FROM pg_class "
            "WHERE relnamespace = 'identity'::regnamespace AND relkind = 'r'"
        ).fetchall()
        assert bool(len(rows) == 3 and all(a and b for a, b in rows))


def test_store_rejects_owner_misconfiguration_before_custody(isolated_database, clock):
    record = make_record(clock)
    for dsn in (isolated_database.admin_dsn, isolated_database.maintenance_dsn):
        with pytest.raises(StorageUnavailable) as error:
            PostgresSessionStore(dsn, isolated_database.key, clock).create(record)
        assert bool(str(error.value) == "")
    with psycopg.connect(isolated_database.admin_dsn) as conn:
        assert bool(conn.execute("SELECT count(*) FROM identity.app_sessions").fetchone()[0] == 0)


def test_ciphertext_not_plaintext_and_roundtrip(store, isolated_database, clock):
    record = make_record(clock)
    store.create(record)
    with psycopg.connect(isolated_database.admin_dsn) as conn:
        value = bytes(
            conn.execute("SELECT secret_ciphertext FROM identity.app_sessions").fetchone()[0]
        )
    assert bool(
        record.access_token.encode() not in value and record.refresh_token.encode() not in value
    )
    assert bool(record.email.encode() not in value)
    with store.transaction(record.digest) as tx:
        assert bool(tx.record is not None and tx.record.access_token == record.access_token)
    wrong = PostgresSessionStore(isolated_database.runtime_dsn, Fernet.generate_key(), clock)
    with pytest.raises(StorageUnavailable) as error, wrong.transaction(record.digest):
        pass
    assert bool(str(error.value) == "")


def test_rls_negative_missing_actor_other_subject_and_moving_row(store, isolated_database, clock):
    a, b = make_record(clock), make_record(clock, suffix="two")
    store.create(a)
    store.create(b)
    with psycopg.connect(isolated_database.runtime_dsn, autocommit=True) as conn:
        assert bool(conn.execute("SELECT count(*) FROM identity.app_sessions").fetchone()[0] == 0)
        with conn.transaction():
            conn.execute("SELECT set_config('abogalia.subject', %s, true)", (a.subject,))
            assert bool(conn.execute("SELECT count(*) FROM identity.users").fetchone()[0] == 1)
            assert bool(
                conn.execute(
                    "SELECT count(*) FROM identity.app_sessions WHERE subject = %s", (b.subject,)
                ).fetchone()[0]
                == 0
            )
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                conn.execute(
                    "UPDATE identity.app_sessions SET subject = %s WHERE digest = %s",
                    (b.subject, a.digest),
                )
        assert bool(conn.execute("SELECT count(*) FROM identity.users").fetchone()[0] == 0)
        for command in (
            "TRUNCATE identity.app_sessions",
            "SELECT * FROM identity.audit",
            "UPDATE identity.users SET state = 'active'",
            "CREATE TABLE identity.escalation(id integer)",
        ):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                conn.execute(command)


def test_rollback_rotation_delete_and_closed_transaction(store, clock):
    record = make_record(clock)
    store.create(record)
    rotated = replace(record, digest=make_record(clock, suffix="rotated").digest, assurance="aal2")
    with pytest.raises(RuntimeError), store.transaction(record.digest) as tx:
        tx.save(rotated)
        raise RuntimeError("public synthetic rollback")
    with store.transaction(record.digest) as tx:
        assert bool(tx.record is not None and tx.record.assurance == "aal1")
        tx.save(rotated)
    with pytest.raises(StorageUnavailable):
        tx.delete()
    with store.transaction(record.digest) as missing:
        assert bool(missing.record is None)
    with store.transaction(rotated.digest) as live:
        assert bool(live.record is not None and live.record.assurance == "aal2")
        live.delete()
        with pytest.raises(StorageUnavailable):
            live.save(rotated)


def test_save_cannot_change_subject_provider_or_absolute_start(store, clock):
    record = make_record(clock)
    store.create(record)
    other = make_record(clock, suffix="two")
    for changed in (
        replace(record, subject=other.subject),
        replace(record, provider_session_id=other.provider_session_id),
        replace(record, created_at=record.created_at - timedelta(seconds=1)),
    ):
        with pytest.raises(StorageUnavailable), store.transaction(record.digest) as tx:
            tx.save(changed)


@pytest.mark.parametrize("boundary", [timedelta(minutes=30), timedelta(hours=12)])
def test_expired_sessions_hard_deleted(store, clock, isolated_database, boundary):
    record = make_record(clock)
    if boundary == timedelta(hours=12):
        record = replace(
            record,
            created_at=record.created_at - timedelta(hours=12),
            token_expires_at=record.token_expires_at,
        )
    store.create(record) if boundary != timedelta(hours=12) else None
    if boundary == timedelta(hours=12):
        record = replace(record, created_at=clock() - timedelta(hours=12) + timedelta(seconds=1))
        store.create(record)
        clock.now += timedelta(seconds=1)
    else:
        clock.now += boundary
    with store.transaction(record.digest) as tx:
        assert bool(tx.record is None)
    with psycopg.connect(isolated_database.admin_dsn) as conn:
        assert bool(conn.execute("SELECT count(*) FROM identity.app_sessions").fetchone()[0] == 0)


def test_global_revoke_does_not_reintroduce_earlier_login(store, clock):
    one = make_record(clock)
    two = make_record(clock, subject=one.subject, suffix="two")
    store.create(one)
    store.create(two)
    pending = make_record(clock, subject=one.subject, suffix="pending")
    clock.now += timedelta(seconds=1)
    with store.transaction(one.digest) as tx:
        tx.revoke_subject(one.subject)
        assert bool(tx.record is None)
    for record in (one, two):
        with store.transaction(record.digest) as tx:
            assert bool(tx.record is None)
    with pytest.raises(StorageUnavailable):
        store.create(pending)
    clock.now += timedelta(seconds=1)
    fresh = make_record(clock, subject=one.subject, suffix="fresh")
    store.create(fresh)
    store.revoke_subject(one.subject)
    with store.transaction(fresh.digest) as tx:
        assert bool(tx.record is None)


def test_concurrent_refresh_serialized_by_subject_and_row(store, clock):
    record = make_record(clock)
    store.create(record)
    held, attempted, entered, release = Event(), Event(), Event(), Event()

    def first():
        with store.transaction(record.digest) as tx:
            held.set()
            if not release.wait(4):
                raise RuntimeError("public synthetic barrier timeout")
            tx.save(replace(tx.record, access_token="PUBLIC_SYNTHETIC_FIRST"))

    def second():
        attempted.set()
        with store.transaction(record.digest) as tx:
            entered.set()
            assert bool(tx.record.access_token == "PUBLIC_SYNTHETIC_FIRST")
            tx.save(replace(tx.record, access_token="PUBLIC_SYNTHETIC_SECOND"))

    with ThreadPoolExecutor(max_workers=2) as executor:
        a = executor.submit(first)
        assert held.wait(4)
        b = executor.submit(second)
        try:
            assert attempted.wait(4)
            assert not entered.wait(0.15)
        finally:
            release.set()
        a.result(timeout=6)
        b.result(timeout=6)
    with store.transaction(record.digest) as tx:
        assert bool(tx.record.access_token == "PUBLIC_SYNTHETIC_SECOND")


def test_revoke_serializes_and_refresh_cannot_resurrect(store, clock):
    record = make_record(clock)
    store.create(record)
    held, requested, release = Event(), Event(), Event()

    def refresh():
        with store.transaction(record.digest) as tx:
            held.set()
            if not release.wait(4):
                raise RuntimeError("public synthetic barrier timeout")
            tx.save(replace(tx.record, refresh_token="PUBLIC_SYNTHETIC_ROTATED"))

    def revoke():
        requested.set()
        store.revoke_subject(record.subject)

    with ThreadPoolExecutor(max_workers=2) as executor:
        a = executor.submit(refresh)
        assert held.wait(4)
        b = executor.submit(revoke)
        try:
            assert requested.wait(4)
        finally:
            release.set()
        a.result(timeout=6)
        b.result(timeout=6)
    with store.transaction(record.digest) as tx:
        assert bool(tx.record is None)


def test_closed_account_not_reactivated_and_retention_fails_without_auth_retirement(
    store, clock, isolated_database, professional_database
):
    record = make_record(clock)
    store.create(record)
    with psycopg.connect(isolated_database.admin_dsn) as conn:
        conn.execute(
            "UPDATE identity.users SET state = 'closed', closed_at = %s WHERE subject = %s",
            (clock(), record.subject),
        )
    with pytest.raises(StorageUnavailable):
        store.create(make_record(clock, subject=record.subject, suffix="closed"))
    clock.now += timedelta(days=30)
    with psycopg.connect(isolated_database.maintenance_dsn) as conn:
        assert bool(conn.execute("SELECT current_user").fetchone()[0] == "abogalia_identity_owner")
    maintenance = PostgresIdentityMaintenance(isolated_database.maintenance_dsn, clock)
    blocked = maintenance.purge(retired_subjects=set())
    assert bool(blocked.blocked_accounts == 1 and not blocked.retention_compliant)
    assert bool(blocked.sessions == 1 and blocked.accounts == 0)
    result = maintenance.purge(retired_subjects={record.subject})
    assert bool(result.accounts == 1 and result.sessions == 0 and result.audit_events == 0)
    assert bool(result.retention_compliant)
    assert bool(maintenance.purge(retired_subjects=set()).accounts == 0)
    clock.now += timedelta(days=60)
    assert bool(maintenance.purge(retired_subjects=set()).audit_events == 1)
    with pytest.raises(StorageUnavailable):
        PostgresIdentityMaintenance(isolated_database.runtime_dsn, clock).purge(
            retired_subjects=set()
        )


def test_ciphertext_binding_and_migration_reapply_fails(store, clock, isolated_database):
    a, b = make_record(clock), make_record(clock, suffix="two")
    store.create(a)
    store.create(b)
    with psycopg.connect(isolated_database.admin_dsn) as conn:
        conn.execute(
            "UPDATE identity.app_sessions SET secret_ciphertext = "
            "(SELECT secret_ciphertext FROM identity.app_sessions WHERE digest = %s) "
            "WHERE digest = %s",
            (a.digest, b.digest),
        )
    with pytest.raises(StorageUnavailable), store.transaction(b.digest):
        pass
    migration = Path(__file__).parents[1] / "migrations/001_identity.sql"
    with psycopg.connect(isolated_database.admin_dsn, autocommit=True) as conn:
        with pytest.raises(psycopg.errors.DuplicateSchema):
            conn.execute(migration.read_text())


def test_concurrent_create_waiting_for_revoke_cannot_reintroduce_session(store, clock):
    record = make_record(clock)
    store.create(record)
    pending = make_record(clock, subject=record.subject, suffix="pending")
    cutoff_set, attempting, release = Event(), Event(), Event()
    clock.now += timedelta(seconds=1)

    def revoker():
        with store.transaction(record.digest) as tx:
            tx.revoke_subject(record.subject)
            cutoff_set.set()
            if not release.wait(4):
                raise RuntimeError("public synthetic barrier timeout")

    def creator():
        attempting.set()
        try:
            store.create(pending)
        except StorageUnavailable:
            return True
        return False

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(revoker)
        assert cutoff_set.wait(4)
        second = executor.submit(creator)
        try:
            assert attempting.wait(4)
        finally:
            release.set()
        first.result(timeout=6)
        assert second.result(timeout=6)
    with store.transaction(pending.digest) as tx:
        assert bool(tx.record is None)


def test_blocked_account_does_not_retain_other_tokens_or_old_audit(
    store, clock, isolated_database, professional_database
):
    a, b = make_record(clock), make_record(clock, suffix="two")
    store.create(a)
    store.create(b)
    with psycopg.connect(isolated_database.admin_dsn) as conn:
        conn.execute(
            "UPDATE identity.users SET state = 'closed', closed_at = %s WHERE subject = %s",
            (clock(), a.subject),
        )
        conn.execute(
            "INSERT INTO identity.audit(subject, action, occurred_at) VALUES (%s, %s, %s)",
            (b.subject, "session_created", clock() - timedelta(days=90)),
        )
    clock.now += timedelta(days=30)
    result = PostgresIdentityMaintenance(isolated_database.maintenance_dsn, clock).purge(
        retired_subjects=set()
    )
    assert bool(result.sessions == 2 and result.audit_events == 1)
    assert bool(
        result.accounts == 0 and result.blocked_accounts == 1 and not result.retention_compliant
    )
    with psycopg.connect(isolated_database.admin_dsn) as conn:
        assert bool(conn.execute("SELECT count(*) FROM identity.app_sessions").fetchone()[0] == 0)
        assert bool(conn.execute("SELECT count(*) FROM identity.users").fetchone()[0] == 2)


def test_probe_sid_owner_match_and_column_only_read_role(isolated_database, clock):
    record, other = make_record(clock), make_record(clock, suffix="two")
    with psycopg.connect(isolated_database.admin_dsn) as conn:
        conn.execute(
            "INSERT INTO auth.sessions(id, user_id, private_marker) VALUES (%s, %s, %s)",
            (record.provider_session_id, record.subject, "PUBLIC_SYNTHETIC_PRIVATE_FIELD"),
        )
    probe = PostgresSessionProbe(isolated_database.probe_dsn)
    assert probe.active(record.provider_session_id, record.subject)
    assert not probe.active(record.provider_session_id, other.subject)
    assert not probe.active(other.provider_session_id, record.subject)
    with psycopg.connect(isolated_database.probe_dsn, autocommit=True) as conn:
        for command in (
            "SELECT private_marker FROM auth.sessions",
            "DELETE FROM auth.sessions",
            "SELECT * FROM identity.app_sessions",
        ):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                conn.execute(command)
    with pytest.raises(StorageUnavailable) as error:
        PostgresSessionProbe(isolated_database.runtime_dsn).active(
            record.provider_session_id, record.subject
        )
    assert bool(str(error.value) == "")
