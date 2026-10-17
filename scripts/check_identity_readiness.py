"""Read-only local Identity preflight; no runtime secrets or remote executor."""

import argparse
import json
import os
from pathlib import Path

NAMES = (
    "ABOGALIA_IDENTITY_ENABLED",
    "ABOGALIA_ENVIRONMENT",
    "ABOGALIA_WEB_ORIGIN",
    "ABOGALIA_SUPABASE_URL",
    "ABOGALIA_SUPABASE_PUBLISHABLE_KEY",
    "ABOGALIA_CSRF_KEY",
    "ABOGALIA_DATABASE_DSN",
    "ABOGALIA_SESSION_CIPHER_KEY",
    "ABOGALIA_AUTH_SESSION_CHECK_DSN",
    "ABOGALIA_AUTH_EMAIL_READY",
)
JWKS_URL = "https://spohytnxscljtitvmdab.supabase.co/auth/v1/.well-known/jwks.json"
OWNER = "abogalia_identity_owner"
RUNTIME = "abogalia_identity_runtime"
PROBE = "abogalia_identity_probe"
PRIVILEGES = (
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE",
    "TRUNCATE",
    "REFERENCES",
    "TRIGGER",
)
COLUMNS = {
    "users": {
        "subject": "uuid",
        "state": "text",
        "created_at": "timestamp with time zone",
        "closed_at": "timestamp with time zone",
        "sessions_revoked_at": "timestamp with time zone",
    },
    "app_sessions": {
        "digest": "text",
        "subject": "uuid",
        "provider_session_id": "uuid",
        "secret_ciphertext": "bytea",
        "assurance": "text",
        "created_at": "timestamp with time zone",
        "last_activity_at": "timestamp with time zone",
        "token_expires_at": "timestamp with time zone",
    },
    "audit": {
        "event_id": "bigint",
        "subject": "uuid",
        "action": "text",
        "occurred_at": "timestamp with time zone",
    },
}


def presence(names):
    """Only iterate names. Presence does not imply nonempty or valid values."""
    available = set(names)
    return {name: name in available for name in NAMES}


def jwks_checks(document, destination, *, enabled=False):
    """Validate an injected public document; never fetch, print or retain keys."""
    checks = {
        "opt_in": enabled is True,
        "destination": destination == JWKS_URL,
        "public_es256_keys": False,
    }
    if not all((checks["opt_in"], checks["destination"])):
        return checks
    try:
        from jwt import PyJWK

        keys = document["keys"]
        if not isinstance(keys, list) or not 1 <= len(keys) <= 16:
            return checks
        seen = set()
        for key in keys:
            if not isinstance(key, dict) or set(key) - {
                "kty",
                "kid",
                "use",
                "alg",
                "crv",
                "x",
                "y",
            }:
                return checks
            if (
                key.get("alg") != "ES256"
                or key.get("kty") != "EC"
                or key.get("crv") != "P-256"
                or key.get("use", "sig") != "sig"
                or not isinstance(key.get("kid"), str)
                or not key["kid"]
                or len(key["kid"]) > 128
                or key["kid"] in seen
            ):
                return checks
            PyJWK.from_dict(key, algorithm="ES256")
            seen.add(key["kid"])
        checks["public_es256_keys"] = True
    except Exception:
        pass
    return checks


def catalog_snapshot(conn, expected_role):
    """Caller owns the connection. All SQL is fixed, catalog-only and read-only."""
    if expected_role not in (RUNTIME, PROBE) or conn.info.transaction_status != 0:
        raise ValueError("Catalog connection unavailable")
    with conn.transaction():
        conn.execute("SET TRANSACTION READ ONLY")
        conn.execute("SET LOCAL statement_timeout = '3s'")
        conn.execute("SET LOCAL lock_timeout = '1s'")
        role = conn.execute(
            "SELECT current_user, rolsuper, rolbypassrls, rolcreatedb, rolcreaterole, "
            "rolreplication FROM pg_catalog.pg_roles WHERE rolname = current_user"
        ).fetchone()
        elevated = conn.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE "
            "(rolsuper OR rolbypassrls OR rolcreatedb OR rolcreaterole OR rolreplication "
            "OR rolname = %s) AND pg_has_role(current_user, oid, 'MEMBER'))",
            (OWNER,),
        ).fetchone()[0]
        schemas = conn.execute(
            "SELECT nspname, has_schema_privilege(oid, 'USAGE'), "
            "has_schema_privilege(oid, 'CREATE') FROM pg_catalog.pg_namespace "
            "WHERE nspname NOT LIKE 'pg_%' AND nspname <> 'information_schema'"
        ).fetchall()
        tables = conn.execute(
            "SELECT c.oid, n.nspname, c.relname, pg_get_userbyid(c.relowner), "
            "c.relrowsecurity, c.relforcerowsecurity FROM pg_catalog.pg_class c "
            "JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace "
            "WHERE c.relkind IN ('r', 'p', 'v', 'm', 'f') "
            "AND n.nspname NOT LIKE 'pg_%' AND n.nspname <> 'information_schema'"
        ).fetchall()
        relations = []
        for oid, schema, table, owner, rls, force in tables:
            privileges = {
                privilege
                for privilege in PRIVILEGES
                if conn.execute(
                    "SELECT has_table_privilege(%s::oid, %s)", (oid, privilege)
                ).fetchone()[0]
            }
            columns = conn.execute(
                "SELECT attname, format_type(atttypid, atttypmod), "
                "has_column_privilege(attrelid, attnum, 'SELECT'), "
                "has_column_privilege(attrelid, attnum, 'INSERT'), "
                "has_column_privilege(attrelid, attnum, 'UPDATE'), "
                "has_column_privilege(attrelid, attnum, 'REFERENCES') "
                "FROM pg_catalog.pg_attribute WHERE attrelid = %s "
                "AND attnum > 0 AND NOT attisdropped",
                (oid,),
            ).fetchall()
            policies = conn.execute(
                "SELECT polname, polcmd, polpermissive, "
                "ARRAY(SELECT pg_get_userbyid(x) FROM unnest(polroles) x), "
                "polqual IS NOT NULL, polwithcheck IS NOT NULL "
                "FROM pg_catalog.pg_policy WHERE polrelid = %s",
                (oid,),
            ).fetchall()
            relations.append((schema, table, owner, rls, force, privileges, columns, policies))
        sequences = conn.execute(
            "SELECT n.nspname, c.relname, has_sequence_privilege(c.oid, 'USAGE'), "
            "has_sequence_privilege(c.oid, 'SELECT'), has_sequence_privilege(c.oid, 'UPDATE') "
            "FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n "
            "ON n.oid = c.relnamespace WHERE c.relkind = 'S' "
            "AND n.nspname NOT LIKE 'pg_%'"
        ).fetchall()
        functions = conn.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_proc p "
            "JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace "
            "WHERE n.nspname = 'identity' AND has_function_privilege(p.oid, 'EXECUTE'))"
        ).fetchone()[0]
        return role, elevated, schemas, relations, sequences, functions


def assess(snapshot, expected_role):
    role, elevated, schemas, relations, sequences, functions = snapshot
    runtime = expected_role == RUNTIME
    checks = {
        "role_exact": role[0] == expected_role,
        "role_unprivileged": not any(role[1:]) and not elevated,
        "schema_usage_only": False,
        "schema_shape": True,
        "table_grants": True,
        "column_grants": True,
        "rls_forced": True,
        "policies_structural": True,
        "other_relations_denied": True,
        "sequence_grants": True,
        "identity_functions_denied": not functions,
    }
    schema_map = {name: (usage, create) for name, usage, create in schemas}
    checks["schema_usage_only"] = (
        schema_map.get("identity") == (True, False)
        if runtime
        else schema_map.get("identity", (False, False)) == (False, False)
    ) and (
        schema_map.get("auth", (False, False)) == (False, False)
        if runtime
        else schema_map.get("auth") == (True, False)
    )
    checks["schema_usage_only"] &= not any(create for _, _, create in schemas)
    found = set()
    for schema, table, owner, rls, force, privileges, columns, policies in relations:
        if schema == "identity" and table in COLUMNS:
            found.add(table)
            checks["schema_shape"] &= (
                owner == OWNER and {column[0]: column[1] for column in columns} == COLUMNS[table]
            )
            checks["rls_forced"] &= rls and force
            allowed = (
                (
                    {"SELECT", "INSERT"}
                    if table == "users"
                    else {"SELECT", "INSERT", "UPDATE", "DELETE"}
                    if table == "app_sessions"
                    else {"INSERT"}
                )
                if runtime
                else set()
            )
            checks["table_grants"] &= privileges == allowed
            for column, _, select, insert, update, references in columns:
                expected = (
                    runtime and table != "audit",
                    runtime,
                    runtime
                    and (
                        table == "app_sessions"
                        or (table == "users" and column == "sessions_revoked_at")
                    ),
                    False,
                )
                checks["column_grants"] &= (
                    select,
                    insert,
                    update,
                    references,
                ) == expected
            runtime_name = {
                "users": "users_runtime",
                "app_sessions": "sessions_runtime",
                "audit": "audit_runtime_insert",
            }[table]
            wanted = {
                (
                    runtime_name,
                    "a" if table == "audit" else "*",
                    True,
                    (RUNTIME,),
                    table != "audit",
                    True,
                ),
                (
                    ("sessions" if table == "app_sessions" else table) + "_maintenance",
                    "*",
                    True,
                    (OWNER,),
                    True,
                    True,
                ),
            }
            actual = {
                (name, cmd, permissive, tuple(roles), using, check)
                for name, cmd, permissive, roles, using, check in policies
            }
            checks["policies_structural"] &= actual == wanted
        elif schema == "auth" and table == "sessions":
            found.add("auth.sessions")
            checks["table_grants"] &= not privileges
            types = {column[0]: column[1] for column in columns}
            checks["schema_shape"] &= types.get("id") == types.get("user_id") == "uuid"
            for column, _, select, insert, update, references in columns:
                checks["column_grants"] &= select == (
                    not runtime and column in ("id", "user_id")
                ) and not any((insert, update, references))
        else:
            checks["other_relations_denied"] &= not privileges and not any(
                any(column[2:]) for column in columns
            )
            if schema == "identity":
                checks["schema_shape"] = False
    checks["schema_shape"] &= set(COLUMNS) <= found if runtime else "auth.sessions" in found
    found_sequence = False
    for schema, name, usage, select, update in sequences:
        expected = runtime and (schema, name) == ("identity", "audit_event_id_seq")
        found_sequence |= (schema, name) == ("identity", "audit_event_id_seq")
        checks["sequence_grants"] &= (usage, select, update) == (expected, False, False)
    checks["sequence_grants"] &= found_sequence if runtime else True
    return {name: bool(value) for name, value in checks.items()}


def inspect_catalog(conn, role, *, enabled=False):
    if enabled is not True:
        return {"status": "disabled", "checks": {}}
    try:
        if role not in (RUNTIME, PROBE):
            raise ValueError
        checks = assess(catalog_snapshot(conn, role), role)
        return {
            "status": "catalog_passed" if all(checks.values()) else "catalog_failed",
            "checks": checks,
        }
    except Exception:
        return {"status": "catalog_unavailable", "checks": {}}


def local_socket_allowed(path):
    try:
        if (
            path is None
            or not path.is_absolute()
            or not path.is_dir()
            or path.is_symlink()
            or path.parent.is_symlink()
            or path.name != "socket"
            or not path.parent.name.startswith("abogalia-identity-tests-")
        ):
            return False
        return all(
            item.stat().st_uid == os.getuid() and item.stat().st_mode & 0o077 == 0
            for item in (path, path.parent)
        )
    except Exception:
        return False


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError("Invalid arguments")


def main(argv=None):
    parser = SafeParser(description=__doc__)
    parser.add_argument("--inspect-local", action="store_true")
    parser.add_argument("--socket", type=Path)
    parser.add_argument("--port", type=int, default=54983)
    try:
        args = parser.parse_args(argv)
    except ValueError:
        print(json.dumps({"status": "invalid_arguments", "real_readiness": "pending"}))
        return 2
    report = {
        "status": "disabled",
        "configuration_presence": presence(os.environ.keys()),
        "jwks": "not_executed",
        "real_readiness": "pending",
    }
    exit_code = 0
    if args.inspect_local:
        try:
            if (
                any(name.startswith("PG") and name != "PGPASSFILE" for name in os.environ.keys())
                or not local_socket_allowed(args.socket)
                or not 1024 < args.port < 65536
            ):
                raise ValueError
            import psycopg

            catalogs = {}
            for label, role in (("runtime", RUNTIME), ("probe", PROBE)):
                with psycopg.connect(
                    host=str(args.socket),
                    port=args.port,
                    dbname="abogalia_storage_test",
                    user=role,
                    password="",
                    passfile=os.devnull,
                    connect_timeout=3,
                    autocommit=True,
                ) as conn:
                    if conn.execute("SHOW listen_addresses").fetchone() != ("",):
                        raise ValueError
                    catalogs[label] = inspect_catalog(conn, role, enabled=True)
            passed = all(item["status"] == "catalog_passed" for item in catalogs.values())
            report |= {
                "status": "local_catalog_passed" if passed else "local_catalog_failed",
                "catalogs": catalogs,
            }
            exit_code = 0 if passed else 2
        except Exception:
            report["status"] = "local_catalog_unavailable"
            exit_code = 2
    print(json.dumps(report, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
