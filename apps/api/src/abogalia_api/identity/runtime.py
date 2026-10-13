"""Construct explicit Abogalia runtime dependencies without reading dotenv files."""

import os

from psycopg.conninfo import conninfo_to_dict

from abogalia_api.identity.config import Settings


def validate_dsn(value: str, role: str) -> None:
    parts = conninfo_to_dict(value)
    if not all(parts.get(name) for name in ("host", "dbname", "user")):
        raise ValueError
    if any(name in parts for name in ("service", "options", "passfile")):
        raise ValueError
    # Direct connections or the explicitly qualified Abogalia pooler user.
    if parts["user"] not in (role, role + ".xggefantvuwpilksfdoy"):
        raise ValueError


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
