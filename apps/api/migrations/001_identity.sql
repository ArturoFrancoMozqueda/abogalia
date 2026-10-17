-- Local C02 only. Roles are provisioned separately by the authorized operator.
-- This migration never touches Supabase auth or public business tables.
BEGIN;
SET LOCAL ROLE abogalia_identity_owner;

CREATE SCHEMA identity AUTHORIZATION abogalia_identity_owner;
REVOKE ALL ON SCHEMA identity FROM PUBLIC;
GRANT USAGE ON SCHEMA identity TO abogalia_identity_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA identity REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA identity REVOKE ALL ON SEQUENCES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA identity REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

CREATE TABLE identity.users (
    subject uuid PRIMARY KEY,
    state text NOT NULL DEFAULT 'active' CHECK (state IN ('active', 'restricted', 'closed')),
    created_at timestamptz NOT NULL,
    closed_at timestamptz,
    sessions_revoked_at timestamptz,
    CHECK ((state = 'closed') = (closed_at IS NOT NULL)),
    CHECK (closed_at IS NULL OR closed_at >= created_at)
);

CREATE TABLE identity.app_sessions (
    digest text PRIMARY KEY CHECK (digest ~ '^[0-9a-f]{64}$'),
    subject uuid NOT NULL REFERENCES identity.users(subject) ON DELETE RESTRICT,
    provider_session_id uuid NOT NULL,
    secret_ciphertext bytea NOT NULL,
    assurance text NOT NULL CHECK (assurance IN ('aal1', 'aal2')),
    created_at timestamptz NOT NULL,
    last_activity_at timestamptz NOT NULL,
    token_expires_at timestamptz NOT NULL,
    CHECK (last_activity_at >= created_at),
    CHECK (token_expires_at > created_at)
);
CREATE INDEX app_sessions_subject_idx ON identity.app_sessions(subject);
CREATE INDEX app_sessions_created_idx ON identity.app_sessions(created_at);
CREATE INDEX app_sessions_activity_idx ON identity.app_sessions(last_activity_at);
CREATE INDEX users_closed_idx ON identity.users(closed_at) WHERE state = 'closed';

CREATE TABLE identity.audit (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject uuid NOT NULL,
    action text NOT NULL CHECK (action IN (
        'session_created', 'session_saved', 'session_deleted', 'subject_revoked'
    )),
    occurred_at timestamptz NOT NULL
);
-- No FK to users: removing account evidence at 30d must not cascade 90d audit.
CREATE INDEX audit_occurred_idx ON identity.audit(occurred_at);

REVOKE ALL ON ALL TABLES IN SCHEMA identity FROM PUBLIC, abogalia_identity_runtime;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA identity FROM PUBLIC, abogalia_identity_runtime;
GRANT SELECT, INSERT ON identity.users TO abogalia_identity_runtime;
GRANT UPDATE (sessions_revoked_at) ON identity.users TO abogalia_identity_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON identity.app_sessions TO abogalia_identity_runtime;
GRANT INSERT ON identity.audit TO abogalia_identity_runtime;
GRANT USAGE ON SEQUENCE identity.audit_event_id_seq TO abogalia_identity_runtime;

ALTER TABLE identity.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.users FORCE ROW LEVEL SECURITY;
ALTER TABLE identity.app_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.app_sessions FORCE ROW LEVEL SECURITY;
ALTER TABLE identity.audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.audit FORCE ROW LEVEL SECURITY;

CREATE POLICY users_runtime ON identity.users TO abogalia_identity_runtime
    USING (subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''))
    WITH CHECK (subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''));
CREATE POLICY sessions_runtime ON identity.app_sessions TO abogalia_identity_runtime
    USING (
        digest = NULLIF((SELECT current_setting('abogalia.digest', true)), '')
        OR subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), '')
    )
    WITH CHECK (subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''));
CREATE POLICY audit_runtime_insert ON identity.audit FOR INSERT TO abogalia_identity_runtime
    WITH CHECK (subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''));

CREATE POLICY users_maintenance ON identity.users TO abogalia_identity_owner
    USING (true) WITH CHECK (true);
CREATE POLICY sessions_maintenance ON identity.app_sessions TO abogalia_identity_owner
    USING (true) WITH CHECK (true);
CREATE POLICY audit_maintenance ON identity.audit TO abogalia_identity_owner
    USING (true) WITH CHECK (true);
COMMIT;
