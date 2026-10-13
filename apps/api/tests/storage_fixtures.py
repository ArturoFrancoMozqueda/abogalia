"""Only isolated local PostgreSQL, never a provider or password-bearing DSN."""

import hashlib
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from cryptography.fernet import Fernet
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from abogalia_api.identity.contracts import SessionRecord
from abogalia_api.identity.storage import PostgresSessionStore


@dataclass(repr=False)
class Database:
    admin_dsn: str
    runtime_dsn: str
    maintenance_dsn: str
    probe_dsn: str
    key: bytes = field(default_factory=Fernet.generate_key)


@dataclass
class TestClock:
    now: datetime = field(default_factory=lambda: datetime(2026, 10, 12, 12, tzinfo=UTC))

    def __call__(self):
        return self.now


@pytest.fixture(scope="session")
def database():
    try:
        source = os.environ.get("ABOGALIA_TEST_POSTGRES_DSN")
        if not source:
            raise ValueError
        parts = conninfo_to_dict(source)
        if (
            set(parts) != {"host", "port", "dbname", "user"}
            or not Path(parts["host"]).is_absolute()
            or not Path(parts["host"]).is_dir()
            or parts["dbname"] != "postgres"
            or parts["user"] != "abogalia_test_owner"
            or not 1024 < int(parts["port"]) < 65536
        ):
            raise ValueError
        with psycopg.connect(source, autocommit=True, passfile=os.devnull, password="") as conn:
            for role, login in (
                ("abogalia_identity_owner", False),
                ("abogalia_identity_runtime", True),
                ("abogalia_identity_probe", True),
            ):
                if not conn.execute(
                    "SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)
                ).fetchone():
                    conn.execute(
                        sql.SQL(
                            "CREATE ROLE {} {} NOSUPERUSER NOCREATEDB NOCREATEROLE "
                            "NOINHERIT NOBYPASSRLS"
                        ).format(sql.Identifier(role), sql.SQL("LOGIN" if login else "NOLOGIN"))
                    )
            exists = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = 'abogalia_storage_test'"
            ).fetchone()
            if not exists:
                conn.execute("CREATE DATABASE abogalia_storage_test OWNER abogalia_identity_owner")
        parts |= {"passfile": os.devnull, "password": ""}
        admin_dsn = make_conninfo(**(parts | {"dbname": "abogalia_storage_test"}))
        runtime_dsn = make_conninfo(
            **(parts | {"dbname": "abogalia_storage_test", "user": "abogalia_identity_runtime"})
        )
        with psycopg.connect(admin_dsn, autocommit=True, passfile=os.devnull, password="") as conn:
            present = conn.execute(
                "SELECT 1 FROM pg_namespace WHERE nspname = 'identity'"
            ).fetchone()
            if not present:
                migration = Path(__file__).parents[1] / "migrations/001_identity.sql"
                conn.execute(migration.read_text())
            if not conn.execute("SELECT to_regclass('auth.sessions')").fetchone()[0]:
                conn.execute("CREATE SCHEMA auth AUTHORIZATION abogalia_identity_owner")
                conn.execute(
                    "CREATE TABLE auth.sessions(id uuid PRIMARY KEY, user_id uuid NOT NULL, "
                    "private_marker text)"
                )
                conn.execute("REVOKE ALL ON SCHEMA auth FROM PUBLIC")
                conn.execute("REVOKE ALL ON auth.sessions FROM PUBLIC")
                conn.execute("GRANT USAGE ON SCHEMA auth TO abogalia_identity_probe")
                conn.execute(
                    "GRANT SELECT (id, user_id) ON auth.sessions TO abogalia_identity_probe"
                )
        maintenance_dsn = make_conninfo(admin_dsn, options="-c role=abogalia_identity_owner")
        probe_dsn = make_conninfo(admin_dsn, user="abogalia_identity_probe")
        yield Database(admin_dsn, runtime_dsn, maintenance_dsn, probe_dsn)
    except Exception:
        pytest.fail("Isolated PostgreSQL setup unavailable; diagnostics suppressed.", pytrace=False)


@pytest.fixture
def isolated_database(database):
    try:
        with psycopg.connect(
            database.admin_dsn, autocommit=True, passfile=os.devnull, password=""
        ) as conn:
            conn.execute(
                "TRUNCATE identity.audit, identity.app_sessions, identity.users RESTART IDENTITY"
            )
            conn.execute("TRUNCATE auth.sessions")
    except Exception:
        pytest.fail("Isolated PostgreSQL reset unavailable; diagnostics suppressed.", pytrace=False)
    return database


@pytest.fixture
def clock():
    return TestClock()


@pytest.fixture
def store(isolated_database, clock):
    return PostgresSessionStore(isolated_database.runtime_dsn, isolated_database.key, clock)


def make_record(clock, *, subject=None, suffix="one"):
    return SessionRecord(
        digest=hashlib.sha256(("public-cookie-" + suffix).encode()).hexdigest(),
        subject=subject or str(uuid4()),
        email="synthetic@example.invalid",
        provider_session_id=str(uuid4()),
        access_token="PUBLIC_SYNTHETIC_ACCESS_" + suffix,
        refresh_token="PUBLIC_SYNTHETIC_REFRESH_" + suffix,
        assurance="aal1",
        created_at=clock(),
        last_activity_at=clock(),
        token_expires_at=clock() + timedelta(minutes=15),
    )
