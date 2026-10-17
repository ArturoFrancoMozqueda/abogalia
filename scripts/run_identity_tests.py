"""Run Identity tests against a fresh private PostgreSQL with synthetic data only."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def invoke(args, *, env=None, cwd=ROOT):
    return subprocess.run(
        args,
        cwd=cwd,
        env=env or {"PATH": os.defpath, "LANG": "C", "LC_ALL": "C"},
        capture_output=True,
        timeout=180,
        check=False,
    )


def postgres_bin(explicit):
    candidates = [explicit] if explicit else []
    if shutil.which("initdb"):
        candidates.append(Path(shutil.which("initdb")).parent)
    candidates.extend(Path(f"/usr/lib/postgresql/{version}/bin") for version in (18, 17, 16, 15))
    candidates.append(Path("/opt/homebrew/opt/postgresql@16/bin"))
    for candidate in candidates:
        if candidate and all((candidate / name).is_file() for name in ("initdb", "pg_ctl")):
            return candidate
    raise RuntimeError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postgres-bin", type=Path)
    args = parser.parse_args()
    cluster = None
    startup_attempted = False
    result_code = 2
    report = {"status": "test_runner_failed", "diagnostics": "suppressed"}
    try:
        binary = postgres_bin(args.postgres_bin)
        cluster = Path(tempfile.mkdtemp(prefix="abogalia-identity-tests-"))
        cluster.chmod(0o700)
        socket = cluster / "socket"
        socket.mkdir(mode=0o700)
        init = invoke(
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
        if init.returncode:
            raise RuntimeError
        options = (
            f'-k {socket} -p 54983 -h "" '
            "-c log_statement=none -c log_min_error_statement=panic "
            "-c log_parameter_max_length_on_error=0"
        )
        startup_attempted = True
        start = invoke(
            [
                str(binary / "pg_ctl"),
                "-D",
                str(cluster / "data"),
                "-l",
                str(cluster / "server.log"),
                "-o",
                options,
                "-w",
                "start",
            ]
        )
        if start.returncode:
            raise RuntimeError
        env = {
            "PATH": os.defpath,
            "LANG": "C",
            "LC_ALL": "C",
            "PYTHONPATH": str(ROOT / "apps/api/src"),
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PGPASSFILE": os.devnull,
            "ABOGALIA_TEST_POSTGRES_DSN": (
                f"host={socket} port=54983 dbname=postgres user=abogalia_test_owner"
            ),
        }
        tests = invoke([sys.executable, "-m", "pytest", "apps/api/tests", "-q", "--tb=no"], env=env)
        summary = {}
        for line in tests.stdout.decode(errors="replace").splitlines():
            counts = re.findall(r"(\d+) (passed|failed|skipped|errors?|xfailed|xpassed)", line)
            if counts:
                summary = {name: int(count) for count, name in counts}
        report = {
            "status": "passed" if tests.returncode == 0 else "failed",
            "database": "isolated_postgresql",
            "summary": summary,
            "raw_diagnostics": "suppressed",
        }
        result_code = tests.returncode
    except Exception:
        report = {"status": "test_runner_failed", "diagnostics": "suppressed"}
    finally:
        if cluster is not None:
            cleanup_ok = True
            if startup_attempted:
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
                    if stopped.returncode:
                        status = invoke(
                            [str(binary / "pg_ctl"), "-D", str(cluster / "data"), "status"]
                        )
                        cleanup_ok = status.returncode == 3
                except Exception:
                    cleanup_ok = False
            if cleanup_ok:
                try:
                    shutil.rmtree(cluster)
                except Exception:
                    cleanup_ok = False
            if not cleanup_ok:
                result_code = 2
                report = {"status": "test_cluster_cleanup_failed", "diagnostics": "suppressed"}
    print(json.dumps(report))
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
