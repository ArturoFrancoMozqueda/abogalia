-- Independent after 002 + 001. Managed Auth grantor approval/capability required.
-- A0 pins Abogalia project externally; postgres database name is not proof.
-- Current remote postgres lacks auth USAGE WITH GRANT OPTION and PUBLIC lacks
-- USAGE. This file must remain unapplied by that operator; no managed-role grant.
BEGIN;
SET LOCAL statement_timeout = '10s';
SET LOCAL lock_timeout = '5s';
DO $probe$
BEGIN
    IF current_database() <> 'postgres'
       OR EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'abogalia_identity_probe')
       OR NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname='identity')
       OR (SELECT count(*) FROM pg_roles WHERE rolname IN (
           'abogalia_identity_owner', 'abogalia_identity_runtime'
       ) AND NOT (rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit OR rolreplication OR rolbypassrls)
         AND rolcanlogin = (rolname='abogalia_identity_runtime')) <> 2
       OR (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname='identity' AND c.relname IN ('users','app_sessions','audit')
           AND c.relkind='r' AND c.relrowsecurity AND c.relforcerowsecurity
           AND pg_get_userbyid(c.relowner)='abogalia_identity_owner') <> 3
       OR EXISTS (SELECT 1 FROM pg_auth_members WHERE member IN (
           SELECT oid FROM pg_roles WHERE rolname IN (
               'abogalia_identity_owner','abogalia_identity_runtime'
           )
       ))
    THEN
        RAISE EXCEPTION 'Identity probe requires reviewed installed state';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname=current_user AND (rolsuper OR rolcreaterole)
    ) THEN
        RAISE EXCEPTION 'Identity probe operator capability unavailable';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='auth' AND c.relname='sessions' AND c.relkind IN ('r','p')
    ) OR (SELECT count(*) FROM pg_attribute WHERE attrelid=to_regclass('auth.sessions')
          AND attname IN ('id','user_id') AND atttypid='uuid'::regtype
          AND attnum>0 AND NOT attisdropped) <> 2 THEN
        RAISE EXCEPTION 'Identity probe target shape unavailable';
    END IF;
    IF NOT has_schema_privilege(current_user, 'auth', 'USAGE WITH GRANT OPTION')
       OR NOT has_column_privilege(current_user, 'auth.sessions', 'id', 'SELECT WITH GRANT OPTION')
       OR NOT has_column_privilege(current_user, 'auth.sessions', 'user_id', 'SELECT WITH GRANT OPTION')
    THEN
        RAISE EXCEPTION 'Identity probe grantor capability unavailable';
    END IF;
END
$probe$;
CREATE ROLE abogalia_identity_probe LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
    NOINHERIT NOREPLICATION NOBYPASSRLS;
GRANT USAGE ON SCHEMA auth TO abogalia_identity_probe;
GRANT SELECT (id, user_id) ON auth.sessions TO abogalia_identity_probe;
COMMIT;
