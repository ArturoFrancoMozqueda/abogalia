-- MANUAL UPGRADE. Pin Legalia spohytnxscljtitvmdab externally before running.
-- Same authorization, cached transaction context per statement via InitPlans.
-- No DB CREATE grant, data access, Auth modification or function execution.
BEGIN;
SET LOCAL statement_timeout = '10s';
SET LOCAL lock_timeout = '5s';
DO $guard$
DECLARE
    policy_row record;
    subject_expression text := '((subject)::text = NULLIF(current_setting(''abogalia.subject''::text, true), ''''::text))';
    session_expression text := '((digest = NULLIF(current_setting(''abogalia.digest''::text, true), ''''::text)) OR ((subject)::text = NULLIF(current_setting(''abogalia.subject''::text, true), ''''::text)))';
BEGIN
    IF current_user <> 'postgres' OR session_user <> 'postgres'
       OR current_database() <> 'postgres'
       OR NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname=current_user AND rolcreaterole AND NOT rolsuper)
       OR pg_has_role('postgres', 'abogalia_identity_owner', 'SET')
       OR pg_has_role('postgres', 'abogalia_identity_owner', 'USAGE')
       OR has_database_privilege('abogalia_identity_owner', 'postgres', 'CREATE')
       OR pg_has_role('abogalia_identity_runtime','abogalia_identity_owner','MEMBER')
       OR (SELECT count(*) FROM pg_roles WHERE rolname IN (
           'abogalia_identity_owner','abogalia_identity_runtime'
       ) AND NOT (rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit OR rolreplication OR rolbypassrls)
         AND rolcanlogin=(rolname='abogalia_identity_runtime')) <> 2
    THEN
        RAISE EXCEPTION 'Identity RLS operator requires review';
    END IF;
    IF (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='identity' AND c.relkind='r' AND c.relrowsecurity AND c.relforcerowsecurity
          AND pg_get_userbyid(c.relowner)='abogalia_identity_owner') <> 3
       OR (SELECT count(*) FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid
           JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity') <> 6 THEN
        RAISE EXCEPTION 'Identity RLS schema requires review';
    END IF;
    FOR policy_row IN SELECT c.relname, p.polname, p.polcmd, p.polroles, p.polpermissive,
        pg_get_expr(p.polqual,p.polrelid) AS using_expression,
        pg_get_expr(p.polwithcheck,p.polrelid) AS check_expression
        FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='identity' AND p.polname IN ('users_runtime','sessions_runtime','audit_runtime_insert')
    LOOP
        IF policy_row.relname NOT IN ('users','app_sessions','audit')
           OR NOT policy_row.polpermissive OR policy_row.polroles <> ARRAY['abogalia_identity_runtime'::regrole::oid]
           OR policy_row.check_expression IS DISTINCT FROM subject_expression
           OR (policy_row.relname='users' AND (policy_row.polname<>'users_runtime' OR policy_row.polcmd<>'*'
                 OR policy_row.using_expression IS DISTINCT FROM subject_expression))
           OR (policy_row.relname='app_sessions' AND (policy_row.polname<>'sessions_runtime' OR policy_row.polcmd<>'*'
                 OR policy_row.using_expression IS DISTINCT FROM session_expression))
           OR (policy_row.relname='audit' AND (policy_row.polname<>'audit_runtime_insert' OR policy_row.polcmd<>'a'
                 OR policy_row.using_expression IS NOT NULL))
        THEN
            RAISE EXCEPTION 'Identity RLS predicates require review';
        END IF;
    END LOOP;
    IF (SELECT count(*) FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='identity'
        AND p.polname IN ('users_runtime','sessions_runtime','audit_runtime_insert')) <> 3 THEN
        RAISE EXCEPTION 'Identity RLS policy targets require review';
    END IF;
END
$guard$;
GRANT abogalia_identity_owner TO postgres WITH SET TRUE;
GRANT abogalia_identity_owner TO postgres WITH INHERIT FALSE;
SET LOCAL ROLE abogalia_identity_owner;

ALTER POLICY users_runtime ON identity.users
    USING (subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''))
    WITH CHECK (subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''));
ALTER POLICY sessions_runtime ON identity.app_sessions
    USING (digest = NULLIF((SELECT current_setting('abogalia.digest', true)), '')
        OR subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''))
    WITH CHECK (subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''));
ALTER POLICY audit_runtime_insert ON identity.audit
    WITH CHECK (subject::text = NULLIF((SELECT current_setting('abogalia.subject', true)), ''));

RESET ROLE;
REVOKE abogalia_identity_owner FROM postgres;
DO $post$
BEGIN
    IF pg_has_role('postgres','abogalia_identity_owner','SET')
       OR pg_has_role('postgres','abogalia_identity_owner','USAGE')
       OR has_database_privilege('abogalia_identity_owner','postgres','CREATE') THEN
        RAISE EXCEPTION 'Identity RLS transient privilege cleanup failed';
    END IF;
END
$post$;
COMMIT;
-- Creator ADMIN remains with SET/INHERIT false, as before this operation.
-- Reapply/unknown policy shape fails closed. No authorization or ACL expansion.
