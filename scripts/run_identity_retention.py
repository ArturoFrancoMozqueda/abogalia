"""Local synthetic Identity retention only; read-only preview unless explicitly applied."""

import argparse
import json
import os
import stat
import sys
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RetentionError(Exception):
    """Fixed diagnostic boundary; never include configuration or database values."""


class ProfessionalSchemaUnavailable(RetentionError):
    def __init__(self, status):
        self.status = status if status in ("absent", "partial") else "unavailable"
        super().__init__("Professional retention schema unavailable")


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise RetentionError from None


def local_dsn(source):
    from psycopg.conninfo import conninfo_to_dict, make_conninfo

    parts = conninfo_to_dict(source or "")
    if (
        set(parts) != {"host", "port", "dbname", "user"}
        or parts["dbname"] != "postgres"
        or parts["user"] != "abogalia_test_owner"
        or not 1024 < int(parts["port"]) < 65536
    ):
        raise RetentionError
    socket = Path(parts["host"])
    if (
        not socket.is_absolute()
        or not socket.is_dir()
        or socket.is_symlink()
        or socket.parent.is_symlink()
        or socket.name != "socket"
        or not socket.parent.name.startswith("abogalia-identity-tests-")
    ):
        raise RetentionError
    for path in (socket, socket.parent):
        metadata = path.stat()
        if metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o700:
            raise RetentionError
    return make_conninfo(
        **(
            parts
            | {
                "dbname": "abogalia_storage_test",
                "password": "",
                "passfile": os.devnull,
            }
        )
    )


def preview(dsn, now):
    import psycopg
    from abogalia_api.identity.storage import (
        ABSOLUTE,
        INACTIVE,
        PostgresIdentityMaintenance,
        _credentials,
        _require_role,
    )

    with psycopg.connect(  # noqa: SIM117 - Explicit connection/transaction lifecycle.
        dsn, autocommit=True, connect_timeout=5, **_credentials(dsn)
    ) as conn:
        with conn.transaction():
            conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            conn.execute("SET LOCAL ROLE abogalia_identity_owner")
            conn.execute("SET LOCAL statement_timeout = '10s'")
            conn.execute("SET LOCAL lock_timeout = '5s'")
            _require_role(conn, "abogalia_identity_owner")
            # Reject TCP-enabled clusters and unexpected ownership before any data query.
            if conn.execute("SHOW listen_addresses").fetchone()[0] != "":
                raise RetentionError
            owner = conn.execute(
                "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = current_database()"
            ).fetchone()[0]
            if owner != "abogalia_identity_owner":
                raise RetentionError
            schema = PostgresIdentityMaintenance.professional_schema(conn)
            if schema != "ready":
                raise ProfessionalSchemaUnavailable(schema)
            sessions = conn.execute(
                "SELECT count(*) FROM identity.app_sessions WHERE created_at <= %s "
                "OR last_activity_at <= %s OR subject IN "
                "(SELECT subject FROM identity.users WHERE state != 'active')",
                (now - ABSOLUTE, now - INACTIVE),
            ).fetchone()[0]
            blocked = conn.execute(
                "SELECT count(*) FROM identity.users WHERE state = 'closed' AND closed_at <= %s",
                (now - timedelta(days=30),),
            ).fetchone()[0]
            events = conn.execute(
                "SELECT count(*) FROM identity.audit WHERE occurred_at <= %s",
                (now - timedelta(days=90),),
            ).fetchone()[0]
            professional_drafts = conn.execute(
                "SELECT count(*) FROM identity.professional_drafts WHERE "
                "COALESCE(withdrawn_at,profile_updated_at)<=%s",
                (now - timedelta(days=30),),
            ).fetchone()[0]
            professional_events = conn.execute(
                "SELECT count(*) FROM identity.professional_events WHERE occurred_at<=%s",
                (now - timedelta(days=90),),
            ).fetchone()[0]
            dependencies = conn.execute(
                "SELECT count(*) FROM identity.users u WHERE state='closed' AND closed_at<=%s "
                "AND EXISTS(SELECT 1 FROM identity.professional_drafts d WHERE d.owner_user_id=u.subject "
                "AND COALESCE(d.withdrawn_at,d.profile_updated_at)>%s)",
                (now - timedelta(days=30), now - timedelta(days=30)),
            ).fetchone()[0]
            return {
                "sessions": sessions,
                "accounts": 0,
                "audit_events": events,
                "blocked_accounts": blocked,
                "retention_compliant": blocked == 0,
                "professional_drafts": professional_drafts,
                "professional_events": professional_events,
                "blocked_accounts_missing_proof": blocked,
                "blocked_accounts_dependencies": dependencies,
                "professional_schema": "ready",
            }


def run(argv=None, *, environ=None, clock=None):
    try:
        parser = Parser(description=__doc__, allow_abbrev=False)
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--isolated-local", action="store_true")
        args = parser.parse_args(argv)
        if args.apply and not args.isolated_local:
            raise RetentionError
        environment = os.environ if environ is None else environ
        # Reject implicit libpq hostaddr/service/options without reading values.
        if any(name.startswith("PG") and name != "PGPASSFILE" for name in os.environ):
            raise RetentionError
        if any(name.startswith("PG") and name != "PGPASSFILE" for name in environment):
            raise RetentionError
        source = environment.get("ABOGALIA_TEST_POSTGRES_DSN")
        dsn = local_dsn(source)
        now = (clock or (lambda: datetime.now(UTC)))()
        if now.tzinfo is None or now.utcoffset() is None:
            raise RetentionError
        counts = preview(dsn, now)
        if args.apply:
            from abogalia_api.identity.storage import PostgresIdentityMaintenance
            from psycopg.conninfo import make_conninfo

            owner_dsn = make_conninfo(dsn, options="-c role=abogalia_identity_owner")
            # No subject assertion or Auth evidence is accepted by this tool.
            counts = asdict(
                PostgresIdentityMaintenance(owner_dsn, lambda: now).purge(
                    retired_subjects=set()
                )
            )
        return {
            "status": "applied" if args.apply else "dry_run",
            "scope": "isolated_local_synthetic",
            "counts": counts,
            "diagnostics": "suppressed",
        }, (3 if args.apply and not counts["retention_compliant"] else 0)
    except ProfessionalSchemaUnavailable as error:
        return {
            "status": "professional_schema_unavailable",
            "professional_schema": error.status,
            "diagnostics": "suppressed",
        }, 2
    except Exception:  # noqa: BLE001 - Boundary emits fixed metadata only.
        return {"status": "retention_runner_failed", "diagnostics": "suppressed"}, 2


def main():
    sys.path.insert(0, str(ROOT / "apps/api/src"))
    report, code = run()
    print(json.dumps(report))
    return code


if __name__ == "__main__":
    with open(os.devnull, "w") as diagnostic_sink:
        os.dup2(diagnostic_sink.fileno(), 2)
        raise SystemExit(main())
