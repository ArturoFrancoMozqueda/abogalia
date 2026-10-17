"""Independent runner failure tests. No PostgreSQL, secrets or inherited credentials."""

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "identity_test_runner", Path(__file__).parents[1] / "run_identity_tests.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

MARKER = "PUBLIC_SYNTHETIC_DIAGNOSTIC_DO_NOT_FORWARD"


class IdentityRunnerTests(unittest.TestCase):
    def run_scenario(self, *, init=0, start=0, stop=0, status=0, tests=0, removal_error=False):
        """Exercise main with synthetic process results and an owned temporary tree."""
        with tempfile.TemporaryDirectory(prefix="abogalia-runner-unit-") as owned:
            cluster = Path(owned) / "cluster"
            cluster.mkdir()
            calls, environments, removed = [], [], []

            def invoke(args, *, env=None, **kwargs):
                if Path(args[0]).name == "initdb":
                    action, outcome = "init", init
                elif Path(args[0]).name == "pg_ctl":
                    action = args[-1]
                    outcome = {"start": start, "stop": stop, "status": status}[action]
                else:
                    action, outcome = "tests", tests
                    environments.append(env)
                calls.append((action, args))
                if isinstance(outcome, Exception):
                    raise outcome
                output = ("17 passed\n" + MARKER).encode() if action == "tests" else MARKER.encode()
                return subprocess.CompletedProcess(args, outcome, output, MARKER.encode())

            def remove(path):
                calls.append(("remove", path))
                removed.append(path)
                if removal_error:
                    raise OSError(MARKER)

            with (
                patch.object(runner, "postgres_bin", return_value=Path("/synthetic/pg/bin")),
                patch.object(runner.tempfile, "mkdtemp", return_value=str(cluster)),
                patch.object(runner, "invoke", side_effect=invoke),
                patch.object(runner.shutil, "rmtree", side_effect=remove),
                patch("sys.argv", ["run_identity_tests.py"]),
            ):
                stdout, stderr = io.StringIO(), io.StringIO()
                with (
                    contextlib.redirect_stdout(stdout),
                    contextlib.redirect_stderr(stderr),
                ):
                    result = runner.main()
            # Return only test metadata; never provider/session/credential values.
            lines = stdout.getvalue().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertNotIn(MARKER, stdout.getvalue() + stderr.getvalue())
            self.assertEqual(stderr.getvalue(), "")
            return (
                result,
                json.loads(lines[0]),
                calls,
                environments,
                removed,
                cluster.stat().st_mode,
            )

    def test_success_emitted_only_after_cleanup_and_private_unix_configuration(self):
        result, report, calls, environments, removed, mode = self.run_scenario()
        self.assertEqual(result, 0)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["summary"], {"passed": 17})
        self.assertEqual([name for name, _ in calls], ["init", "start", "tests", "stop", "remove"])
        self.assertEqual(len(removed), 1)
        self.assertEqual(mode & 0o777, 0o700)
        start = next(args for name, args in calls if name == "start")
        options = start[start.index("-o") + 1]
        self.assertIn('-h ""', options)
        self.assertIn("log_parameter_max_length_on_error=0", options)
        self.assertEqual(environments[0]["PGPASSFILE"], os.devnull)
        self.assertNotIn("PGPASSWORD", environments[0])

    def test_start_timeout_attempts_stop_before_removal(self):
        timeout = subprocess.TimeoutExpired("synthetic", 1, output=MARKER.encode())
        result, report, calls, _, removed, _ = self.run_scenario(start=timeout)
        self.assertEqual(result, 2)
        self.assertEqual(report["status"], "test_runner_failed")
        self.assertEqual([name for name, _ in calls], ["init", "start", "stop", "remove"])
        self.assertEqual(len(removed), 1)

    def test_start_failure_stop_failure_but_status_not_running_allows_removal(self):
        result, report, calls, _, removed, _ = self.run_scenario(start=1, stop=1, status=3)
        self.assertEqual(result, 2)
        self.assertEqual(report["status"], "test_runner_failed")
        self.assertEqual([name for name, _ in calls], ["init", "start", "stop", "status", "remove"])
        self.assertEqual(len(removed), 1)

    def test_failed_stop_and_live_status_preserve_cluster_and_do_not_report_passed(
        self,
    ):
        result, report, calls, _, removed, _ = self.run_scenario(stop=1, status=0)
        self.assertEqual(result, 2)
        self.assertEqual(
            report,
            {"status": "test_cluster_cleanup_failed", "diagnostics": "suppressed"},
        )
        self.assertEqual([name for name, _ in calls][-2:], ["stop", "status"])
        self.assertFalse(removed)

    def test_failed_stop_with_unknown_status_preserves_cluster(self):
        result, report, _, _, removed, _ = self.run_scenario(stop=1, status=4)
        self.assertEqual(result, 2)
        self.assertEqual(report["status"], "test_cluster_cleanup_failed")
        self.assertFalse(removed)

    def test_stop_exception_is_suppressed_and_cluster_preserved(self):
        result, report, _, _, removed, _ = self.run_scenario(stop=OSError(MARKER))
        self.assertEqual(result, 2)
        self.assertEqual(report["status"], "test_cluster_cleanup_failed")
        self.assertFalse(removed)

    def test_status_exception_is_suppressed_and_cluster_preserved(self):
        result, report, _, _, removed, _ = self.run_scenario(stop=1, status=OSError(MARKER))
        self.assertEqual(result, 2)
        self.assertEqual(report["status"], "test_cluster_cleanup_failed")
        self.assertFalse(removed)

    def test_removal_exception_has_single_failure_report_and_no_traceback(self):
        result, report, _, _, removed, _ = self.run_scenario(removal_error=True)
        self.assertEqual(result, 2)
        self.assertEqual(report["status"], "test_cluster_cleanup_failed")
        self.assertNotIn("summary", report)
        self.assertEqual(len(removed), 1)

    def test_failed_init_removes_owned_tree_without_attempting_server_stop(self):
        result, report, calls, _, _, _ = self.run_scenario(init=1)
        self.assertEqual(result, 2)
        self.assertEqual(report["status"], "test_runner_failed")
        self.assertEqual([name for name, _ in calls], ["init", "remove"])

    def test_pytest_failure_or_timeout_is_sanitized_and_still_cleans_up(self):
        for outcome, expected in (
            (1, "failed"),
            (OSError(MARKER), "test_runner_failed"),
        ):
            with self.subTest(kind=expected):
                result, report, calls, _, _, _ = self.run_scenario(tests=outcome)
                self.assertIn(result, (1, 2))
                self.assertEqual(report["status"], expected)
                self.assertEqual([name for name, _ in calls][-2:], ["stop", "remove"])

    def test_test_child_environment_is_closed_and_has_only_synthetic_local_destination(
        self,
    ):
        _, _, _, environments, _, _ = self.run_scenario()
        env = environments[0]
        self.assertEqual(
            set(env),
            {
                "PATH",
                "LANG",
                "LC_ALL",
                "PYTHONPATH",
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
                "PGPASSFILE",
                "ABOGALIA_TEST_POSTGRES_DSN",
            },
        )
        self.assertEqual(env["PGPASSFILE"], os.devnull)
        self.assertIn(
            "dbname=postgres user=abogalia_test_owner",
            env["ABOGALIA_TEST_POSTGRES_DSN"],
        )
        self.assertNotIn("password", env["ABOGALIA_TEST_POSTGRES_DSN"])

    def test_invoke_never_inherits_environment_and_captures_both_outputs(self):
        with patch.object(runner.subprocess, "run") as child:
            runner.invoke(["synthetic-child"])
        self.assertEqual(
            child.call_args.kwargs["env"],
            {
                "PATH": os.defpath,
                "LANG": "C",
                "LC_ALL": "C",
            },
        )
        self.assertTrue(child.call_args.kwargs["capture_output"])
        self.assertFalse(child.call_args.kwargs["check"])
        self.assertGreater(child.call_args.kwargs["timeout"], 0)


if __name__ == "__main__":
    unittest.main()
