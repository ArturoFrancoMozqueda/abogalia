"""Synthetic pure-domain checks; no live account, permissions, DB or registry."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from abogalia_api.professional_contexts.domain import DomainError, DraftFields
from abogalia_api.professional_contexts.publication import (
    Declaration,
    OwnerActor,
    ReviewAuthority,
    activate_practice,
    create_publication_candidate,
    decide_review,
    edit_declaration,
    public_projection,
    set_publication,
    set_reception,
    submit_for_review,
    suspend_profile,
    withdraw_profile,
)

NOW = datetime(2026, 10, 17, tzinfo=UTC)
OWNER = UUID(int=1)
PROFILE = UUID(int=2)
CONTEXT = UUID(int=3)
PUBLIC = UUID(int=4)
REVIEWER = UUID(int=5)
ACTOR = OwnerActor(OWNER, True, "aal2")
AUTHORITY = ReviewAuthority(REVIEWER, PROFILE, True, "aal2", True, True)
FIELDS = DraftFields("Profesional Sintético", "Ámbito declarado sintético")
DECLARATION = Declaration("Nombre Sintético Privado", "0012345678")


def candidate():
    return create_publication_candidate(
        profile_id=PROFILE,
        owner_user_id=OWNER,
        context_id=CONTEXT,
        public_id=PUBLIC,
        fields=FIELDS,
        public_context_label="Práctica sintética",
        now=NOW,
    )


def declared():
    value = candidate()
    return edit_declaration(
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        fields=FIELDS,
        declaration=DECLARATION,
        now=NOW,
    )


def submitted():
    value = declared()
    return submit_for_review(
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        now=NOW,
    )


def decide(value, **overrides):
    kwargs = {
        "authority": AUTHORITY,
        "expected_profile_version": value.profile_version,
        "expected_data_version": value.data_version,
        "outcome": "enabled",
        "scope": "registry_record_checked",
        "source": "official_registry",
        "reason_code": "registry_record_checked",
        "now": NOW,
    }
    kwargs.update(overrides)
    return decide_review(value, **kwargs)


def enabled():
    return decide(submitted())


def active():
    value = enabled()
    return activate_practice(
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        expected_context_version=value.context_version,
        now=NOW,
    )


def visible():
    value = active()
    return set_publication(
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        published=True,
        now=NOW,
    )


def projection(value):
    return public_projection(value, account_active=True, recipient_current=True)


def rejected():
    return decide(
        submitted(),
        outcome="rejected",
        scope="none",
        source=None,
        reason_code="identity_binding_unresolved",
    )


def assert_error(code, function, *args, **kwargs):
    with pytest.raises(DomainError) as caught:
        function(*args, **kwargs)
    assert caught.value.code == code
    assert str(caught.value) == "Professional draft operation unavailable"


def test_review_is_version_bound_and_does_not_activate_publish_or_accept_requests():
    before = submitted()
    value = decide(before)
    assert value.state == "enabled"
    assert value.review.data_version == value.data_version
    assert value.review.reviewed_profile_version == before.profile_version
    assert value.review.reviewer_user_id != value.owner_user_id
    assert value.context_state == "preparing"
    assert not value.published and not value.accepting_requests
    assert projection(value) is None


def test_active_practice_still_requires_voluntary_publication_and_reception():
    value = active()
    assert projection(value) is None
    value = set_publication(
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        published=True,
        now=NOW,
    )
    assert projection(value)["requestable"] is False
    value = set_reception(
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        accepting_requests=True,
        now=NOW,
    )
    assert projection(value)["requestable"] is True


def test_projection_exact_allowlist_and_nested_review_scope():
    value = visible()
    result = projection(value)
    assert set(result) == {
        "public_id",
        "display_name",
        "declared_area",
        "review",
        "listing_version",
        "public_context_label",
        "requestable",
    }
    assert result["review"] == {
        "scope": "registry_record_checked",
        "checked_at": NOW.isoformat(),
    }
    assert result["public_id"] == str(PUBLIC)
    assert result["public_context_label"] == "Práctica sintética"
    assert DECLARATION.legal_name not in str(result)
    assert DECLARATION.registration_number not in str(result)
    assert str(OWNER) not in str(result)
    assert str(CONTEXT) not in str(result)
    result["review"]["scope"] = "tampered"
    assert projection(value)["review"]["scope"] == "registry_record_checked"


@pytest.mark.parametrize("factory", [candidate, declared, submitted, rejected])
def test_non_enabled_profiles_have_no_public_projection(factory):
    assert projection(factory()) is None


@pytest.mark.parametrize("field", ["account_active", "recipient_current"])
def test_current_account_and_recipient_are_required_at_disclosure(field):
    facts = {"account_active": True, "recipient_current": True}
    facts[field] = False
    assert public_projection(visible(), **facts) is None


@pytest.mark.parametrize(
    "change",
    [
        {"user_id": OWNER},
        {"assigned_profile_id": UUID(int=99)},
        {"confirmed": False},
        {"assurance": "aal1"},
        {"review_professionals": False},
        {"procedure_approved": False},
    ],
)
def test_review_requires_explicit_current_authority_assignment_mfa_and_distinct_actor(change):
    assert_error("REQUEST_FORBIDDEN", decide, submitted(), authority=replace(AUTHORITY, **change))


def test_metadata_dict_is_never_review_authority():
    assert_error(
        "REQUEST_FORBIDDEN",
        decide,
        submitted(),
        authority={"user_id": REVIEWER, "review_professionals": True, "aal": "aal2"},
    )


@pytest.mark.parametrize(
    "change",
    [
        {"expected_profile_version": 1},
        {"expected_data_version": 1},
    ],
)
def test_review_rejects_stale_profile_or_declaration_versions(change):
    assert_error("VERSION_CONFLICT", decide, submitted(), **change)


@pytest.mark.parametrize(
    "change",
    [
        {"scope": "none"},
        {"source": None},
        {"reason_code": "identity_verified"},
        {"outcome": "published"},
    ],
)
def test_enabled_review_requires_exact_non_overclaiming_evidence(change):
    assert_error("INVALID_REQUEST", decide, submitted(), **change)


@pytest.mark.parametrize(
    "fields,declaration",
    [
        (DraftFields("Otro nombre sintético", FIELDS.declared_area), DECLARATION),
        (FIELDS, Declaration("Otro nombre privado sintético", "0012345678")),
        (FIELDS, Declaration(DECLARATION.legal_name, "0098765432")),
        (DraftFields(FIELDS.display_name, "Otro ámbito declarado"), DECLARATION),
    ],
)
def test_any_reviewed_input_edit_invalidates_review_publication_and_activation(fields, declaration):
    before = visible()
    value = edit_declaration(
        before,
        actor=ACTOR,
        expected_profile_version=before.profile_version,
        fields=fields,
        declaration=declaration,
        now=NOW + timedelta(seconds=1),
    )
    assert value.state == "draft" and value.context_state == "preparing"
    assert value.review is None and value.submitted_profile_version is None
    assert value.data_version > before.data_version
    assert value.listing_version > before.listing_version
    assert not value.published and not value.accepting_requests
    assert value.public_id == before.public_id and value.context_id == before.context_id
    assert projection(value) is None
    assert_error(
        "STATE_CONFLICT",
        set_publication,
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        published=True,
        now=value.updated_at,
    )


def test_edit_while_submitted_invalidates_pending_snapshot_and_stale_decision():
    before = submitted()
    after = edit_declaration(
        before,
        actor=ACTOR,
        expected_profile_version=before.profile_version,
        fields=DraftFields("Revisión cambiada", None),
        declaration=DECLARATION,
        now=NOW,
    )
    assert after.state == "draft"
    assert_error(
        "VERSION_CONFLICT",
        decide,
        after,
        expected_profile_version=before.profile_version,
        expected_data_version=before.data_version,
    )


def test_unchanged_edit_and_publication_noop_do_not_extend_dates_or_versions():
    before = visible()
    assert (
        edit_declaration(
            before,
            actor=ACTOR,
            expected_profile_version=before.profile_version,
            fields=FIELDS,
            declaration=DECLARATION,
            now=NOW + timedelta(hours=1),
        )
        is before
    )
    assert (
        set_publication(
            before,
            actor=ACTOR,
            expected_profile_version=before.profile_version,
            published=True,
            now=NOW + timedelta(hours=1),
        )
        is before
    )


def test_rejection_requires_real_edit_and_new_submission_before_reconsideration():
    before = rejected()
    assert projection(before) is None
    assert_error("STATE_CONFLICT", decide, before)
    after = edit_declaration(
        before,
        actor=ACTOR,
        expected_profile_version=before.profile_version,
        fields=FIELDS,
        declaration=Declaration(DECLARATION.legal_name, "0098765432"),
        now=NOW,
    )
    after = submit_for_review(
        after,
        actor=ACTOR,
        expected_profile_version=after.profile_version,
        now=NOW,
    )
    assert decide(after).state == "enabled"


@pytest.mark.parametrize("factory", [candidate, submitted, rejected])
def test_cannot_activate_without_enabled_review(factory):
    value = factory()
    assert_error(
        "STATE_CONFLICT",
        activate_practice,
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        expected_context_version=value.context_version,
        now=NOW,
    )


@pytest.mark.parametrize("action", [activate_practice, withdraw_profile])
def test_context_cas_is_checked_for_aggregate_wide_commands(action):
    value = enabled()
    assert_error(
        "VERSION_CONFLICT",
        action,
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        expected_context_version=99,
        now=NOW,
    )


@pytest.mark.parametrize(
    "actor",
    [
        OwnerActor(UUID(int=99), True, "aal2"),
        OwnerActor(OWNER, False, "aal2"),
        OwnerActor(OWNER, True, "aal1"),
    ],
)
def test_owner_operations_require_current_confirmed_owner_and_mfa(actor):
    value = visible()
    expected = "RESOURCE_UNAVAILABLE" if actor.user_id != OWNER else "REQUEST_FORBIDDEN"
    assert_error(
        expected,
        set_publication,
        value,
        actor=actor,
        expected_profile_version=value.profile_version,
        published=False,
        now=NOW,
    )


def test_revoke_publication_immediately_hides_projection_and_increments_listing_version():
    before = visible()
    after = set_publication(
        before,
        actor=ACTOR,
        expected_profile_version=before.profile_version,
        published=False,
        now=NOW,
    )
    assert projection(after) is None
    assert after.listing_version > before.listing_version


@pytest.mark.parametrize("terminal", ["suspended", "withdrawn"])
def test_terminal_profiles_cannot_be_resurrected_by_edit_submit_publish_or_activate(terminal):
    before = visible()
    kwargs = {
        "expected_profile_version": before.profile_version,
        "expected_context_version": before.context_version,
        "now": NOW,
    }
    value = (
        suspend_profile(before, authority=AUTHORITY, **kwargs)
        if terminal == "suspended"
        else withdraw_profile(before, actor=ACTOR, **kwargs)
    )
    assert value.state == terminal and projection(value) is None
    assert not value.accepting_requests and not value.published
    assert_error(
        "STATE_CONFLICT",
        edit_declaration,
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        fields=DraftFields("Cambio posterior", None),
        declaration=DECLARATION,
        now=NOW,
    )
    assert_error(
        "STATE_CONFLICT",
        submit_for_review,
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        now=NOW,
    )
    assert_error(
        "STATE_CONFLICT",
        set_publication,
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        published=True,
        now=NOW,
    )
    assert_error(
        "STATE_CONFLICT",
        activate_practice,
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        expected_context_version=value.context_version,
        now=NOW,
    )


def test_withdrawal_replay_is_noop_and_old_version_still_fails():
    before = visible()
    value = withdraw_profile(
        before,
        actor=ACTOR,
        expected_profile_version=before.profile_version,
        expected_context_version=before.context_version,
        now=NOW,
    )
    assert (
        withdraw_profile(
            value,
            actor=ACTOR,
            expected_profile_version=value.profile_version,
            expected_context_version=value.context_version,
            now=NOW + timedelta(days=1),
        )
        is value
    )
    assert_error(
        "VERSION_CONFLICT",
        withdraw_profile,
        value,
        actor=ACTOR,
        expected_profile_version=before.profile_version,
        expected_context_version=before.context_version,
        now=NOW,
    )


@pytest.mark.parametrize("number", ["", "123 45", "１２３", "1" * 33, True])
def test_registration_validation_does_not_coerce_or_claim_registry_validity(number):
    assert_error("INVALID_REQUEST", Declaration, "Nombre sintético", number)


def test_registration_preserves_leading_zeroes_and_private_values_never_appear_in_repr():
    value = visible()
    assert value.declaration.registration_number == "0012345678"
    output = repr((value, value.declaration, value.review, ACTOR, AUTHORITY, value.fields))
    for private in (DECLARATION.legal_name, DECLARATION.registration_number, str(OWNER)):
        assert private not in output


@pytest.mark.parametrize(
    "change",
    [
        {"published": True},
        {"accepting_requests": True},
        {"profile_version": True},
        {"public_id": OWNER},
        {"public_id": CONTEXT},
        {"state": "enabled"},
        {"context_state": "closed"},
        {"data_version": 99},
    ],
)
def test_corrupt_or_premature_aggregate_is_rejected(change):
    assert_error("INVALID_REQUEST", replace, candidate(), **change)


def test_review_from_other_data_version_cannot_be_attached_to_current_aggregate():
    value = enabled()
    assert_error(
        "INVALID_REQUEST",
        replace,
        value,
        review=replace(value.review, data_version=value.data_version + 1),
    )


def test_backdated_mutation_fails_instead_of_restarting_review_or_retention():
    value = visible()
    assert_error(
        "INVALID_REQUEST",
        set_publication,
        value,
        actor=ACTOR,
        expected_profile_version=value.profile_version,
        published=False,
        now=NOW - timedelta(seconds=1),
    )
