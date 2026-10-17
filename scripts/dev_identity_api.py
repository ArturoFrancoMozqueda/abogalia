"""Private, fixed-file launcher for approved local Legalia Identity development."""

import contextlib
import importlib
import json
import logging
import os
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
NAMES = frozenset(
    (
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
)
REQUIRED = NAMES - {"ABOGALIA_AUTH_EMAIL_READY", "ABOGALIA_AUTH_SESSION_CHECK_DSN"}
PROJECT = "https://spohytnxscljtitvmdab.supabase.co"


class LaunchUnavailable(Exception):
    def __init__(self):
        super().__init__("Identity launcher unavailable")


@dataclass(repr=False)
class PrivateConfiguration:
    values: dict[str, str] = field(repr=False)

    @property
    def enabled(self):
        return self.values.get("ABOGALIA_IDENTITY_ENABLED") == "1"


def parse_private_file(path):
    """Never execute, interpolate, log or include content in an exception."""
    fd = None
    try:
        # O_NONBLOCK prevents a malicious FIFO from hanging before fstat.
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        before = os.fstat(fd)
        if (
            not stat.S_ISREG(before.st_mode)
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_uid != os.getuid()
            or before.st_nlink != 1
            or before.st_size > 32768
        ):
            raise LaunchUnavailable
        with os.fdopen(fd, "rb") as source:
            fd = None
            payload = source.read(32769)
            after = os.fstat(source.fileno())
        if (
            len(payload) > 32768
            or before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
        ):
            raise LaunchUnavailable
        text = payload.decode("utf-8")
        if "\x00" in text or "\r" in text:
            raise LaunchUnavailable
        values = {}
        seen = set()
        for line in text.split("\n"):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            name, separator, value = line.partition("=")
            name = name.strip()
            value = value.strip()
            if (
                not separator
                or name not in NAMES
                or name in seen
                or any(character in value for character in "$`;|&<>")
                or value.startswith(("'", '"'))
                or value.endswith(("'", '"'))
                or any(ord(character) < 32 for character in value)
            ):
                raise LaunchUnavailable
            seen.add(name)
            if value:
                values[name] = value
        return PrivateConfiguration(values)
    except FileNotFoundError:
        return PrivateConfiguration({})
    except Exception:
        raise LaunchUnavailable from None
    finally:
        if fd is not None:
            os.close(fd)


def validate_private_configuration(configuration):
    values = configuration.values
    try:
        if values.get("ABOGALIA_IDENTITY_ENABLED", "0") not in ("0", "1"):
            raise ValueError
        if values.get("ABOGALIA_AUTH_EMAIL_READY", "0") not in ("0", "1"):
            raise ValueError
        if not configuration.enabled:
            return
        if (
            not REQUIRED <= values.keys()
            or values["ABOGALIA_ENVIRONMENT"] != "development"
            or values["ABOGALIA_WEB_ORIGIN"] != "http://127.0.0.1:5190"
            or values["ABOGALIA_SUPABASE_URL"] != PROJECT
        ):
            raise ValueError
        from abogalia_api.identity.config import Settings
        from abogalia_api.identity.runtime import validate_dsn
        from cryptography.fernet import Fernet
        from psycopg.conninfo import conninfo_to_dict

        Settings(
            origin=values["ABOGALIA_WEB_ORIGIN"],
            development_http=True,
            project_url=values["ABOGALIA_SUPABASE_URL"],
            publishable_key=values["ABOGALIA_SUPABASE_PUBLISHABLE_KEY"],
            csrf_key=values["ABOGALIA_CSRF_KEY"].encode(),
            email_enabled=values.get("ABOGALIA_AUTH_EMAIL_READY") == "1",
        )
        Fernet(values["ABOGALIA_SESSION_CIPHER_KEY"].encode())
        for name, role in (("ABOGALIA_DATABASE_DSN", "abogalia_identity_runtime"),):
            value = values[name]
            validate_dsn(value, role)
            parts = conninfo_to_dict(value)
            direct = (
                parts.get("host") == "db.spohytnxscljtitvmdab.supabase.co"
                and parts.get("user") == role
            )
            pooled = (
                parts.get("host")
                in (
                    "aws-0-us-east-1.pooler.supabase.com",
                    "aws-1-us-east-1.pooler.supabase.com",
                )
                and parts.get("user") == role + ".spohytnxscljtitvmdab"
            )
            if (
                not (direct or pooled)
                or parts.get("dbname") != "postgres"
                or parts.get("sslmode") != "verify-full"
                or set(parts)
                - {
                    "host",
                    "port",
                    "dbname",
                    "user",
                    "password",
                    "sslmode",
                    "sslrootcert",
                    "connect_timeout",
                }
                or parts.get("port", "5432") != "5432"
            ):
                raise ValueError
    except Exception:
        raise LaunchUnavailable from None


def install_environment(configuration, environment=None):
    """Dedicated process: remove inherited product/libpq settings without reading them."""
    environment = os.environ if environment is None else environment
    for name in list(environment.keys()):
        if name.startswith(("ABOGALIA_", "PG")):
            del environment[name]
    if configuration.enabled:
        environment.update(
            {
                name: value
                for name, value in configuration.values.items()
                if name != "ABOGALIA_AUTH_SESSION_CHECK_DSN"
            }
        )
    else:
        environment["ABOGALIA_IDENTITY_ENABLED"] = "0"
    environment["PGPASSFILE"] = os.devnull


def build_app():
    # A cached global app could have been created with different credentials.
    if "abogalia_api.main" in sys.modules:
        raise LaunchUnavailable
    sys.path.insert(0, str(ROOT / "apps/api/src"))
    return importlib.import_module("abogalia_api.main").app


def serve_app(app):
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8090,
        reload=False,
        workers=1,
        access_log=False,
        log_config=None,
        log_level="critical",
    )


@contextlib.contextmanager
def silent_diagnostics():
    """Suppress Python streams and native FD writes, restoring both on exit."""
    saved = []
    restoration_failed = False
    with open(os.devnull, "w") as silent:
        try:
            for stream in (sys.stdout, sys.stderr):
                stream.flush()
            for number in (1, 2):
                saved.append((number, os.dup(number)))
                os.dup2(silent.fileno(), number)
            with contextlib.redirect_stdout(silent), contextlib.redirect_stderr(silent):
                yield
        finally:
            for number, original in saved:
                try:
                    os.dup2(original, number)
                except OSError:
                    restoration_failed = True
                finally:
                    os.close(original)
            if restoration_failed:
                raise LaunchUnavailable from None


def main(argv=None, *, env_file=ENV_FILE, factory=None, serve=None):
    if list(sys.argv[1:] if argv is None else argv):
        print(json.dumps({"status": "invalid_arguments"}))
        return 2
    try:
        # This process suppresses library diagnostics for the entire server lifetime.
        logging.disable(sys.maxsize)
        with silent_diagnostics():
            configuration = parse_private_file(env_file)
            sys.path.insert(0, str(ROOT / "apps/api/src"))
            validate_private_configuration(configuration)
            install_environment(configuration)
            app = (factory or build_app)()
            (serve or serve_app)(app)
        status, code = "stopped", 0
    except KeyboardInterrupt:
        status, code = "stopped", 0
    except (Exception, SystemExit):
        status, code = "launcher_unavailable", 2
    print(json.dumps({"status": status}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
