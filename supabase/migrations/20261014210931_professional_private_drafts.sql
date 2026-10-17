-- C03 private inactive aggregate only. Existing Identity owner/runtime required.
-- No Auth, public API, managed grants, new role or external resource changes.
BEGIN;
SET LOCAL ROLE abogalia_identity_owner;
DO $guard$
BEGIN
    IF current_user <> 'abogalia_identity_owner'
       OR EXISTS (SELECT 1 FROM pg_roles WHERE rolname = current_user
                  AND (rolsuper OR rolbypassrls OR rolcanlogin))
       OR NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'identity'
                      AND pg_get_userbyid(nspowner) = current_user)
       OR to_regclass('identity.users') IS NULL
       OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'abogalia_identity_runtime'
                      AND rolcanlogin AND NOT rolsuper AND NOT rolbypassrls
                      AND NOT rolcreatedb AND NOT rolcreaterole)
       OR pg_has_role('abogalia_identity_runtime', 'abogalia_identity_owner', 'MEMBER')
       OR to_regclass('identity.professional_drafts') IS NOT NULL
       OR to_regclass('identity.professional_events') IS NOT NULL
    THEN RAISE EXCEPTION 'Professional schema prerequisite unavailable';
    END IF;
END
$guard$;

CREATE TABLE identity.professional_drafts (
    profile_id uuid PRIMARY KEY CHECK (profile_id <> '00000000-0000-0000-0000-000000000000'),
    owner_user_id uuid NOT NULL UNIQUE REFERENCES identity.users(subject) ON DELETE RESTRICT,
    context_id uuid NOT NULL UNIQUE CHECK (context_id <> '00000000-0000-0000-0000-000000000000'),
    kind text NOT NULL CHECK (kind = 'practice'),
    display_name text NOT NULL CHECK (length(btrim(display_name)) BETWEEN 1 AND 120),
    declared_area text CHECK (declared_area IS NULL OR length(btrim(declared_area)) BETWEEN 1 AND 240),
    profile_state text NOT NULL CHECK (profile_state IN ('draft', 'withdrawn')),
    context_state text NOT NULL CHECK (context_state IN ('preparing', 'closed')),
    profile_version integer NOT NULL CHECK (profile_version > 0),
    context_version integer NOT NULL CHECK (context_version > 0),
    created_at timestamptz NOT NULL,
    profile_updated_at timestamptz NOT NULL CHECK (profile_updated_at >= created_at),
    context_updated_at timestamptz NOT NULL CHECK (context_updated_at >= created_at),
    withdrawn_at timestamptz,
    closed_at timestamptz,
    CHECK (owner_user_id <> '00000000-0000-0000-0000-000000000000'),
    CHECK (
        (profile_state = 'draft' AND context_state = 'preparing'
         AND withdrawn_at IS NULL AND closed_at IS NULL)
        OR
        (profile_state = 'withdrawn' AND context_state = 'closed'
         AND withdrawn_at IS NOT NULL AND closed_at IS NOT NULL
         AND withdrawn_at = closed_at
         AND withdrawn_at = profile_updated_at AND closed_at = context_updated_at)
    )
);
CREATE INDEX professional_drafts_retention_idx
    ON identity.professional_drafts ((COALESCE(withdrawn_at, profile_updated_at)));

CREATE TABLE identity.professional_events (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_user_id uuid NOT NULL CHECK (actor_user_id <> '00000000-0000-0000-0000-000000000000'),
    profile_id uuid NOT NULL CHECK (profile_id <> '00000000-0000-0000-0000-000000000000'),
    context_id uuid NOT NULL CHECK (context_id <> '00000000-0000-0000-0000-000000000000'),
    transition text NOT NULL CHECK (transition IN ('draft_created', 'draft_edited', 'draft_withdrawn')),
    occurred_at timestamptz NOT NULL,
    profile_version integer NOT NULL CHECK (profile_version > 0),
    context_version integer NOT NULL CHECK (context_version > 0)
);
-- Logical references intentionally lack FK: 30d data purge must not cascade 90d history.
CREATE INDEX professional_events_retention_idx ON identity.professional_events(occurred_at);

REVOKE ALL ON identity.professional_drafts, identity.professional_events
    FROM PUBLIC, abogalia_identity_runtime;
REVOKE ALL ON SEQUENCE identity.professional_events_event_id_seq
    FROM PUBLIC, abogalia_identity_runtime;
GRANT SELECT, INSERT ON identity.professional_drafts TO abogalia_identity_runtime;
GRANT UPDATE (display_name, declared_area, profile_state, context_state,
              profile_version, context_version, profile_updated_at, context_updated_at,
              withdrawn_at, closed_at)
    ON identity.professional_drafts TO abogalia_identity_runtime;
GRANT INSERT ON identity.professional_events TO abogalia_identity_runtime;
GRANT USAGE ON SEQUENCE identity.professional_events_event_id_seq TO abogalia_identity_runtime;

ALTER TABLE identity.professional_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.professional_drafts FORCE ROW LEVEL SECURITY;
ALTER TABLE identity.professional_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.professional_events FORCE ROW LEVEL SECURITY;

CREATE POLICY professional_drafts_runtime ON identity.professional_drafts
    TO abogalia_identity_runtime
    USING (owner_user_id::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''))
    WITH CHECK (owner_user_id::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''));
CREATE POLICY professional_events_runtime_insert ON identity.professional_events
    FOR INSERT TO abogalia_identity_runtime
    WITH CHECK (
        actor_user_id::text = NULLIF((SELECT current_setting('abogalia.subject', true)), '')
        AND EXISTS (
            SELECT 1 FROM identity.professional_drafts d
            WHERE d.owner_user_id = professional_events.actor_user_id
              AND d.profile_id = professional_events.profile_id
              AND d.context_id = professional_events.context_id
              AND d.profile_version = professional_events.profile_version
              AND d.context_version = professional_events.context_version
        )
    );
CREATE POLICY professional_drafts_maintenance ON identity.professional_drafts
    TO abogalia_identity_owner USING (true) WITH CHECK (true);
CREATE POLICY professional_events_maintenance ON identity.professional_events
    TO abogalia_identity_owner USING (true) WITH CHECK (true);
COMMIT;
