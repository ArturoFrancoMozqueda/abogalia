"""Construct explicit Abogalia runtime dependencies without reading dotenv files."""

import os
import stat
from pathlib import Path

from psycopg.conninfo import conninfo_to_dict

from abogalia_api.identity.config import Settings

PROJECT_REF = "spohytnxscljtitvmdab"
ROLES = ("abogalia_identity_runtime", "abogalia_identity_probe")
POOLER_HOSTS = (
    "aws-0-us-east-1.pooler.supabase.com",
    "aws-1-us-east-1.pooler.supabase.com",
)
REMOTE_FIELDS = {
    "host",
    "port",
    "dbname",
    "user",
    "password",
    "sslmode",
    "sslrootcert",
    "connect_timeout",
}


def _local_fixture(parts, role):
    if (
        set(parts) != {"host", "port", "dbname", "user"}
        or parts["dbname"] != "abogalia_storage_test"
        or parts["user"] != role
        or not parts["port"].isascii()
        or not parts["port"].isdigit()
        or not 1024 < int(parts["port"]) < 65536
    ):
        raise ValueError
    socket = Path(parts["host"])
    if (
        not socket.is_absolute()
        or socket.name != "socket"
        or not socket.parent.name.startswith("abogalia-identity-tests-")
        or socket.is_symlink()
        or socket.parent.is_symlink()
    ):
        raise ValueError
    for directory in (socket, socket.parent):
        metadata = directory.stat()
        if (
            not stat.S_ISDIR(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o700
            or metadata.st_uid != os.getuid()
        ):
            raise ValueError


def validate_dsn(value: str, role: str, *, allow_local_fixture: bool = False) -> None:
    """Remote by default; isolated fixture opt-in is never exposed by runtime/env."""
    try:
        if role not in ROLES or any(
            name.startswith("PG") and name != "PGPASSFILE" for name in os.environ.keys()
        ):
            raise ValueError
        parts = conninfo_to_dict(value)
        if allow_local_fixture is not False:
            if allow_local_fixture is not True:
                raise ValueError
            _local_fixture(parts, role)
            return
        if (
            set(parts) - REMOTE_FIELDS
            or not all(parts.get(name) for name in ("host", "dbname", "user"))
            or parts["dbname"] != "postgres"
            or parts.get("port", "5432") != "5432"
            or parts.get("sslmode") != "verify-full"
        ):
            raise ValueError
        direct = parts["host"] == "db." + PROJECT_REF + ".supabase.co" and parts["user"] == role
        pooled = parts["host"] in POOLER_HOSTS and parts["user"] == role + "." + PROJECT_REF
        if not (direct or pooled):
            raise ValueError
    except Exception:
        raise ValueError("Identity runtime configuration unavailable") from None


def load_runtime():
    if os.environ.get("ABOGALIA_IDENTITY_ENABLED") != "1":
        return Settings(), None, None
    required = (
        "ABOGALIA_WEB_ORIGIN",
        "ABOGALIA_SUPABASE_URL",
        "ABOGALIA_SUPABASE_PUBLISHABLE_KEY",
        "ABOGALIA_CSRF_KEY",
        "ABOGALIA_DATABASE_DSN",
        "ABOGALIA_SESSION_CIPHER_KEY",
        "ABOGALIA_AUTH_SESSION_CHECK_DSN",
    )
    if not all(os.environ.get(name) for name in required):
        raise RuntimeError("Identity runtime configuration unavailable")
    try:
        from abogalia_api.identity.storage import PostgresSessionProbe, PostgresSessionStore

        validate_dsn(os.environ["ABOGALIA_DATABASE_DSN"], "abogalia_identity_runtime")
        validate_dsn(os.environ["ABOGALIA_AUTH_SESSION_CHECK_DSN"], "abogalia_identity_probe")
        settings = Settings(
            origin=os.environ["ABOGALIA_WEB_ORIGIN"],
            development_http=os.environ.get("ABOGALIA_ENVIRONMENT") == "development",
            project_url=os.environ["ABOGALIA_SUPABASE_URL"],
            publishable_key=os.environ["ABOGALIA_SUPABASE_PUBLISHABLE_KEY"],
            csrf_key=os.environ["ABOGALIA_CSRF_KEY"].encode(),
            email_enabled=os.environ.get("ABOGALIA_AUTH_EMAIL_READY") == "1",
        )
        store = PostgresSessionStore(
            os.environ["ABOGALIA_DATABASE_DSN"],
            os.environ["ABOGALIA_SESSION_CIPHER_KEY"].encode(),
        )
        probe = PostgresSessionProbe(os.environ["ABOGALIA_AUTH_SESSION_CHECK_DSN"])
        return settings, store, probe
    except Exception:
        raise RuntimeError("Identity runtime configuration unavailable") from None
