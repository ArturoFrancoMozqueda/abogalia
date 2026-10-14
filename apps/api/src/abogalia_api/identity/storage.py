"""Private PostgreSQL session custody. No diagnostic contains records or DSNs."""

import json
import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import psycopg
from cryptography.fernet import Fernet, InvalidToken
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row

from abogalia_api.identity.contracts import Clock, SessionRecord, StorageUnavailable

ABSOLUTE = timedelta(hours=12)
INACTIVE = timedelta(minutes=30)


def _credentials(dsn: str) -> dict[str, str]:
    if not isinstance(dsn, str) or not dsn:
        raise StorageUnavailable
    try:
        # sslcertmode exists in libpq16+. An older client must never silently
        # connect with its default client certificate/private-key selection.
        version = psycopg.pq.version()
        if type(version) is not int or version < 160000:
            raise StorageUnavailable
        return {
            "passfile": os.devnull,
            "password": conninfo_to_dict(dsn).get("password", ""),
            "sslcertmode": "disable",
        }
    except Exception:
        raise StorageUnavailable from None


def _uuid(value: str) -> str:
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise StorageUnavailable from None


def _digest(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise StorageUnavailable
    return value


def _time(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise StorageUnavailable
    return value.astimezone(UTC)


def _context(conn: psycopg.Connection, name: str, value: str) -> None:
    conn.execute("SELECT set_config(%s, %s, true)", (name, value))


def _event(conn: psycopg.Connection, subject: str, action: str, now: datetime) -> None:
    conn.execute(
        "INSERT INTO identity.audit(subject, action, occurred_at) VALUES (%s, %s, %s)",
        (subject, action, now),
    )


def _require_role(conn: psycopg.Connection, name: str) -> None:
    with conn.cursor(row_factory=dict_row) as cursor:
        role = cursor.execute(
            "SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"
        ).fetchone()
        if role is None or role["rolname"] != name or role["rolsuper"] or role["rolbypassrls"]:
            raise StorageUnavailable
        if (
            name != "abogalia_identity_owner"
            and cursor.execute(
                "SELECT pg_has_role(current_user, 'abogalia_identity_owner', 'MEMBER') AS elevated"
            ).fetchone()["elevated"]
        ):
            raise StorageUnavailable


class PostgresSessionStore:
    """Use only the private runtime role and a key injected outside this module."""

    def __init__(self, dsn: str, cipher_key: bytes, clock: Clock | None = None):
        self._dsn = dsn
        self._clock = clock or (lambda: datetime.now(UTC))
        try:
            self._cipher = Fernet(cipher_key)
        except (ValueError, TypeError):
            raise StorageUnavailable from None

    @contextmanager
    def _connection(self) -> Iterator[psycopg.Connection]:
        try:
            with psycopg.connect(
                self._dsn,
                autocommit=True,
                row_factory=dict_row,
                connect_timeout=5,
                **_credentials(self._dsn),
            ) as conn:
                with conn.transaction():
                    conn.execute("SET LOCAL statement_timeout = '10s'")
                    conn.execute("SET LOCAL lock_timeout = '5s'")
                    _require_role(conn, "abogalia_identity_runtime")
                    yield conn
        except psycopg.Error:
            raise StorageUnavailable from None

    def _validate(self, record: SessionRecord) -> None:
        _digest(record.digest)
        if _uuid(record.subject) != record.subject:
            raise StorageUnavailable
        if _uuid(record.provider_session_id) != record.provider_session_id:
            raise StorageUnavailable
        created, activity, expiry = (
            _time(record.created_at),
            _time(record.last_activity_at),
            _time(record.token_expires_at),
        )
        if not created <= activity <= _time(self._clock()) or expiry <= created:
            raise StorageUnavailable
        if record.assurance not in {"aal1", "aal2"}:
            raise StorageUnavailable
        if any(
            not isinstance(value, str) or not value or len(value.encode()) > 65_536
            for value in (record.email, record.access_token, record.refresh_token)
        ):
            raise StorageUnavailable

    def _encode(self, record: SessionRecord) -> bytes:
        # Binding prevents swapping ciphertext between subjects or session rows.
        data = {
            "digest": record.digest,
            "subject": record.subject,
            "provider_session_id": record.provider_session_id,
            "email": record.email,
            "access_token": record.access_token,
            "refresh_token": record.refresh_token,
        }
        return self._cipher.encrypt(json.dumps(data, separators=(",", ":")).encode())

    def _decode(self, row: dict) -> SessionRecord:
        try:
            data = json.loads(self._cipher.decrypt(bytes(row["secret_ciphertext"])))
            for name in ("digest", "subject", "provider_session_id"):
                if data[name] != str(row[name]):
                    raise StorageUnavailable
            record = SessionRecord(
                digest=row["digest"],
                subject=str(row["subject"]),
                email=data["email"],
                provider_session_id=str(row["provider_session_id"]),
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                assurance=row["assurance"],
                created_at=row["created_at"],
                last_activity_at=row["last_activity_at"],
                token_expires_at=row["token_expires_at"],
            )
            self._validate(record)
            return record
        except (InvalidToken, ValueError, KeyError, TypeError, UnicodeError):
            raise StorageUnavailable from None

    def _expired(self, record: SessionRecord) -> bool:
        now = _time(self._clock())
        return now >= record.created_at + ABSOLUTE or now >= record.last_activity_at + INACTIVE

    def _lock_user(self, conn: psycopg.Connection, subject: str, *, create: bool = False):
        _context(conn, "abogalia.subject", subject)
        if create:
            conn.execute(
                "INSERT INTO identity.users(subject, created_at) VALUES (%s, %s) "
                "ON CONFLICT (subject) DO NOTHING",
                (subject, _time(self._clock())),
            )
        return conn.execute(
            "SELECT state, sessions_revoked_at FROM identity.users WHERE subject = %s FOR UPDATE",
            (subject,),
        ).fetchone()

    def create(self, record: SessionRecord) -> None:
        self._validate(record)
        if self._expired(record):
            raise StorageUnavailable
        with self._connection() as conn:
            user = self._lock_user(conn, record.subject, create=True)
            if user["state"] != "active" or (
                user["sessions_revoked_at"] is not None
                and record.created_at <= user["sessions_revoked_at"]
            ):
                raise StorageUnavailable
            conn.execute(
                "INSERT INTO identity.app_sessions "
                "(digest, subject, provider_session_id, secret_ciphertext, assurance, "
                "created_at, last_activity_at, token_expires_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    record.digest,
                    record.subject,
                    record.provider_session_id,
                    self._encode(record),
                    record.assurance,
                    record.created_at,
                    record.last_activity_at,
                    record.token_expires_at,
                ),
            )
            _event(conn, record.subject, "session_created", _time(self._clock()))

    @contextmanager
    def transaction(self, digest: str) -> Iterator["_Transaction"]:
        _digest(digest)
        with self._connection() as conn:
            _context(conn, "abogalia.digest", digest)
            initial = conn.execute(
                "SELECT subject FROM identity.app_sessions WHERE digest = %s", (digest,)
            ).fetchone()
            record = None
            if initial is not None:
                subject = str(initial["subject"])
                user = self._lock_user(conn, subject)
                row = conn.execute(
                    "SELECT * FROM identity.app_sessions WHERE digest = %s FOR UPDATE", (digest,)
                ).fetchone()
                if row is not None:
                    record = self._decode(row)
                    if user is None or user["state"] != "active" or self._expired(record):
                        conn.execute(
                            "DELETE FROM identity.app_sessions WHERE digest = %s", (digest,)
                        )
                        _event(conn, subject, "session_deleted", _time(self._clock()))
                        record = None
            tx = _Transaction(self, conn, record)
            try:
                yield tx
            finally:
                tx._finished = True

    def _revoke(self, conn: psycopg.Connection, subject: str) -> None:
        self._lock_user(conn, subject, create=True)
        now = _time(self._clock())
        conn.execute(
            "UPDATE identity.users SET sessions_revoked_at = "
            "GREATEST(sessions_revoked_at, %s) WHERE subject = %s",
            (now, subject),
        )
        conn.execute("DELETE FROM identity.app_sessions WHERE subject = %s", (subject,))
        _event(conn, subject, "subject_revoked", now)

    def revoke_subject(self, subject: str) -> None:
        # The caller must obtain this principal from verified Auth, never a body/URL.
        with self._connection() as conn:
            self._revoke(conn, _uuid(subject))


class _Transaction:
    def __init__(self, store: PostgresSessionStore, conn: psycopg.Connection, record):
        self.record = record
        self._store, self._conn = store, conn
        self._finished = False
        self._digest = record.digest if record is not None else None
        self._last_activity = record.last_activity_at if record is not None else None
        self._origin = (
            (record.subject, record.provider_session_id, record.created_at)
            if record is not None
            else None
        )

    def _check(self) -> None:
        if self._finished:
            raise StorageUnavailable

    def save(self, record: SessionRecord) -> None:
        self._check()
        self._store._validate(record)
        if (
            self.record is None
            or self._origin != (record.subject, record.provider_session_id, record.created_at)
            or record.last_activity_at < self._last_activity
            or self._store._expired(record)
        ):
            raise StorageUnavailable
        result = self._conn.execute(
            "UPDATE identity.app_sessions SET digest = %s, secret_ciphertext = %s, "
            "assurance = %s, last_activity_at = %s, token_expires_at = %s WHERE digest = %s",
            (
                record.digest,
                self._store._encode(record),
                record.assurance,
                record.last_activity_at,
                record.token_expires_at,
                self._digest,
            ),
        )
        if result.rowcount != 1:
            raise StorageUnavailable
        _event(self._conn, record.subject, "session_saved", _time(self._store._clock()))
        self.record, self._digest = record, record.digest
        self._last_activity = record.last_activity_at

    def delete(self) -> None:
        self._check()
        if self.record is not None:
            self._conn.execute(
                "DELETE FROM identity.app_sessions WHERE digest = %s", (self._digest,)
            )
            _event(self._conn, self._origin[0], "session_deleted", _time(self._store._clock()))
            self.record = None

    def revoke_subject(self, subject: str) -> None:
        self._check()
        if self.record is None or _uuid(subject) != self._origin[0]:
            raise StorageUnavailable
        self._store._revoke(self._conn, subject)
        self.record = None


@dataclass(frozen=True)
class PurgeResult:
    sessions: int
    accounts: int
    audit_events: int
    blocked_accounts: int
    retention_compliant: bool


class PostgresIdentityMaintenance:
    """Separate owner-role job; account blockage never keeps expired custody or audit."""

    def __init__(self, dsn: str, clock: Clock | None = None):
        self._dsn = dsn
        self._clock = clock or (lambda: datetime.now(UTC))

    def purge(self, *, retired_subjects: set[str]) -> PurgeResult:
        retired = {_uuid(subject) for subject in retired_subjects}
        now = _time(self._clock())
        try:
            with psycopg.connect(
                self._dsn, autocommit=True, row_factory=dict_row, **_credentials(self._dsn)
            ) as conn:
                with conn.transaction():
                    conn.execute("SET LOCAL statement_timeout = '10s'")
                    conn.execute("SET LOCAL lock_timeout = '5s'")
                    _require_role(conn, "abogalia_identity_owner")
                    due = conn.execute(
                        "SELECT subject FROM identity.users WHERE state = 'closed' "
                        "AND closed_at <= %s ORDER BY subject FOR UPDATE",
                        (now - timedelta(days=30),),
                    ).fetchall()
                    subjects = {str(row["subject"]) for row in due}
                    confirmed = sorted(subjects & retired)
                    blocked = len(subjects - retired)
                    sessions = conn.execute(
                        "DELETE FROM identity.app_sessions WHERE created_at <= %s "
                        "OR last_activity_at <= %s OR subject IN "
                        "(SELECT subject FROM identity.users WHERE state != 'active')",
                        (now - ABSOLUTE, now - INACTIVE),
                    ).rowcount
                    accounts = conn.execute(
                        "DELETE FROM identity.users WHERE state = 'closed' AND closed_at <= %s "
                        "AND subject = ANY(%s::uuid[])",
                        (now - timedelta(days=30), confirmed),
                    ).rowcount
                    events = conn.execute(
                        "DELETE FROM identity.audit WHERE occurred_at <= %s",
                        (now - timedelta(days=90),),
                    ).rowcount
                    return PurgeResult(sessions, accounts, events, blocked, blocked == 0)
        except psycopg.Error:
            raise StorageUnavailable from None


class PostgresSessionProbe:
    """Dedicated read-only DSN. This module does not provision Auth permissions."""

    def __init__(self, dsn: str):
        self._dsn = dsn

    def active(self, provider_session_id: str, subject: str) -> bool:
        sid, principal = _uuid(provider_session_id), _uuid(subject)
        try:
            with psycopg.connect(
                self._dsn, autocommit=True, connect_timeout=5, **_credentials(self._dsn)
            ) as conn:
                with conn.transaction():
                    conn.execute("SET LOCAL TRANSACTION READ ONLY")
                    conn.execute("SET LOCAL statement_timeout = '5s'")
                    _require_role(conn, "abogalia_identity_probe")
                    return bool(
                        conn.execute(
                            "SELECT EXISTS (SELECT 1 FROM auth.sessions "
                            "WHERE id = %s AND user_id = %s)",
                            (sid, principal),
                        ).fetchone()[0]
                    )
        except psycopg.Error:
            raise StorageUnavailable from None
