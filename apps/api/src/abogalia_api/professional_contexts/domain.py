"""Private inactive C03 aggregate only; no Auth, persistence, HTTP or permissions."""

import unicodedata
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

DATA_RETENTION = timedelta(days=30)
EVENT_RETENTION = timedelta(days=90)


class DomainError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__("Professional draft operation unavailable")


def _reject(code="INVALID_REQUEST"):
    raise DomainError(code) from None


def _uuid(value):
    if not isinstance(value, UUID) or value.int == 0:
        _reject()
    return value


def _version(value):
    if type(value) is not int or not 1 <= value <= 2**31 - 1:
        _reject()


def _time(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _reject()
    try:
        return value.astimezone(UTC)
    except (OverflowError, ValueError):
        _reject()


def _text(value, maximum, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str) or any(unicodedata.category(char) == "Cc" for char in value):
        _reject()
    result = unicodedata.normalize("NFC", value.strip())
    try:
        result.encode("utf-8")
    except UnicodeError:
        _reject()
    if nullable and not result:
        return None
    if not 1 <= len(result) <= maximum:
        _reject()
    return result


@dataclass(frozen=True, slots=True, repr=False)
class DraftFields:
    display_name: str
    declared_area: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "display_name", _text(self.display_name, 120))
        object.__setattr__(self, "declared_area", _text(self.declared_area, 240, nullable=True))


@dataclass(frozen=True, slots=True, repr=False)
class Profile:
    profile_id: UUID
    owner_user_id: UUID
    fields: DraftFields
    state: Literal["draft", "withdrawn"]
    profile_version: int
    created_at: datetime
    updated_at: datetime
    withdrawn_at: datetime | None = None

    def __post_init__(self):
        _uuid(self.profile_id)
        _uuid(self.owner_user_id)
        _version(self.profile_version)
        if not isinstance(self.fields, DraftFields) or self.state not in ("draft", "withdrawn"):
            _reject()
        for field in ("created_at", "updated_at"):
            object.__setattr__(self, field, _time(getattr(self, field)))
        if self.withdrawn_at is not None:
            object.__setattr__(self, "withdrawn_at", _time(self.withdrawn_at))
        if (
            self.updated_at < self.created_at
            or (self.state == "withdrawn") != (self.withdrawn_at is not None)
            or (self.withdrawn_at is not None and self.withdrawn_at != self.updated_at)
        ):
            _reject()


@dataclass(frozen=True, slots=True, repr=False)
class Practice:
    context_id: UUID
    owner_user_id: UUID
    profile_id: UUID
    kind: Literal["practice"]
    state: Literal["preparing", "closed"]
    context_version: int
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

    def __post_init__(self):
        for field in ("context_id", "owner_user_id", "profile_id"):
            _uuid(getattr(self, field))
        _version(self.context_version)
        if self.kind != "practice" or self.state not in ("preparing", "closed"):
            _reject()
        for field in ("created_at", "updated_at"):
            object.__setattr__(self, field, _time(getattr(self, field)))
        if self.closed_at is not None:
            object.__setattr__(self, "closed_at", _time(self.closed_at))
        if (
            self.updated_at < self.created_at
            or (self.state == "closed") != (self.closed_at is not None)
            or (self.closed_at is not None and self.closed_at != self.updated_at)
        ):
            _reject()


@dataclass(frozen=True, slots=True, repr=False)
class Event:
    actor_user_id: UUID
    profile_id: UUID
    context_id: UUID
    transition: Literal["draft_created", "draft_edited", "draft_withdrawn"]
    occurred_at: datetime
    profile_version: int
    context_version: int

    def __post_init__(self):
        for field in ("actor_user_id", "profile_id", "context_id"):
            _uuid(getattr(self, field))
        _version(self.profile_version)
        _version(self.context_version)
        if self.transition not in ("draft_created", "draft_edited", "draft_withdrawn"):
            _reject()
        object.__setattr__(self, "occurred_at", _time(self.occurred_at))

    def retention_due(self, now: datetime) -> bool:
        return _time(now) >= self.occurred_at + EVENT_RETENTION


@dataclass(frozen=True, slots=True, repr=False)
class DraftAggregate:
    profile: Profile
    practice: Practice

    def __post_init__(self):
        if not isinstance(self.profile, Profile) or not isinstance(self.practice, Practice):
            _reject()
        if (
            self.profile.profile_id != self.practice.profile_id
            or self.profile.owner_user_id != self.practice.owner_user_id
            or self.profile.created_at != self.practice.created_at
            or (self.profile.state, self.practice.state)
            not in (("draft", "preparing"), ("withdrawn", "closed"))
            or self.profile.withdrawn_at != self.practice.closed_at
        ):
            _reject()

    @property
    def retention_deadline(self) -> datetime:
        # Preparing practice follows its draft; no orphaned indefinite context.
        return (self.profile.withdrawn_at or self.profile.updated_at) + DATA_RETENTION

    def retention_due(self, now: datetime) -> bool:
        return _time(now) >= self.retention_deadline


@dataclass(frozen=True, slots=True, repr=False)
class Transition:
    aggregate: DraftAggregate
    events: tuple[Event, ...]


def _owned(aggregate, actor_user_id):
    _uuid(actor_user_id)
    if actor_user_id != aggregate.profile.owner_user_id:
        _reject("RESOURCE_UNAVAILABLE")


def _cas(actual, expected):
    _version(expected)
    if actual != expected:
        _reject("VERSION_CONFLICT")


def _event(aggregate, transition, now):
    return Event(
        aggregate.profile.owner_user_id,
        aggregate.profile.profile_id,
        aggregate.practice.context_id,
        transition,
        now,
        aggregate.profile.profile_version,
        aggregate.practice.context_version,
    )


def create_draft(
    *, actor_user_id: UUID, profile_id: UUID, context_id: UUID, fields: DraftFields, now: datetime
) -> Transition:
    now = _time(now)
    aggregate = DraftAggregate(
        Profile(profile_id, actor_user_id, fields, "draft", 1, now, now),
        Practice(context_id, actor_user_id, profile_id, "practice", "preparing", 1, now, now),
    )
    return Transition(aggregate, (_event(aggregate, "draft_created", now),))


def read_draft(aggregate: DraftAggregate, *, actor_user_id: UUID) -> DraftAggregate:
    _owned(aggregate, actor_user_id)
    return aggregate


def edit_draft(
    aggregate: DraftAggregate,
    *,
    actor_user_id: UUID,
    expected_version: int,
    fields: DraftFields,
    now: datetime,
) -> Transition:
    _owned(aggregate, actor_user_id)
    _cas(aggregate.profile.profile_version, expected_version)
    if aggregate.profile.state != "draft":
        _reject("STATE_CONFLICT")
    now = _time(now)
    if now < aggregate.profile.updated_at or not isinstance(fields, DraftFields):
        _reject()
    if fields == aggregate.profile.fields:
        return Transition(aggregate, ())  # No-op is not an edit/retention reset.
    profile = replace(
        aggregate.profile,
        fields=fields,
        profile_version=aggregate.profile.profile_version + 1,
        updated_at=now,
    )
    result = DraftAggregate(profile, aggregate.practice)
    return Transition(result, (_event(result, "draft_edited", now),))


def withdraw_draft(
    aggregate: DraftAggregate,
    *,
    actor_user_id: UUID,
    expected_version: int,
    expected_context_version: int,
    now: datetime,
) -> Transition:
    _owned(aggregate, actor_user_id)
    _cas(aggregate.profile.profile_version, expected_version)
    _cas(aggregate.practice.context_version, expected_context_version)
    now = _time(now)
    if now < max(aggregate.profile.updated_at, aggregate.practice.updated_at):
        _reject()
    if aggregate.profile.state == "withdrawn":
        return Transition(aggregate, ())
    profile = replace(
        aggregate.profile,
        state="withdrawn",
        withdrawn_at=now,
        updated_at=now,
        profile_version=aggregate.profile.profile_version + 1,
    )
    practice = replace(
        aggregate.practice,
        state="closed",
        closed_at=now,
        updated_at=now,
        context_version=aggregate.practice.context_version + 1,
    )
    result = DraftAggregate(profile, practice)
    return Transition(result, (_event(result, "draft_withdrawn", now),))
