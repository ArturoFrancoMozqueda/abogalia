"""Exact role SQL in a separate disposable Unix-only cluster, never fixture roles."""

import importlib.util
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import psycopg
import pytest
from psycopg import sql

ROOT = Path(__file__).parents[3]
BOOTSTRAP = ROOT / "apps/api/migrations/002_identity_roles.sql"
SCHEMA = ROOT / "apps/api/migrations/001_identity.sql"
ROLES = ("abogalia_identity_owner", "abogalia_identity_runtime", "abogalia_identity_probe")


def invoke(args):
    return subprocess.run(
        args,
        env={"PATH": os.defpath, "LANG": "C", "LC_ALL": "C", "PGPASSFILE": os.devnull},
        capture_output=True,
        timeout=30,
        check=False,
    )


@pytest.fixture(scope="module")
def bootstrap_cluster():
    spec = importlib.util.spec_from_file_location(
        "sql_runner", ROOT / "scripts/run_identity_tests.py"
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    cluster = Path(tempfile.mkdtemp(prefix="abogalia-identity-role-tests-"))
    cluster.chmod(0o700)
    socket = cluster / "socket"
    socket.mkdir(mode=0o700)
    binary, attempted = None, False
    try:
        binary = helper.postgres_bin(None)
        result = invoke(
            [
                str(binary / "initdb"),
                "-D",
                str(cluster / "data"),
                "-A",
                "trust",
                "-U",
                "abogalia_test_owner",
                "--no-locale",
                "--encoding=UTF8",
            ]
        )
        if result.returncode:
            raise RuntimeError
        attempted = True
        result = invoke(
            [
                str(binary / "pg_ctl"),
                "-D",
                str(cluster / "data"),
                "-l",
                str(cluster / "server.log"),
                "-o",
                f'-k {socket} -p 54984 -h "" -c log_statement=none '
                "-c log_min_error_statement=panic -c log_parameter_max_length_on_error=0",
                "-w",
                "start",
            ]
        )
        if result.returncode:
            raise RuntimeError
        yield f"host={socket} port=54984 dbname=postgres user=abogalia_test_owner"
    except Exception:
        pytest.fail("Isolated role bootstrap unavailable; diagnostics suppressed.", pytrace=False)
    finally:
        safe_to_remove = not attempted
        if attempted:
            try:
                stopped = invoke(
                    [
                        str(binary / "pg_ctl"),
                        "-D",
                        str(cluster / "data"),
                        "-m",
                        "immediate",
                        "-w",
                        "stop",
                    ]
                )
                safe_to_remove = stopped.returncode == 0
                if not safe_to_remove:
                    safe_to_remove = (
                        invoke(
                            [str(binary / "pg_ctl"), "-D", str(cluster / "data"), "status"]
                        ).returncode
                        == 3
                    )
            except Exception:
                safe_to_remove = False
        try:
            if not safe_to_remove:
                raise RuntimeError
            shutil.rmtree(cluster)
        except Exception:
            pytest.fail(
                "Role bootstrap cluster cleanup failed; diagnostics suppressed.", pytrace=False
            )


@pytest.fixture
def bootstrap_db(bootstrap_cluster):
    with psycopg.connect(
        bootstrap_cluster, autocommit=True, passfile=os.devnull, password=""
    ) as conn:
        # This module owns the entire separate disposable cluster.
        conn.execute("DROP SCHEMA IF EXISTS identity CASCADE")
        conn.execute("DROP SCHEMA IF EXISTS auth CASCADE")
        for name in ROLES:
            conn.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(name)))
        if conn.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='abogalia_bootstrap_limited')"
        ).fetchone()[0]:
            conn.execute("REVOKE CREATE ON DATABASE postgres FROM abogalia_bootstrap_limited")
        conn.execute("DROP ROLE IF EXISTS abogalia_bootstrap_limited")
        conn.execute("CREATE SCHEMA auth")
        conn.execute(
            "CREATE TABLE auth.sessions(id uuid PRIMARY KEY, user_id uuid, private_marker text)"
        )
        conn.execute("REVOKE ALL ON SCHEMA auth FROM PUBLIC")
        conn.execute("REVOKE ALL ON auth.sessions FROM PUBLIC")
        yield conn


def apply(conn):
    conn.execute(BOOTSTRAP.read_text())


def existing(conn):
    return conn.execute(
        "SELECT count(*) FROM pg_roles WHERE rolname = ANY(%s)", (list(ROLES),)
    ).fetchone()[0]


PROBE = ROOT / "apps/api/migrations/003_identity_probe.sql"


def transaction_body(path):
    return "\n".join(
        line for line in path.read_text().splitlines() if line not in {"BEGIN;", "COMMIT;"}
    )


def install_schema(conn):
    apply(conn)
    conn.execute("GRANT CREATE ON DATABASE postgres TO abogalia_identity_owner")
    conn.execute(SCHEMA.read_text())
    conn.execute("REVOKE CREATE ON DATABASE postgres FROM abogalia_identity_owner")


def role_connection(source, user):
    from psycopg.conninfo import make_conninfo

    return psycopg.connect(
        make_conninfo(source, user=user), autocommit=True, password="", passfile=os.devnull
    )


def test_bootstrap_exact_roles_no_elevation(bootstrap_db, bootstrap_cluster):
    conn = bootstrap_db
    apply(conn)
    rows = conn.execute(
        "SELECT rolname, rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, "
        "rolinherit, rolreplication, rolbypassrls FROM pg_roles WHERE rolname = ANY(%s)",
        (list(ROLES),),
    ).fetchall()
    assert bool(len(rows) == 2 and all(not any(row[2:]) for row in rows))
    assert bool({name: login for name, login, *_ in rows} == {ROLES[0]: False, ROLES[1]: True})
    assert bool(
        conn.execute(
            "SELECT count(*) FROM pg_auth_members WHERE member IN "
            "(SELECT oid FROM pg_roles WHERE rolname = ANY(%s))",
            (list(ROLES),),
        ).fetchone()[0]
        == 0
    )
    with role_connection(bootstrap_cluster, ROLES[1]) as runtime:
        for query in (
            "SELECT id FROM auth.sessions",
            "SET ROLE abogalia_identity_owner",
            "CREATE TABLE auth.forbidden(id int)",
        ):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                runtime.execute(query)


@pytest.mark.parametrize("role", ROLES)
def test_existing_role_blocks_without_modifying_it(bootstrap_db, role):
    conn = bootstrap_db
    conn.execute(sql.SQL("CREATE ROLE {} NOLOGIN CREATEDB").format(sql.Identifier(role)))
    with pytest.raises(psycopg.Error):
        apply(conn)
    conn.rollback()
    assert bool(existing(conn) == 1)
    assert bool(
        conn.execute(
            "SELECT rolcreatedb, rolcanlogin FROM pg_roles WHERE rolname = %s", (role,)
        ).fetchone()
        == (True, False)
    )


def test_existing_schema_blocks_before_roles(bootstrap_db):
    bootstrap_db.execute("CREATE SCHEMA identity")
    with pytest.raises(psycopg.Error):
        apply(bootstrap_db)
    bootstrap_db.rollback()
    assert bool(existing(bootstrap_db) == 0)


def test_probe_wrong_shape_preserves_schema_and_roles(bootstrap_db):
    install_schema(bootstrap_db)
    bootstrap_db.execute("ALTER TABLE auth.sessions ALTER COLUMN user_id TYPE text")
    with pytest.raises(psycopg.Error):
        bootstrap_db.execute(PROBE.read_text())
    bootstrap_db.rollback()
    assert bool(existing(bootstrap_db) == 2)


def limited_operator(conn, source, *, auth_usage=True):
    from psycopg.conninfo import make_conninfo

    conn.execute(
        "CREATE ROLE abogalia_bootstrap_limited LOGIN CREATEROLE NOSUPERUSER "
        "NOCREATEDB NOINHERIT NOREPLICATION NOBYPASSRLS"
    )
    conn.execute(
        "GRANT CREATE ON DATABASE postgres TO abogalia_bootstrap_limited WITH GRANT OPTION"
    )
    if auth_usage:
        conn.execute("GRANT USAGE ON SCHEMA auth TO abogalia_bootstrap_limited WITH GRANT OPTION")
    conn.execute(
        "GRANT SELECT (id, user_id) ON auth.sessions "
        "TO abogalia_bootstrap_limited WITH GRANT OPTION"
    )
    return make_conninfo(source, user="abogalia_bootstrap_limited")


def test_probe_missing_usage_grantor_preserves_installed_schema(bootstrap_db, bootstrap_cluster):
    install_schema(bootstrap_db)
    source = limited_operator(bootstrap_db, bootstrap_cluster, auth_usage=False)
    with psycopg.connect(source, autocommit=True, password="", passfile=os.devnull) as conn:
        with pytest.raises(psycopg.Error):
            conn.execute(PROBE.read_text())
        conn.rollback()
    assert bool(existing(bootstrap_db) == 2)
    assert bool(
        bootstrap_db.execute(
            "SELECT count(*) FROM pg_auth_members "
            "WHERE member='abogalia_bootstrap_limited'::regrole"
        ).fetchone()[0]
        == 0
    )


def test_schema_legitimate_operator_runtime_denied(bootstrap_db, bootstrap_cluster):
    install_schema(bootstrap_db)
    with role_connection(bootstrap_cluster, ROLES[1]) as conn:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute("SET ROLE abogalia_identity_owner")
        assert bool(
            conn.execute(
                "SELECT has_schema_privilege(current_user, 'identity', 'CREATE')"
            ).fetchone()
            == (False,)
        )
    assert bool(
        bootstrap_db.execute(
            "SELECT count(*) FROM pg_class WHERE relnamespace='identity'::regnamespace "
            "AND relkind='r' AND relrowsecurity AND relforcerowsecurity"
        ).fetchone()[0]
        == 3
    )


def test_probe_exact_columns_no_write_or_owner(bootstrap_db, bootstrap_cluster):
    install_schema(bootstrap_db)
    bootstrap_db.execute(PROBE.read_text())
    with role_connection(bootstrap_cluster, ROLES[2]) as conn:
        assert bool(conn.execute("SELECT id, user_id FROM auth.sessions").fetchall() == [])
        for query in (
            "SELECT private_marker FROM auth.sessions",
            "INSERT INTO auth.sessions(id,user_id) VALUES(NULL,NULL)",
            "SET ROLE abogalia_identity_owner",
            "SELECT subject FROM identity.users",
        ):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                conn.execute(query)
    with pytest.raises(psycopg.Error):
        bootstrap_db.execute(PROBE.read_text())
    bootstrap_db.rollback()
    assert bool(existing(bootstrap_db) == 3)


def test_reapply_rejected(bootstrap_db):
    apply(bootstrap_db)
    with pytest.raises(psycopg.Error):
        apply(bootstrap_db)
    bootstrap_db.rollback()
    assert bool(existing(bootstrap_db) == 2)


def test_nonsuper_transient_set_create_removed_auto_admin_retained(bootstrap_db, bootstrap_cluster):
    source = limited_operator(bootstrap_db, bootstrap_cluster)
    with psycopg.connect(source, autocommit=True, password="", passfile=os.devnull) as conn:
        with conn.transaction():
            conn.execute(transaction_body(BOOTSTRAP))
            assert bool(
                conn.execute(
                    "SELECT pg_has_role(current_user, 'abogalia_identity_owner', 'SET')"
                ).fetchone()
                == (False,)
            )
            conn.execute(
                "GRANT abogalia_identity_owner TO abogalia_bootstrap_limited WITH SET TRUE"
            )
            conn.execute(
                "GRANT abogalia_identity_owner TO abogalia_bootstrap_limited WITH INHERIT FALSE"
            )
            conn.execute("GRANT CREATE ON DATABASE postgres TO abogalia_identity_owner")
            conn.execute(transaction_body(SCHEMA))
            conn.execute("RESET ROLE")
            conn.execute("REVOKE CREATE ON DATABASE postgres FROM abogalia_identity_owner")
            conn.execute("REVOKE abogalia_identity_owner FROM abogalia_bootstrap_limited")
            assert bool(
                conn.execute(
                    "SELECT pg_has_role(current_user, 'abogalia_identity_owner', 'SET'), "
                    "has_database_privilege('abogalia_identity_owner', 'postgres', 'CREATE')"
                ).fetchone()
                == (False, False)
            )
    assert bool(
        bootstrap_db.execute(
            "SELECT admin_option, inherit_option, set_option FROM pg_auth_members "
            "WHERE roleid='abogalia_identity_owner'::regrole "
            "AND member='abogalia_bootstrap_limited'::regrole"
        ).fetchall()
        == [(True, False, False)]
    )


def test_failed_schema_rolls_back_role_grants_membership(bootstrap_db, bootstrap_cluster):
    source = limited_operator(bootstrap_db, bootstrap_cluster)
    with psycopg.connect(source, autocommit=True, password="", passfile=os.devnull) as conn:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            conn.execute(transaction_body(BOOTSTRAP))
            conn.execute(
                "GRANT abogalia_identity_owner TO abogalia_bootstrap_limited WITH SET TRUE"
            )
            conn.execute(transaction_body(SCHEMA))
    assert bool(existing(bootstrap_db) == 0)
    assert bool(
        bootstrap_db.execute(
            "SELECT count(*) FROM pg_namespace WHERE nspname='identity'"
        ).fetchone()[0]
        == 0
    )


def test_identity_bootstrap_does_not_require_auth(bootstrap_db):
    bootstrap_db.execute("DROP SCHEMA auth CASCADE")
    install_schema(bootstrap_db)
    assert bool(existing(bootstrap_db) == 2)


def test_probe_without_schema_blocks(bootstrap_db):
    apply(bootstrap_db)
    with pytest.raises(psycopg.Error):
        bootstrap_db.execute(PROBE.read_text())
    bootstrap_db.rollback()
    assert bool(existing(bootstrap_db) == 2)


def test_probe_wrong_rls_blocks(bootstrap_db):
    install_schema(bootstrap_db)
    bootstrap_db.execute("ALTER TABLE identity.users NO FORCE ROW LEVEL SECURITY")
    with pytest.raises(psycopg.Error):
        bootstrap_db.execute(PROBE.read_text())
    bootstrap_db.rollback()
    assert bool(existing(bootstrap_db) == 2)
