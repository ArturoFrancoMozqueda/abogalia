-- MANUAL INSTALL, NOT AN AUTOMATIC MIGRATION. Review/pin destination first:
-- Legalia project spohytnxscljtitvmdab; organization tagovxtvdicxjweeerwi.
-- PostgreSQL catalogs do not establish the project identity. A0 verifies UI.
-- Technical names remain abogalia_identity_* by coordinated decision.
-- Derived exact bodies: 002_identity_roles.sql then 001_identity.sql.
-- One transaction; no passwords, Auth grants, data rows or remote configuration.
BEGIN;
SET LOCAL statement_timeout = '10s';
SET LOCAL lock_timeout = '5s';
DO $operator$
BEGIN
    IF current_user <> 'postgres' OR session_user <> 'postgres'
       OR current_database() <> 'postgres'
       OR current_setting('server_version_num')::integer < 160000
       OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname=current_user
                      AND rolcreaterole AND NOT rolsuper)
       OR NOT has_database_privilege(current_user, current_database(), 'CREATE WITH GRANT OPTION')
    THEN
        RAISE EXCEPTION 'Identity installer capability requires review';
    END IF;
END
$operator$;
-- Bootstrap preparation, not a numbered upgrade: run 002 BEFORE 001, once.
-- A0 must pin and verify the approved Abogalia project outside SQL. A database
-- name alone does not establish product identity. No passwords or memberships.
-- Requires existing operator CREATEROLE. No access to managed Auth required.
-- 001 separately requires legitimate SET ROLE owner and database CREATE;
-- this file never grants either privilege to its executor to bypass a blocker.
-- Install 002 and 001 bodies inside ONE reviewed transaction. Installer may
-- temporarily grant SET TRUE/INHERIT FALSE only on the new owner to itself,
-- and database CREATE to that new owner; RESET ROLE, REVOKE database CREATE
-- and REVOKE the transient SET membership BEFORE COMMIT. PG16/17 automatic
-- creator ADMIN membership may remain, with SET/INHERIT false; operator already
-- has CREATEROLE. Do not modify bootstrap/managed grantors to remove that row.
-- Verify no membership of runtime/probe in owner/elevated roles. No runtime DDL.
-- Probe is independent 003 and remains blocked by managed-auth USAGE grantor.
-- PG17 reference: https://www.postgresql.org/docs/17/sql-grant.html
SET LOCAL statement_timeout = '10s';
SET LOCAL lock_timeout = '5s';

DO $bootstrap$
BEGIN
    IF current_database() <> 'postgres'
       OR EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'identity')
       OR EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN (
           'abogalia_identity_owner', 'abogalia_identity_runtime', 'abogalia_identity_probe'
       )) THEN
        RAISE EXCEPTION 'Identity bootstrap requires reviewed empty state';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = current_user AND (rolsuper OR rolcreaterole)
    ) THEN
        RAISE EXCEPTION 'Identity bootstrap operator capability unavailable';
    END IF;
END
$bootstrap$;

CREATE ROLE abogalia_identity_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
    NOINHERIT NOREPLICATION NOBYPASSRLS;
CREATE ROLE abogalia_identity_runtime LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
    NOINHERIT NOREPLICATION NOBYPASSRLS;
-- Temporary permission on the NEW owner only; leave normal creator ADMIN intact.
GRANT abogalia_identity_owner TO postgres WITH SET TRUE;
GRANT abogalia_identity_owner TO postgres WITH INHERIT FALSE;
GRANT CREATE ON DATABASE postgres TO abogalia_identity_owner;
-- Local C02 only. Roles are provisioned separately by the authorized operator.
-- This migration never touches Supabase auth or public business tables.
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
RESET ROLE;
REVOKE CREATE ON DATABASE postgres FROM abogalia_identity_owner;
REVOKE abogalia_identity_owner FROM postgres;
DO $postcondition$
BEGIN
    IF pg_has_role('postgres', 'abogalia_identity_owner', 'SET')
       OR pg_has_role('postgres', 'abogalia_identity_owner', 'USAGE')
       OR has_database_privilege('abogalia_identity_owner', 'postgres', 'CREATE')
       OR pg_has_role('abogalia_identity_runtime', 'abogalia_identity_owner', 'MEMBER')
       OR (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname='identity' AND c.relkind='r'
             AND c.relrowsecurity AND c.relforcerowsecurity
             AND pg_get_userbyid(c.relowner)='abogalia_identity_owner') <> 3
    THEN
        RAISE EXCEPTION 'Identity installer postconditions failed';
    END IF;
END
$postcondition$;
COMMIT;
-- No probe was created. API must remain disabled until all activation gates pass.
-- Normal automatic creator ADMIN may remain, with SET/INHERIT false. It does not
-- imply credentials, readiness, remote Auth access, retention job or SMTP evidence.
