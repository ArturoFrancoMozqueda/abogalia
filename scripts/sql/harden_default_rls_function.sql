-- MANUAL ACL ONLY. Pin Legalia spohytnxscljtitvmdab externally before running.
-- Do not call/read/replace the function, disable the trigger, or assume a new
-- managed role. Exact catalog state reviewed by A0, 2026-10-13.
BEGIN;
SET LOCAL statement_timeout = '5s';
SET LOCAL lock_timeout = '5s';
DO $harden$
DECLARE
    function_before record;
    function_after record;
    trigger_before record;
    trigger_after record;
BEGIN
    IF current_user <> 'postgres' OR session_user <> 'postgres' THEN
        RAISE EXCEPTION 'RLS function ACL operator requires review';
    END IF;
    SELECT p.oid, p.proowner, p.prorettype, p.prokind, p.prosecdef, p.pronargs
      INTO function_before FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
      WHERE n.nspname='public' AND p.proname='rls_auto_enable' AND p.pronargs=0;
    IF NOT FOUND OR pg_get_userbyid(function_before.proowner) <> 'postgres'
       OR function_before.prorettype <> 'event_trigger'::regtype
       OR function_before.prokind <> 'f' OR NOT function_before.prosecdef THEN
        RAISE EXCEPTION 'RLS function ACL target requires review';
    END IF;
    IF (SELECT count(*) FROM pg_event_trigger WHERE evtfoid=function_before.oid) <> 1 THEN
        RAISE EXCEPTION 'RLS function ACL trigger requires review';
    END IF;
    SELECT oid, evtname, evtevent, evtowner, evtenabled, evttags, evtfoid
      INTO trigger_before FROM pg_event_trigger WHERE evtfoid=function_before.oid;
    IF trigger_before.evtname <> 'ensure_rls'
       OR trigger_before.evtevent <> 'ddl_command_end'
       OR trigger_before.evtenabled <> 'O'
       OR trigger_before.evttags IS DISTINCT FROM
          ARRAY['CREATE TABLE','CREATE TABLE AS','SELECT INTO']::text[] THEN
        RAISE EXCEPTION 'RLS function ACL trigger configuration requires review';
    END IF;

    REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC RESTRICT;
    REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM anon RESTRICT;
    REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM authenticated RESTRICT;

    SELECT p.oid, p.proowner, p.prorettype, p.prokind, p.prosecdef, p.pronargs
      INTO function_after FROM pg_proc p WHERE p.oid=function_before.oid;
    SELECT oid, evtname, evtevent, evtowner, evtenabled, evttags, evtfoid
      INTO trigger_after FROM pg_event_trigger WHERE oid=trigger_before.oid;
    IF function_after IS DISTINCT FROM function_before
       OR trigger_after IS DISTINCT FROM trigger_before
       OR has_function_privilege('anon', function_before.oid, 'EXECUTE')
       OR has_function_privilege('authenticated', function_before.oid, 'EXECUTE')
       OR EXISTS (SELECT 1 FROM pg_proc p,
           LATERAL aclexplode(COALESCE(p.proacl, acldefault('f', p.proowner))) a
           WHERE p.oid=function_before.oid AND a.grantee=0 AND a.privilege_type='EXECUTE')
    THEN
        RAISE EXCEPTION 'RLS function ACL postconditions failed';
    END IF;
END
$harden$;
-- Query evaluates real effective privileges; no function body or function call.
SELECT NOT has_function_privilege('anon', 'public.rls_auto_enable()', 'EXECUTE')
    AND NOT has_function_privilege('authenticated', 'public.rls_auto_enable()', 'EXECUTE')
    AS browser_execute_denied;
COMMIT;
