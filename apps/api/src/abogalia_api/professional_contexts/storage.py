"""Private inactive drafts on the verified Identity business savepoint only."""

from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import UUID, uuid4

import psycopg
from psycopg.pq import TransactionStatus
from psycopg.rows import dict_row, tuple_row

from abogalia_api.identity.contracts import Clock, StorageUnavailable
from abogalia_api.identity.storage import _require_role
from abogalia_api.professional_contexts.domain import (
    DomainError,
    DraftAggregate,
    DraftFields,
    Practice,
    Profile,
    create_draft,
    edit_draft,
    withdraw_draft,
)


class PostgresProfessionalContextStore:
    """No DSN, new connection or commit; the caller owns Auth's final frontier."""

    def __init__(self, conn: psycopg.Connection, *, subject: str, clock: Clock | None = None):
        self._conn = conn
        self._clock = clock or (lambda: datetime.now(UTC))
        try:
            self._subject = UUID(subject)
            if self._subject.int == 0 or str(self._subject) != subject:
                raise ValueError
        except (ValueError, TypeError, AttributeError):
            raise StorageUnavailable from None
        with self._operation():
            self._check()

    def _check(self):
        if self._conn.closed or self._conn.info.transaction_status != TransactionStatus.INTRANS:
            raise StorageUnavailable
        _require_role(self._conn, "abogalia_identity_runtime")
        with self._conn.cursor(row_factory=tuple_row) as cursor:
            value = cursor.execute("SELECT current_setting('abogalia.subject', true)").fetchone()
            if value is None or value[0] != str(self._subject):
                raise StorageUnavailable

    @contextmanager
    def _operation(self):
        try:
            yield
        except psycopg.Error:
            raise StorageUnavailable from None

    def _load(self) -> DraftAggregate | None:
        self._check()
        with self._conn.cursor(row_factory=dict_row) as cursor:
            row = cursor.execute(
                "SELECT * FROM identity.professional_drafts WHERE owner_user_id = %s FOR UPDATE",
                (self._subject,),
            ).fetchone()
        if row is None:
            return None
        try:
            return DraftAggregate(
                Profile(
                    row["profile_id"],
                    row["owner_user_id"],
                    DraftFields(row["display_name"], row["declared_area"]),
                    row["profile_state"],
                    row["profile_version"],
                    row["created_at"],
                    row["profile_updated_at"],
                    row["withdrawn_at"],
                ),
                Practice(
                    row["context_id"],
                    row["owner_user_id"],
                    row["profile_id"],
                    row["kind"],
                    row["context_state"],
                    row["context_version"],
                    row["created_at"],
                    row["context_updated_at"],
                    row["closed_at"],
                ),
            )
        except (DomainError, KeyError, TypeError, ValueError):
            raise StorageUnavailable from None

    def read(self) -> DraftAggregate | None:
        with self._operation():
            return self._load()

    def _events(self, events):
        for event in events:
            self._conn.execute(
                "INSERT INTO identity.professional_events "
                "(actor_user_id, profile_id, context_id, transition, occurred_at, "
                "profile_version, context_version) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (
                    event.actor_user_id,
                    event.profile_id,
                    event.context_id,
                    event.transition,
                    event.occurred_at,
                    event.profile_version,
                    event.context_version,
                ),
            )

    def create(self, fields: DraftFields) -> DraftAggregate:
        with self._operation():
            self._check()
            # Common lock with Identity creation/revocation and competing creates.
            with self._conn.cursor(row_factory=tuple_row) as cursor:
                user = cursor.execute(
                    "SELECT state FROM identity.users WHERE subject = %s FOR UPDATE",
                    (self._subject,),
                ).fetchone()
                if user is None or user[0] != "active":
                    raise DomainError("RESOURCE_UNAVAILABLE")
            if self._load() is not None:
                raise DomainError("STATE_CONFLICT")
            transition = create_draft(
                actor_user_id=self._subject,
                profile_id=uuid4(),
                context_id=uuid4(),
                fields=fields,
                now=self._clock(),
            )
            profile, practice = transition.aggregate.profile, transition.aggregate.practice
            self._conn.execute(
                "INSERT INTO identity.professional_drafts "
                "(profile_id, owner_user_id, context_id, kind, display_name, declared_area, "
                "profile_state, context_state, profile_version, context_version, created_at, "
                "profile_updated_at, context_updated_at) VALUES "
                "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    profile.profile_id,
                    profile.owner_user_id,
                    practice.context_id,
                    practice.kind,
                    profile.fields.display_name,
                    profile.fields.declared_area,
                    profile.state,
                    practice.state,
                    profile.profile_version,
                    practice.context_version,
                    profile.created_at,
                    profile.updated_at,
                    practice.updated_at,
                ),
            )
            self._events(transition.events)
            return transition.aggregate

    def _save(self, original, transition):
        if not transition.events:
            return transition.aggregate
        profile, practice = transition.aggregate.profile, transition.aggregate.practice
        updated = self._conn.execute(
            "UPDATE identity.professional_drafts SET display_name=%s, declared_area=%s, "
            "profile_state=%s, context_state=%s, profile_version=%s, context_version=%s, "
            "profile_updated_at=%s, context_updated_at=%s, withdrawn_at=%s, closed_at=%s "
            "WHERE owner_user_id=%s AND profile_version=%s AND context_version=%s",
            (
                profile.fields.display_name,
                profile.fields.declared_area,
                profile.state,
                practice.state,
                profile.profile_version,
                practice.context_version,
                profile.updated_at,
                practice.updated_at,
                profile.withdrawn_at,
                practice.closed_at,
                self._subject,
                original.profile.profile_version,
                original.practice.context_version,
            ),
        )
        if updated.rowcount != 1:
            raise DomainError("VERSION_CONFLICT")
        self._events(transition.events)
        return transition.aggregate

    def edit(self, fields: DraftFields, *, expected_version: int) -> DraftAggregate:
        with self._operation():
            original = self._load()
            if original is None:
                raise DomainError("RESOURCE_UNAVAILABLE")
            return self._save(
                original,
                edit_draft(
                    original,
                    actor_user_id=self._subject,
                    expected_version=expected_version,
                    fields=fields,
                    now=self._clock(),
                ),
            )

    def withdraw(self, *, expected_version: int, expected_context_version: int) -> DraftAggregate:
        with self._operation():
            original = self._load()
            if original is None:
                raise DomainError("RESOURCE_UNAVAILABLE")
            return self._save(
                original,
                withdraw_draft(
                    original,
                    actor_user_id=self._subject,
                    expected_version=expected_version,
                    expected_context_version=expected_context_version,
                    now=self._clock(),
                ),
            )
