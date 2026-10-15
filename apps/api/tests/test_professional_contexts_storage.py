"""Real PostgreSQL runtime ownership/CAS/savepoint tests; synthetic data only."""

import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from threading import Event

import psycopg
import pytest

from abogalia_api.identity.contracts import StorageUnavailable
from abogalia_api.professional_contexts.domain import DomainError, DraftFields
from abogalia_api.professional_contexts.storage import PostgresProfessionalContextStore

pytest_plugins = ["storage_fixtures"]


@pytest.fixture
def professional_database(isolated_database):
    migrations = list(
        (Path(__file__).parents[3] / "supabase/migrations").glob("*professional_private_drafts.sql")
    )
    assert len(migrations) == 1
    with psycopg.connect(
        isolated_database.admin_dsn, passfile=os.devnull, password="", autocommit=True
    ) as conn:
        conn.execute(migrations[0].read_text())
    try:
        yield isolated_database
    finally:
        with psycopg.connect(
            isolated_database.admin_dsn, passfile=os.devnull, password="", autocommit=True
        ) as conn:
            conn.execute("DROP TABLE identity.professional_events, identity.professional_drafts")


@contextmanager
def actor_connection(database, subject):
    with psycopg.connect(
        database.runtime_dsn, passfile=os.devnull, password="", autocommit=True
    ) as conn:
        with conn.transaction():
            conn.execute("SELECT set_config('abogalia.subject', %s, true)", (subject,))
            yield conn


def record(store, clock, suffix="draft"):
    from storage_fixtures import make_record

    value = make_record(clock, suffix=suffix)
    store.create(value)
    return value


def create(database, subject, clock):
    with actor_connection(database, subject) as conn:
        return PostgresProfessionalContextStore(conn, subject=subject, clock=clock).create(
            DraftFields("PUBLIC_SYNTHETIC_PRIVATE", "PUBLIC_AREA")
        )


def counts(database):
    with psycopg.connect(database.admin_dsn, passfile=os.devnull, password="") as conn:
        return conn.execute(
            "SELECT (SELECT count(*) FROM identity.professional_drafts), "
            "(SELECT count(*) FROM identity.professional_events)"
        ).fetchone()


def test_real_runtime_private_grants_force_rls_and_minimal_events(
    professional_database, store, clock
):
    db = professional_database
    value = record(store, clock)
    aggregate = create(db, value.subject, clock)
    assert aggregate.profile.state == "draft" and aggregate.practice.state == "preparing"
    with psycopg.connect(db.admin_dsn, passfile=os.devnull, password="") as conn:
        rows = conn.execute(
            "SELECT relrowsecurity AND relforcerowsecurity, "
            "pg_get_userbyid(relowner)='abogalia_identity_owner' FROM pg_class "
            "WHERE oid IN ('identity.professional_drafts'::regclass, "
            "'identity.professional_events'::regclass)"
        ).fetchall()
        assert rows == [(True, True), (True, True)]
        event = conn.execute("SELECT * FROM identity.professional_events").fetchone()
        assert "PUBLIC_SYNTHETIC_PRIVATE" not in str(event) and "PUBLIC_AREA" not in str(event)
        assert conn.execute(
            "SELECT has_schema_privilege('abogalia_identity_probe','identity','USAGE')"
        ).fetchone() == (False,)
    with actor_connection(db, value.subject) as conn:
        for command in (
            "SELECT * FROM identity.professional_events",
            "DELETE FROM identity.professional_drafts",
            "TRUNCATE identity.professional_drafts",
            "UPDATE identity.professional_drafts SET owner_user_id=owner_user_id",
            "UPDATE identity.professional_drafts SET context_id=context_id",
            "UPDATE identity.professional_drafts SET kind=kind",
            "UPDATE identity.professional_drafts SET created_at=created_at",
            "UPDATE identity.professional_events SET transition=transition",
        ):
            with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
                conn.execute(command)


def test_missing_or_foreign_subject_has_no_rows_or_mutations(professional_database, store, clock):
    db = professional_database
    a, b = record(store, clock), record(store, clock, "other")
    aggregate = create(db, a.subject, clock)
    with psycopg.connect(db.runtime_dsn, passfile=os.devnull, password="", autocommit=True) as conn:
        assert conn.execute("SELECT count(*) FROM identity.professional_drafts").fetchone() == (0,)
        with pytest.raises(StorageUnavailable):
            PostgresProfessionalContextStore(conn, subject=a.subject)
    with actor_connection(db, b.subject) as conn:
        scoped = PostgresProfessionalContextStore(conn, subject=b.subject, clock=clock)
        assert scoped.read() is None
        with pytest.raises(DomainError) as error:
            scoped.edit(DraftFields("PUBLIC_FOREIGN"), expected_version=1)
        assert error.value.code == "RESOURCE_UNAVAILABLE"
        assert (
            conn.execute(
                "UPDATE identity.professional_drafts SET display_name='PUBLIC_FOREIGN' "
                "WHERE profile_id=%s",
                (aggregate.profile.profile_id,),
            ).rowcount
            == 0
        )
        with pytest.raises(StorageUnavailable):
            PostgresProfessionalContextStore(conn, subject=a.subject)
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            conn.execute(
                "INSERT INTO identity.professional_events "
                "(actor_user_id,profile_id,context_id,transition,occurred_at,"
                "profile_version,context_version) "
                "VALUES (%s,%s,%s,'draft_edited',%s,1,1)",
                (b.subject, aggregate.profile.profile_id, aggregate.practice.context_id, clock()),
            )
    assert counts(db) == (1, 1)


def test_context_switch_and_reuse_cannot_retain_old_actor(professional_database, store, clock):
    db = professional_database
    a, b = record(store, clock), record(store, clock, "other")
    create(db, a.subject, clock)
    with psycopg.connect(db.runtime_dsn, passfile=os.devnull, password="", autocommit=True) as conn:
        with conn.transaction():
            conn.execute("SELECT set_config('abogalia.subject',%s,true)", (a.subject,))
            scoped = PostgresProfessionalContextStore(conn, subject=a.subject, clock=clock)
            assert scoped.read() is not None
            conn.execute("SELECT set_config('abogalia.subject',%s,true)", (b.subject,))
            with pytest.raises(StorageUnavailable):
                scoped.read()
            assert PostgresProfessionalContextStore(conn, subject=b.subject).read() is None
        with conn.transaction():
            with pytest.raises(StorageUnavailable):
                scoped.read()
            assert conn.execute("SELECT count(*) FROM identity.professional_drafts").fetchone() == (
                0,
            )


def test_edit_cas_noop_and_withdraw_two_versions_atomic(professional_database, store, clock):
    db = professional_database
    value = record(store, clock)
    initial = create(db, value.subject, clock)
    clock.now += timedelta(days=1)
    with actor_connection(db, value.subject) as conn:
        scoped = PostgresProfessionalContextStore(conn, subject=value.subject, clock=clock)
        noop = scoped.edit(initial.profile.fields, expected_version=1)
        assert noop.profile.updated_at == initial.profile.updated_at
        edited = scoped.edit(DraftFields("PUBLIC_EDITED"), expected_version=1)
        assert edited.profile.profile_version == 2 and edited.practice.context_version == 1
        for kwargs in (
            dict(expected_version=1, expected_context_version=1),
            dict(expected_version=2, expected_context_version=2),
        ):
            with pytest.raises(DomainError) as error:
                scoped.withdraw(**kwargs)
            assert error.value.code == "VERSION_CONFLICT"
            assert scoped.read().profile.state == "draft"
        final = scoped.withdraw(expected_version=2, expected_context_version=1)
        assert final.profile.state == "withdrawn" and final.practice.state == "closed"
        assert final.profile.withdrawn_at == final.practice.closed_at
        assert final.profile.profile_version == 3 and final.practice.context_version == 2
        clock.now += timedelta(days=10)
        retry = scoped.withdraw(expected_version=3, expected_context_version=2)
        assert retry.profile.updated_at == final.profile.updated_at
        with pytest.raises(DomainError):
            scoped.create(DraftFields("PUBLIC_RECREATE"))
        with pytest.raises(DomainError):
            scoped.edit(DraftFields("PUBLIC_REOPEN"), expected_version=3)
    assert counts(db) == (1, 3)


@pytest.mark.parametrize(
    "update",
    [
        "profile_state='withdrawn'",
        "context_state='closed'",
        "profile_version=0",
        "context_version=0",
        "display_name=''",
        "declared_area=repeat('x',241)",
    ],
)
def test_constraints_reject_half_withdrawal_and_invalid_values(
    professional_database, store, clock, update
):
    db = professional_database
    value = record(store, clock)
    create(db, value.subject, clock)
    with actor_connection(db, value.subject) as conn:
        with pytest.raises(psycopg.errors.CheckViolation), conn.transaction():
            conn.execute("UPDATE identity.professional_drafts SET " + update)
    assert counts(db) == (1, 1)


def test_business_savepoint_rollback_preserves_outer_custody_rotation(
    professional_database, store, clock
):
    db = professional_database
    value = record(store, clock)
    with store.transaction(value.digest) as tx:
        rotated = replace(
            tx.record, access_token="PUBLIC_NEW_ACCESS", refresh_token="PUBLIC_NEW_REFRESH"
        )
        tx.save(rotated)
        with pytest.raises(DomainError), tx.business() as conn:
            scoped = PostgresProfessionalContextStore(conn, subject=value.subject, clock=clock)
            scoped.create(DraftFields("PUBLIC_ROLLED_BACK"))
            raise DomainError("STATE_CONFLICT")
    assert counts(db) == (0, 0)
    with store.transaction(value.digest) as tx:
        assert tx.record.refresh_token == "PUBLIC_NEW_REFRESH"


def test_owner_role_and_completed_identity_unit_rejected(professional_database, store, clock):
    db = professional_database
    value = record(store, clock)
    with psycopg.connect(db.maintenance_dsn, passfile=os.devnull, password="") as conn:
        conn.execute("SELECT set_config('abogalia.subject', %s, true)", (value.subject,))
        with pytest.raises(StorageUnavailable) as error:
            PostgresProfessionalContextStore(conn, subject=value.subject)
        assert str(error.value) == ""
    with store.transaction(value.digest) as tx:
        with tx.business() as conn:
            scoped = PostgresProfessionalContextStore(conn, subject=value.subject, clock=clock)
            assert scoped.read() is None
    with pytest.raises(StorageUnavailable):
        scoped.read()
    with pytest.raises(StorageUnavailable), tx.business():
        pass


def test_closed_user_cannot_create_or_be_reactivated(professional_database, store, clock):
    db = professional_database
    value = record(store, clock)
    with psycopg.connect(db.admin_dsn, passfile=os.devnull, password="") as conn:
        conn.execute(
            "UPDATE identity.users SET state='closed', closed_at=%s WHERE subject=%s",
            (clock(), value.subject),
        )
    with actor_connection(db, value.subject) as conn:
        scoped = PostgresProfessionalContextStore(conn, subject=value.subject, clock=clock)
        with pytest.raises(DomainError) as error:
            scoped.create(DraftFields("PUBLIC_CLOSED"))
        assert error.value.code == "RESOURCE_UNAVAILABLE"
    with store.transaction(value.digest) as tx:
        assert tx.record is None
    assert counts(db) == (0, 0)


def test_concurrent_edit_stale_version_cannot_overwrite(professional_database, store, clock):
    db = professional_database
    value = record(store, clock)
    create(db, value.subject, clock)
    entered, release, second_started = Event(), Event(), Event()

    def first():
        with actor_connection(db, value.subject) as conn:
            result = PostgresProfessionalContextStore(
                conn, subject=value.subject, clock=clock
            ).edit(DraftFields("PUBLIC_FIRST_EDIT"), expected_version=1)
            entered.set()
            assert release.wait(5)
            return result.profile.profile_version

    def second():
        second_started.set()
        try:
            with actor_connection(db, value.subject) as conn:
                PostgresProfessionalContextStore(conn, subject=value.subject, clock=clock).edit(
                    DraftFields("PUBLIC_STALE_EDIT"), expected_version=1
                )
        except DomainError as error:
            return error.code
        return "unexpected_success"

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(first)
        assert entered.wait(5)
        b = pool.submit(second)
        assert second_started.wait(5)
        release.set()
        assert a.result(timeout=10) == 2
        assert b.result(timeout=10) == "VERSION_CONFLICT"
    with actor_connection(db, value.subject) as conn:
        result = PostgresProfessionalContextStore(conn, subject=value.subject, clock=clock).read()
        assert result.profile.fields.display_name == "PUBLIC_FIRST_EDIT"
    assert counts(db) == (1, 2)


def test_concurrent_create_only_one_aggregate_and_event(professional_database, store, clock):
    db = professional_database
    value = record(store, clock)
    entered, release, second_started = Event(), Event(), Event()

    def first():
        with actor_connection(db, value.subject) as conn:
            result = PostgresProfessionalContextStore(
                conn, subject=value.subject, clock=clock
            ).create(DraftFields("PUBLIC_FIRST"))
            entered.set()
            assert release.wait(5)
            return result.profile.profile_id

    def second():
        second_started.set()
        try:
            create(db, value.subject, clock)
        except DomainError as error:
            return error.code
        return "unexpected_success"

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(first)
        assert entered.wait(5)
        b = pool.submit(second)
        assert second_started.wait(5)
        release.set()
        assert a.result(timeout=10)
        assert b.result(timeout=10) == "STATE_CONFLICT"
    assert counts(db) == (1, 1)


def test_retention_boundaries_no_cascade_account_blocked(professional_database, store, clock):
    db = professional_database
    value = record(store, clock)
    initial = create(db, value.subject, clock)
    with psycopg.connect(db.admin_dsn, passfile=os.devnull, password="") as conn:
        conn.execute("DELETE FROM identity.app_sessions WHERE subject=%s", (value.subject,))
        with pytest.raises(psycopg.errors.ForeignKeyViolation), conn.transaction():
            conn.execute("DELETE FROM identity.users WHERE subject=%s", (value.subject,))
    with psycopg.connect(db.maintenance_dsn, passfile=os.devnull, password="") as conn:
        cutoff = clock() + timedelta(days=30)
        for now, expected in ((cutoff - timedelta(microseconds=1), 0), (cutoff, 1)):
            deleted = conn.execute(
                "DELETE FROM identity.professional_drafts WHERE "
                "COALESCE(withdrawn_at,profile_updated_at)<=%s-interval '30 days'",
                (now,),
            )
            assert deleted.rowcount == expected
        assert conn.execute("SELECT count(*) FROM identity.professional_events").fetchone() == (1,)
        assert (
            conn.execute("DELETE FROM identity.users WHERE subject=%s", (value.subject,)).rowcount
            == 1
        )
        boundary = initial.profile.created_at + timedelta(days=90)
        for now, expected in ((boundary - timedelta(microseconds=1), 0), (boundary, 1)):
            assert (
                conn.execute(
                    "DELETE FROM identity.professional_events "
                    "WHERE occurred_at<=%s-interval '90 days'",
                    (now,),
                ).rowcount
                == expected
            )


def test_migration_reapply_fails_without_partial_change(professional_database):
    migration = next(
        (Path(__file__).parents[3] / "supabase/migrations").glob("*professional_private_drafts.sql")
    )
    with psycopg.connect(
        professional_database.admin_dsn, passfile=os.devnull, password="", autocommit=True
    ) as conn:
        with pytest.raises(psycopg.Error):
            conn.execute(migration.read_text())
        conn.execute("ROLLBACK")
        assert conn.execute("SELECT count(*) FROM identity.professional_drafts").fetchone() == (0,)
