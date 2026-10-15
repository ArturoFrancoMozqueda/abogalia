"""Fixed single-process production entrypoint; runtime injection only, no dotenv."""

import contextlib
import importlib
import ipaddress
import json
import logging
import os
import re
import sys
from urllib.parse import urlsplit

CA_PATH = "/app/certificates/supabase-prod-ca-2021.crt"
PROJECT = "https://spohytnxscljtitvmdab.supabase.co"


class ProductionUnavailable(Exception):
    def __init__(self):
        super().__init__("Production configuration unavailable")


def validate_environment():
    """Consume injected values internally; never return configuration or diagnostics."""
    try:
        if (
            os.environ.get("ABOGALIA_ENVIRONMENT") != "production"
            or os.environ.get("ABOGALIA_IDENTITY_ENABLED") not in ("0", "1")
            or os.environ.get("ABOGALIA_AUTH_EMAIL_READY", "0") not in ("0", "1")
            or os.environ.get("WEB_CONCURRENCY", "1") != "1"
            or any(name.startswith("UVICORN_") for name in os.environ)
            or any(name in os.environ for name in ("GUNICORN_CMD_ARGS", "FORWARDED_ALLOW_IPS"))
            or any(name.startswith("PG") and name != "PGPASSFILE" for name in os.environ)
        ):
            raise ProductionUnavailable
        origin = os.environ.get("ABOGALIA_WEB_ORIGIN", "")
        parsed = urlsplit(origin)
        host = parsed.hostname or ""
        if (
            parsed.scheme != "https"
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path
            or parsed.port not in (None, 443)
            or parsed.netloc not in (host, host + ":443")
            or origin != "https://" + parsed.netloc
            or not host.isascii()
            or host != host.lower()
            or len(host) > 253
            or "." not in host
            or any(
                not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
                for label in host.split(".")
            )
        ):
            raise ProductionUnavailable
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise ProductionUnavailable
        if os.environ["ABOGALIA_IDENTITY_ENABLED"] == "0":
            return
        from cryptography.fernet import Fernet
        from psycopg.conninfo import conninfo_to_dict

        from abogalia_api.identity.config import Settings
        from abogalia_api.identity.runtime import validate_dsn
        from abogalia_api.identity.storage import _credentials

        if os.environ.get("ABOGALIA_SUPABASE_URL") != PROJECT:
            raise ProductionUnavailable
        settings = Settings(
            origin=origin,
            development_http=False,
            project_url=PROJECT,
            publishable_key=os.environ["ABOGALIA_SUPABASE_PUBLISHABLE_KEY"],
            csrf_key=os.environ["ABOGALIA_CSRF_KEY"].encode(),
            email_enabled=os.environ.get("ABOGALIA_AUTH_EMAIL_READY") == "1",
        )
        if not settings.configured:
            raise ProductionUnavailable
        dsn = os.environ["ABOGALIA_DATABASE_DSN"]
        validate_dsn(dsn, "abogalia_identity_runtime")
        parts = conninfo_to_dict(dsn)
        if parts.get("sslrootcert") != CA_PATH or not parts.get("password"):
            raise ProductionUnavailable
        _credentials(dsn)  # Includes the minimum libpq16 guard; does not connect.
        Fernet(os.environ["ABOGALIA_SESSION_CIPHER_KEY"].encode())
    except Exception:
        raise ProductionUnavailable from None


def build_app():
    if "abogalia_api.main" in sys.modules:
        raise ProductionUnavailable
    module = importlib.import_module("abogalia_api.main")
    if os.environ["ABOGALIA_IDENTITY_ENABLED"] == "1":
        app = module.app
    else:
        from abogalia_api.identity.config import Settings

        app = module.create_app(
            settings=Settings(origin=os.environ["ABOGALIA_WEB_ORIGIN"], development_http=False)
        )
    # Exact API paths avoid implicit redirects built from the internal HTTP scheme.
    app.router.redirect_slashes = False
    if app.debug or app.state.identity.settings.development_http:
        raise ProductionUnavailable
    return app


def serve_app(app):
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        workers=1,
        reload=False,
        access_log=False,
        log_config=None,
        log_level="critical",
        env_file=None,
        proxy_headers=False,
        forwarded_allow_ips="",
        server_header=False,
    )


@contextlib.contextmanager
def silent_diagnostics():
    saved = []
    failed = False
    with open(os.devnull, "w") as sink:
        try:
            for stream in (sys.stdout, sys.stderr):
                stream.flush()
            for number in (1, 2):
                saved.append((number, os.dup(number)))
                os.dup2(sink.fileno(), number)
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                yield
        finally:
            for number, original in saved:
                try:
                    os.dup2(original, number)
                except OSError:
                    failed = True
                finally:
                    os.close(original)
            if failed:
                raise ProductionUnavailable from None


def main(argv=None, *, factory=None, serve=None):
    status, code = "production_unavailable", 2
    previous = logging.root.manager.disable
    try:
        logging.disable(sys.maxsize)
        with silent_diagnostics():
            if list(sys.argv[1:] if argv is None else argv):
                raise ProductionUnavailable
            validate_environment()
            (serve or serve_app)((factory or build_app)())
        status, code = "stopped", 0
    except KeyboardInterrupt:
        status, code = "stopped", 0
    except (Exception, SystemExit):
        pass
    finally:
        logging.disable(previous)
    print(json.dumps({"status": status}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
