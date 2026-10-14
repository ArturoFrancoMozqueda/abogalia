"""Pure inactive drafts, synthetic UUID/text/time only; no Auth/store/HTTP evidence."""

import json
from dataclasses import FrozenInstanceError, asdict, replace
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from abogalia_api.professional_contexts.domain import (
    DomainError,
    DraftAggregate,
    DraftFields,
    create_draft,
    edit_draft,
    read_draft,
    withdraw_draft,
)

NOW = datetime(2026, 10, 14, 12, tzinfo=UTC)
PRIVATE_TEXT = "PUBLIC_SYNTHETIC_PRIVATE_NAME"


@pytest.fixture
def original():
    return create_draft(
        actor_user_id=uuid4(),
        profile_id=uuid4(),
        context_id=uuid4(),
        fields=DraftFields(PRIVATE_TEXT, "PUBLIC_SYNTHETIC_AREA"),
        now=NOW,
    )


def withdraw(aggregate, **overrides):
    arguments = {
        "actor_user_id": aggregate.profile.owner_user_id,
        "expected_version": aggregate.profile.profile_version,
        "expected_context_version": aggregate.practice.context_version,
        "now": NOW + timedelta(days=1),
    }
    arguments.update(overrides)
    return withdraw_draft(aggregate, **arguments)


def test_creation_is_private_inactive_pair_with_minimal_event(original):
    aggregate = original.aggregate
    assert aggregate.profile.state == "draft" and aggregate.practice.state == "preparing"
    assert aggregate.practice.kind == "practice"
    assert aggregate.profile.profile_id == aggregate.practice.profile_id
    assert aggregate.profile.owner_user_id == aggregate.practice.owner_user_id
    assert aggregate.profile.created_at == aggregate.practice.created_at == NOW
    assert "PUBLIC_SYNTHETIC" not in repr(aggregate) + repr(aggregate.profile) + repr(
        aggregate.profile.fields
    )
    assert "PUBLIC_SYNTHETIC" not in json.dumps(asdict(original.events[0]), default=str)
    assert set(asdict(original.events[0])) == {
        "actor_user_id",
        "profile_id",
        "context_id",
        "transition",
        "occurred_at",
        "profile_version",
        "context_version",
    }
    assert not hasattr(aggregate.practice, "capabilities")
    assert not hasattr(aggregate.profile, "registration_number")


@pytest.mark.parametrize("operation", ["read", "edit", "withdraw"])
def test_foreign_actor_denied_before_versions_and_no_partial_state(original, operation):
    aggregate = original.aggregate
    foreign = uuid4()
    with pytest.raises(DomainError) as error:
        if operation == "read":
            read_draft(aggregate, actor_user_id=foreign)
        elif operation == "edit":
            edit_draft(
                aggregate,
                actor_user_id=foreign,
                expected_version=99,
                fields=DraftFields("PUBLIC_CHANGED"),
                now=NOW,
            )
        else:
            withdraw(aggregate, actor_user_id=foreign, expected_version=99)
    assert error.value.code == "RESOURCE_UNAVAILABLE"
    assert PRIVATE_TEXT not in str(error.value) + repr(error.value)
    assert aggregate.profile.state == "draft" and aggregate.practice.state == "preparing"
    assert aggregate.profile.profile_version == aggregate.practice.context_version == 1


def test_edit_preserves_owner_context_and_rejects_stale_snapshot(original):
    aggregate = original.aggregate
    updated = edit_draft(
        aggregate,
        actor_user_id=aggregate.profile.owner_user_id,
        expected_version=1,
        fields=DraftFields("PUBLIC_CHANGED"),
        now=NOW + timedelta(days=2),
    )
    assert updated.aggregate.profile.owner_user_id == aggregate.profile.owner_user_id
    assert updated.aggregate.practice is aggregate.practice
    assert updated.aggregate.profile.profile_version == 2
    assert aggregate.profile.fields.display_name == PRIVATE_TEXT
    with pytest.raises(DomainError) as error:
        edit_draft(
            updated.aggregate,
            actor_user_id=aggregate.profile.owner_user_id,
            expected_version=1,
            fields=DraftFields("PUBLIC_LOST_UPDATE"),
            now=NOW + timedelta(days=3),
        )
    assert error.value.code == "VERSION_CONFLICT"
    assert updated.aggregate.profile.fields.display_name == "PUBLIC_CHANGED"


@pytest.mark.parametrize("version_field", ["expected_version", "expected_context_version"])
def test_withdraw_both_versions_required_and_atomic(original, version_field):
    aggregate = original.aggregate
    with pytest.raises(DomainError) as error:
        withdraw(aggregate, **{version_field: 2})
    assert error.value.code == "VERSION_CONFLICT"
    assert aggregate.profile.state == "draft" and aggregate.practice.state == "preparing"
    result = withdraw(aggregate)
    assert result.aggregate.profile.state == "withdrawn"
    assert result.aggregate.practice.state == "closed"
    assert result.aggregate.profile.withdrawn_at == result.aggregate.practice.closed_at
    assert (
        result.aggregate.profile.profile_version == result.aggregate.practice.context_version == 2
    )
    assert len(result.events) == 1 and result.events[0].transition == "draft_withdrawn"


def test_withdraw_retry_cannot_extend_retention_or_restore_editing(original):
    aggregate = withdraw(original.aggregate).aggregate
    retry = withdraw(aggregate, now=NOW + timedelta(days=20))
    assert retry.aggregate is aggregate and retry.events == ()
    assert retry.aggregate.retention_deadline == NOW + timedelta(days=31)
    with pytest.raises(DomainError) as error:
        edit_draft(
            aggregate,
            actor_user_id=aggregate.profile.owner_user_id,
            expected_version=2,
            fields=DraftFields("PUBLIC_RESTORE"),
            now=NOW + timedelta(days=2),
        )
    assert error.value.code == "STATE_CONFLICT"


def test_read_and_noop_do_not_reset_draft_deadline_but_real_edit_does(original):
    aggregate = original.aggregate
    read = read_draft(aggregate, actor_user_id=aggregate.profile.owner_user_id)
    noop = edit_draft(
        read,
        actor_user_id=aggregate.profile.owner_user_id,
        expected_version=1,
        fields=DraftFields("  " + PRIVATE_TEXT + "  ", "PUBLIC_SYNTHETIC_AREA"),
        now=NOW + timedelta(days=29),
    )
    assert noop.aggregate is aggregate and noop.events == ()
    assert not aggregate.retention_due(NOW + timedelta(days=30) - timedelta(microseconds=1))
    assert aggregate.retention_due(NOW + timedelta(days=30))
    changed = edit_draft(
        aggregate,
        actor_user_id=aggregate.profile.owner_user_id,
        expected_version=1,
        fields=DraftFields("PUBLIC_REAL_EDIT"),
        now=NOW + timedelta(days=29),
    ).aggregate
    assert not changed.retention_due(NOW + timedelta(days=30))
    assert changed.retention_due(NOW + timedelta(days=59))
    assert changed.practice.context_version == 1


def test_data_30_days_and_event_90_days_are_separate_at_exact_boundary(original):
    result = withdraw(original.aggregate)
    assert not result.aggregate.retention_due(NOW + timedelta(days=31) - timedelta(microseconds=1))
    assert result.aggregate.retention_due(NOW + timedelta(days=31))
    event = result.events[0]
    assert not event.retention_due(NOW + timedelta(days=31))
    assert not event.retention_due(NOW + timedelta(days=91) - timedelta(microseconds=1))
    assert event.retention_due(NOW + timedelta(days=91))


def test_broken_owner_reference_or_half_withdrawn_pair_rejected(original):
    aggregate = original.aggregate
    for practice in (
        replace(aggregate.practice, owner_user_id=uuid4()),
        replace(aggregate.practice, profile_id=uuid4()),
        replace(aggregate.practice, state="closed", updated_at=NOW, closed_at=NOW),
    ):
        with pytest.raises(DomainError):
            DraftAggregate(aggregate.profile, practice)
    with pytest.raises(FrozenInstanceError):
        aggregate.profile.owner_user_id = uuid4()


@pytest.mark.parametrize("field", ["actor_user_id", "profile_id", "context_id"])
def test_zero_uuid_rejected_for_actor_and_objects(field):
    arguments = {
        "actor_user_id": uuid4(),
        "profile_id": uuid4(),
        "context_id": uuid4(),
        "fields": DraftFields("PUBLIC_SYNTHETIC"),
        "now": NOW,
    }
    arguments[field] = UUID(int=0)
    with pytest.raises(DomainError):
        create_draft(**arguments)


def test_zero_event_id_reference_and_forbidden_states_rejected(original):
    with pytest.raises(DomainError):
        replace(original.events[0], actor_user_id=UUID(int=0))
    for record, field, value in (
        (original.aggregate.profile, "state", "enabled"),
        (original.aggregate.practice, "state", "active"),
        (original.aggregate.practice, "kind", "firm"),
    ):
        with pytest.raises(DomainError):
            replace(record, **{field: value})


@pytest.mark.parametrize("value", ["", "PUBLIC\nPRIVATE", "X" * 121, "\ud800"])
def test_invalid_text_fixed_error_without_echo(value):
    with pytest.raises(DomainError) as error:
        DraftFields(value)
    assert str(error.value) == "Professional draft operation unavailable"


def test_invalid_clock_and_boolean_version_fail_without_mutation(original):
    aggregate = original.aggregate
    for clock in (NOW.replace(tzinfo=None), NOW - timedelta(seconds=1)):
        with pytest.raises(DomainError):
            withdraw(aggregate, now=clock)
    with pytest.raises(DomainError):
        withdraw(aggregate, expected_version=True)
    normalized = create_draft(
        actor_user_id=uuid4(),
        profile_id=uuid4(),
        context_id=uuid4(),
        fields=DraftFields("PUBLIC_SYNTHETIC"),
        now=NOW.astimezone(timezone(timedelta(hours=-6))),
    )
    assert normalized.aggregate.profile.created_at == NOW
