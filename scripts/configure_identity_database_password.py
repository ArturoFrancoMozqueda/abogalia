"""One-off Legalia runtime password setup; private input and fixed TLS destination.

Never reads the application's .env. Never emits passwords or raw diagnostics.
Only the already-existing runtime role's password can change; no grants or roles.
"""

import hashlib
import json
import logging
import os
import secrets
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / ".env.database-setup"
OUTPUT = ROOT / ".env.database-runtime"
CA = ROOT / "apps/api/certificates/supabase-prod-ca-2021.crt"
PROJECT = "spohytnxscljtitvmdab"
HOST = "aws-0-us-east-1.pooler.supabase.com"
ROLE = "abogalia_identity_runtime"
NAME = "ABOGALIA_SETUP_DATABASE_ADMIN_PASSWORD"
ROLE_SAFETY_SQL = (
    "SELECT rolcanlogin AND NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole "
    "AND NOT rolreplication AND NOT rolbypassrls AND NOT rolinherit "
    "AND NOT EXISTS (SELECT 1 FROM pg_auth_members m WHERE m.member = pg_roles.oid) "
    "FROM pg_roles WHERE rolname = %s"
)


class SetupUnavailable(Exception):
    def __init__(self):
        super().__init__("Database setup unavailable")


def private_password(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as source:
        before = os.fstat(source.fileno())
        if (
            not stat.S_ISREG(before.st_mode)
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_uid != os.getuid()
            or before.st_nlink != 1
            or before.st_size > 4096
        ):
            raise SetupUnavailable
        payload = source.read(4097)
        after = os.fstat(source.fileno())
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise SetupUnavailable
    name, separator, value = payload.decode("utf-8").removesuffix("\n").partition("=")
    if (
        name != NAME
        or not separator
        or not value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise SetupUnavailable
    return value


def tls_options():
    if (
        CA.is_symlink()
        or not CA.is_file()
        or hashlib.sha256(CA.read_bytes()).hexdigest()
        != "700723581420dd1ac98fd7e9ac529f0ef210eadcaf87fc868a3ad7d114c2f3b7"
    ):
        raise SetupUnavailable
    return {
        "host": HOST,
        "port": 5432,
        "dbname": "postgres",
        "sslmode": "verify-full",
        "sslrootcert": str(CA),
        "sslcertmode": "disable",
        "passfile": os.devnull,
        "connect_timeout": 10,
    }


def write_runtime_file(path, password):
    # Generated URL-safe password cannot introduce conninfo or dotenv syntax.
    dsn = (
        f"host={HOST} port=5432 dbname=postgres user={ROLE}.{PROJECT} "
        f"password={password} sslmode=verify-full sslrootcert={CA}"
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
        os.fchmod(output.fileno(), 0o600)
        output.write("ABOGALIA_DATABASE_DSN=" + dsn + "\n")
        output.flush()
        os.fsync(output.fileno())


def configure(password, *, connect, output=OUTPUT):
    from psycopg import sql

    # Refuse repeat execution, including after uncertain external outcomes.
    if output.exists() or output.is_symlink():
        raise SetupUnavailable
    options = tls_options()
    with connect(**options, user="postgres." + PROJECT, password=password) as admin:
        identity = admin.execute("SELECT current_user, current_database()").fetchone()
        role = admin.execute(
            ROLE_SAFETY_SQL,
            (ROLE,),
        ).fetchone()
        if identity != ("postgres", "postgres") or role != (True,):
            raise SetupUnavailable
        generated = secrets.token_urlsafe(48)
        verifier = admin.pgconn.encrypt_password(
            generated.encode("ascii"), ROLE.encode("ascii"), b"scram-sha-256"
        )
        # Persist the candidate privately before changing the external credential.
        # If outcome is uncertain, never silently overwrite/rotate it on a retry.
        write_runtime_file(output, generated)
        admin.execute(
            sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                sql.Identifier(ROLE), sql.Literal(verifier.decode("ascii"))
            )
        )
    with connect(**options, user=ROLE + "." + PROJECT, password=generated) as runtime:
        if runtime.execute("SELECT current_user, current_database()").fetchone() != (
            ROLE,
            "postgres",
        ):
            raise SetupUnavailable


def main():
    if len(sys.argv) != 1:
        print(json.dumps({"status": "invalid_arguments"}))
        return 2
    logging.disable(logging.CRITICAL)
    for name in list(os.environ):
        if name.startswith("PG"):
            del os.environ[name]
    try:
        import psycopg

        configure(private_password(INPUT), connect=psycopg.connect)
    except Exception:
        print(json.dumps({"status": "setup_unavailable", "diagnostics": "suppressed"}))
        return 2
    print(
        json.dumps(
            {"status": "runtime_password_set_and_verified", "values": "not_disclosed"}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
