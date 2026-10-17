-- MANUAL METADATA ONLY after install. Pin Legalia spohytnxscljtitvmdab externally.
-- No users, sessions, audit contents, passwords, keys or connection values.
BEGIN;
SET TRANSACTION READ ONLY;
SET LOCAL statement_timeout = '5s';
WITH relations AS (
    SELECT c.oid, c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='identity' AND c.relkind='r'
)
SELECT
    (SELECT count(*) FROM pg_roles WHERE rolname IN (
        'abogalia_identity_owner', 'abogalia_identity_runtime'
    ) AND NOT (rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit OR rolreplication OR rolbypassrls)
      AND rolcanlogin=(rolname='abogalia_identity_runtime')) = 2 AS roles_minimal,
    (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname='identity' AND c.relkind='r' AND c.relrowsecurity AND c.relforcerowsecurity
      AND pg_get_userbyid(c.relowner)='abogalia_identity_owner') = 3 AS tables_private_forced,
    NOT pg_has_role('postgres', 'abogalia_identity_owner', 'SET') AS installer_set_removed,
    NOT pg_has_role('postgres', 'abogalia_identity_owner', 'USAGE') AS installer_inherit_removed,
    NOT has_database_privilege('abogalia_identity_owner', 'postgres', 'CREATE') AS owner_db_create_removed,
    NOT pg_has_role('abogalia_identity_runtime', 'abogalia_identity_owner', 'MEMBER') AS runtime_no_owner,
    has_schema_privilege('abogalia_identity_runtime', 'identity', 'USAGE')
      AND NOT has_schema_privilege('abogalia_identity_runtime', 'identity', 'CREATE') AS runtime_schema_minimal,
    NOT has_schema_privilege('anon', 'identity', 'USAGE')
      AND NOT has_schema_privilege('authenticated', 'identity', 'USAGE') AS browser_roles_denied,
    NOT has_column_privilege('abogalia_identity_runtime',
        (SELECT oid FROM relations WHERE relname='users'), 'state', 'UPDATE')
      AND has_column_privilege('abogalia_identity_runtime',
        (SELECT oid FROM relations WHERE relname='users'), 'sessions_revoked_at', 'UPDATE')
      AS user_update_limited,
    NOT has_table_privilege('abogalia_identity_runtime',
        (SELECT oid FROM relations WHERE relname='audit'), 'SELECT')
      AND has_table_privilege('abogalia_identity_runtime',
        (SELECT oid FROM relations WHERE relname='audit'), 'INSERT') AS audit_insert_only,
    NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='abogalia_identity_probe') AS probe_deferred;
COMMIT;
-- All booleans must be true for this owner/runtime installation only. These
-- catalog checks do not prove RLS predicates, login, revocation, SMTP or C02 Done.
