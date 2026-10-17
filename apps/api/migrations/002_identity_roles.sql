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
BEGIN;
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
COMMIT;
