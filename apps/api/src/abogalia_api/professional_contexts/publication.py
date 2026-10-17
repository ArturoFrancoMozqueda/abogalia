"""Pure C03 review/publication rules; no grants, identity checks, storage or live source.

Actor facts must come from the verified server boundary, never browser metadata.
A public projection is only a candidate: its caller must revalidate account,
recipient and aggregate under its authorization transaction before disclosure.
"""

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from abogalia_api.professional_contexts.domain import DomainError, DraftFields, _text

State = Literal["draft", "submitted", "enabled", "rejected", "suspended", "withdrawn"]
ContextState = Literal["preparing", "active", "suspended", "closed"]


def _fail(code="INVALID_REQUEST"):
    raise DomainError(code) from None


def _uuid(value):
    if not isinstance(value, UUID) or value.int == 0:
        _fail()
    return value


def _version(value):
    if type(value) is not int or not 1 <= value <= 2**31 - 1:
        _fail()
    return value


def _bool(value):
    if type(value) is not bool:
        _fail()
    return value


def _time(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail()
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True, repr=False)
class Declaration:
    legal_name: str
    registration_number: str

    def __post_init__(self):
        object.__setattr__(self, "legal_name", _text(self.legal_name, 200))
        number = self.registration_number
        if not isinstance(number, str) or not 1 <= len(number) <= 32:
            _fail()
        if any(char not in "0123456789" for char in number):
            _fail()


@dataclass(frozen=True, slots=True, repr=False)
class OwnerActor:
    user_id: UUID
    confirmed: bool
    assurance: str

    def __post_init__(self):
        _uuid(self.user_id)
        _bool(self.confirmed)
        if self.assurance not in ("aal1", "aal2"):
            _fail()


@dataclass(frozen=True, slots=True, repr=False)
class ReviewAuthority:
    user_id: UUID
    assigned_profile_id: UUID
    confirmed: bool
    assurance: str
    review_professionals: bool
    procedure_approved: bool

    def __post_init__(self):
        _uuid(self.user_id)
        _uuid(self.assigned_profile_id)
        for value in (self.confirmed, self.review_professionals, self.procedure_approved):
            _bool(value)
        if self.assurance not in ("aal1", "aal2"):
            _fail()


@dataclass(frozen=True, slots=True, repr=False)
class ReviewDecision:
    reviewer_user_id: UUID
    reviewed_profile_version: int
    data_version: int
    outcome: Literal["enabled", "rejected"]
    scope: Literal["registry_record_checked", "none"]
    source: Literal["official_registry"] | None
    reason_code: str
    checked_at: datetime

    def __post_init__(self):
        _uuid(self.reviewer_user_id)
        _version(self.reviewed_profile_version)
        _version(self.data_version)
        object.__setattr__(self, "checked_at", _time(self.checked_at))
        if self.outcome == "enabled":
            if (self.scope, self.source, self.reason_code) != (
                "registry_record_checked",
                "official_registry",
                "registry_record_checked",
            ):
                _fail()
        elif self.outcome == "rejected":
            if (
                self.scope != "none"
                or self.source is not None
                or self.reason_code
                not in (
                    "incomplete_declaration",
                    "registry_mismatch",
                    "identity_binding_unresolved",
                    "out_of_scope",
                )
            ):
                _fail()
        else:
            _fail()


@dataclass(frozen=True, slots=True, repr=False)
class PublicationAggregate:
    profile_id: UUID
    owner_user_id: UUID
    context_id: UUID
    public_id: UUID
    fields: DraftFields
    public_context_label: str
    declaration: Declaration | None = None
    state: State = "draft"
    context_state: ContextState = "preparing"
    profile_version: int = 1
    context_version: int = 1
    listing_version: int = 1
    data_version: int = 1
    submitted_profile_version: int | None = None
    review: ReviewDecision | None = None
    published: bool = False
    accepting_requests: bool = False
    updated_at: datetime | None = None

    def __post_init__(self):
        for value in (self.profile_id, self.owner_user_id, self.context_id, self.public_id):
            _uuid(value)
        if self.public_id in (self.profile_id, self.owner_user_id, self.context_id):
            _fail()
        if not isinstance(self.fields, DraftFields):
            _fail()
        object.__setattr__(self, "public_context_label", _text(self.public_context_label, 120))
        if self.declaration is not None and not isinstance(self.declaration, Declaration):
            _fail()
        for value in (
            self.profile_version,
            self.context_version,
            self.listing_version,
            self.data_version,
        ):
            _version(value)
        for value in (self.published, self.accepting_requests):
            _bool(value)
        if self.state not in (
            "draft",
            "submitted",
            "enabled",
            "rejected",
            "suspended",
            "withdrawn",
        ):
            _fail()
        if self.context_state not in ("preparing", "active", "suspended", "closed"):
            _fail()
        if self.updated_at is None:
            _fail()
        object.__setattr__(self, "updated_at", _time(self.updated_at))
        if self.submitted_profile_version is not None:
            _version(self.submitted_profile_version)
            if self.submitted_profile_version > self.profile_version:
                _fail()
        if self.review is not None:
            if not isinstance(self.review, ReviewDecision):
                _fail()
            if (
                self.review.reviewer_user_id == self.owner_user_id
                or self.review.data_version != self.data_version
                or self.review.reviewed_profile_version != self.submitted_profile_version
                or self.review.checked_at > self.updated_at
            ):
                _fail()
        if self.state in ("submitted", "enabled", "rejected"):
            if self.declaration is None or self.submitted_profile_version is None:
                _fail()
        if self.state in ("enabled", "rejected"):
            if self.review is None or self.review.outcome != self.state:
                _fail()
        if self.state in ("draft", "submitted") and self.review is not None:
            _fail()
        if self.state == "draft" and self.submitted_profile_version is not None:
            _fail()
        if self.context_state == "active" and self.state != "enabled":
            _fail()
        if self.state in ("draft", "submitted", "rejected") and self.context_state != "preparing":
            _fail()
        if self.state == "enabled" and self.context_state not in ("preparing", "active"):
            _fail()
        if self.data_version > self.profile_version:
            _fail()
        if self.state == "withdrawn" and self.context_state != "closed":
            _fail()
        if self.state == "suspended" and self.context_state != "suspended":
            _fail()
        if (self.published or self.accepting_requests) and (
            self.state != "enabled" or self.context_state != "active"
        ):
            _fail()


def create_publication_candidate(
    *, profile_id, owner_user_id, context_id, public_id, fields, public_context_label, now
):
    """Candidate for an own practice; identity binding/public label approval is external."""
    return PublicationAggregate(
        profile_id,
        owner_user_id,
        context_id,
        public_id,
        fields,
        public_context_label,
        updated_at=_time(now),
    )


def _owner(aggregate, actor):
    if not isinstance(actor, OwnerActor) or actor.user_id != aggregate.owner_user_id:
        _fail("RESOURCE_UNAVAILABLE")
    if not actor.confirmed or actor.assurance != "aal2":
        _fail("REQUEST_FORBIDDEN")


def _reviewer(aggregate, authority):
    if not isinstance(authority, ReviewAuthority):
        _fail("REQUEST_FORBIDDEN")
    if (
        authority.user_id == aggregate.owner_user_id
        or authority.assigned_profile_id != aggregate.profile_id
        or not authority.confirmed
        or authority.assurance != "aal2"
        or not authority.review_professionals
        or not authority.procedure_approved
    ):
        _fail("REQUEST_FORBIDDEN")


def _cas(aggregate, expected_profile_version, expected_context_version=None):
    _version(expected_profile_version)
    if expected_profile_version != aggregate.profile_version:
        _fail("VERSION_CONFLICT")
    if expected_context_version is not None:
        _version(expected_context_version)
        if expected_context_version != aggregate.context_version:
            _fail("VERSION_CONFLICT")


def _now(aggregate, now):
    result = _time(now)
    if result < aggregate.updated_at:
        _fail()
    return result


def edit_declaration(aggregate, *, actor, expected_profile_version, fields, declaration, now):
    _owner(aggregate, actor)
    _cas(aggregate, expected_profile_version)
    now = _now(aggregate, now)
    if aggregate.state in ("suspended", "withdrawn"):
        _fail("STATE_CONFLICT")
    if not isinstance(fields, DraftFields) or not isinstance(declaration, Declaration):
        _fail()
    if (fields, declaration) == (aggregate.fields, aggregate.declaration):
        return aggregate
    return replace(
        aggregate,
        fields=fields,
        declaration=declaration,
        state="draft",
        context_state="preparing",
        profile_version=aggregate.profile_version + 1,
        context_version=aggregate.context_version + (aggregate.context_state != "preparing"),
        listing_version=aggregate.listing_version + 1,
        data_version=aggregate.data_version + 1,
        submitted_profile_version=None,
        review=None,
        published=False,
        accepting_requests=False,
        updated_at=now,
    )


def submit_for_review(aggregate, *, actor, expected_profile_version, now):
    _owner(aggregate, actor)
    _cas(aggregate, expected_profile_version)
    now = _now(aggregate, now)
    if aggregate.state != "draft" or aggregate.declaration is None:
        _fail("STATE_CONFLICT")
    version = aggregate.profile_version + 1
    return replace(
        aggregate,
        state="submitted",
        profile_version=version,
        submitted_profile_version=version,
        updated_at=now,
    )


def decide_review(
    aggregate,
    *,
    authority,
    expected_profile_version,
    expected_data_version,
    outcome,
    scope,
    source,
    reason_code,
    now,
):
    _reviewer(aggregate, authority)
    _cas(aggregate, expected_profile_version)
    _version(expected_data_version)
    now = _now(aggregate, now)
    if expected_data_version != aggregate.data_version:
        _fail("VERSION_CONFLICT")
    if aggregate.state != "submitted":
        _fail("STATE_CONFLICT")
    decision = ReviewDecision(
        authority.user_id,
        aggregate.profile_version,
        aggregate.data_version,
        outcome,
        scope,
        source,
        reason_code,
        now,
    )
    return replace(
        aggregate,
        state=outcome,
        review=decision,
        profile_version=aggregate.profile_version + 1,
        listing_version=aggregate.listing_version + 1,
        updated_at=now,
    )


def activate_practice(aggregate, *, actor, expected_profile_version, expected_context_version, now):
    _owner(aggregate, actor)
    _cas(aggregate, expected_profile_version, expected_context_version)
    now = _now(aggregate, now)
    if aggregate.state != "enabled" or aggregate.context_state != "preparing":
        _fail("STATE_CONFLICT")
    return replace(
        aggregate,
        context_state="active",
        context_version=aggregate.context_version + 1,
        listing_version=aggregate.listing_version + 1,
        updated_at=now,
    )


def set_publication(aggregate, *, actor, expected_profile_version, published, now):
    _owner(aggregate, actor)
    _cas(aggregate, expected_profile_version)
    _bool(published)
    now = _now(aggregate, now)
    if aggregate.state in ("suspended", "withdrawn") or (
        published and (aggregate.state != "enabled" or aggregate.context_state != "active")
    ):
        _fail("STATE_CONFLICT")
    if aggregate.published == published:
        return aggregate
    return replace(
        aggregate,
        published=published,
        profile_version=aggregate.profile_version + 1,
        listing_version=aggregate.listing_version + 1,
        updated_at=now,
    )


def set_reception(aggregate, *, actor, expected_profile_version, accepting_requests, now):
    _owner(aggregate, actor)
    _cas(aggregate, expected_profile_version)
    _bool(accepting_requests)
    now = _now(aggregate, now)
    if aggregate.state != "enabled" or aggregate.context_state != "active":
        _fail("STATE_CONFLICT")
    if aggregate.accepting_requests == accepting_requests:
        return aggregate
    return replace(
        aggregate,
        accepting_requests=accepting_requests,
        profile_version=aggregate.profile_version + 1,
        listing_version=aggregate.listing_version + 1,
        updated_at=now,
    )


def withdraw_profile(aggregate, *, actor, expected_profile_version, expected_context_version, now):
    _owner(aggregate, actor)
    _cas(aggregate, expected_profile_version, expected_context_version)
    now = _now(aggregate, now)
    if aggregate.state == "withdrawn":
        return aggregate
    return replace(
        aggregate,
        state="withdrawn",
        context_state="closed",
        published=False,
        accepting_requests=False,
        profile_version=aggregate.profile_version + 1,
        context_version=aggregate.context_version + 1,
        listing_version=aggregate.listing_version + 1,
        updated_at=now,
    )


def suspend_profile(
    aggregate, *, authority, expected_profile_version, expected_context_version, now
):
    _reviewer(aggregate, authority)
    _cas(aggregate, expected_profile_version, expected_context_version)
    now = _now(aggregate, now)
    if aggregate.state != "enabled":
        _fail("STATE_CONFLICT")
    return replace(
        aggregate,
        state="suspended",
        context_state="suspended",
        published=False,
        accepting_requests=False,
        profile_version=aggregate.profile_version + 1,
        context_version=aggregate.context_version + 1,
        listing_version=aggregate.listing_version + 1,
        updated_at=now,
    )


def public_projection(aggregate, *, account_active, recipient_current):
    """Return the public allowlist only; caller must guard/recheck the live boundary."""
    _bool(account_active)
    _bool(recipient_current)
    if (
        not account_active
        or not recipient_current
        or aggregate.state != "enabled"
        or aggregate.context_state != "active"
        or not aggregate.published
        or aggregate.review is None
        or aggregate.review.outcome != "enabled"
        or aggregate.review.data_version != aggregate.data_version
    ):
        return None
    return {
        "public_id": str(aggregate.public_id),
        "display_name": aggregate.fields.display_name,
        "declared_area": aggregate.fields.declared_area,
        "review": {
            "scope": "registry_record_checked",
            "checked_at": aggregate.review.checked_at.isoformat(),
        },
        "listing_version": aggregate.listing_version,
        "public_context_label": aggregate.public_context_label,
        "requestable": aggregate.accepting_requests,
    }
