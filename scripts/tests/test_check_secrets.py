import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "check_secrets", Path(__file__).parents[1] / "check_secrets.py"
)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class ScannerTests(unittest.TestCase):
    def test_report_exposes_only_location_and_rule(self):
        marker = "PUBLIC_SYNTHETIC_" + "DO_NOT_FORWARD"
        payload = json.dumps(
            [
                {
                    "RuleID": "generic-api-key",
                    "File": "docs/sample.md",
                    "StartLine": 3,
                    "Secret": marker,
                    "Match": marker,
                    "Author": marker,
                }
            ]
        ).encode()
        output = scanner.sanitized_findings(payload, {"docs/sample.md"})
        self.assertEqual(
            output, [{"rule": "generic-api-key", "file": "docs/sample.md", "line": 3}]
        )
        self.assertNotIn(marker, json.dumps(output))

    def test_unexpected_report_fails_closed(self):
        for payload in [b"not-json", b"{}", b'[{"RuleID":"x"}]']:
            with self.assertRaises(scanner.ScanError):
                scanner.sanitized_findings(payload)

    def test_location_cannot_inject_or_escape(self):
        for name in ["../sample", "/tmp/sample", "sample\nINJECTED"]:
            payload = json.dumps(
                [{"RuleID": "test", "File": name, "StartLine": 1}]
            ).encode()
            with self.assertRaises(scanner.ScanError):
                scanner.sanitized_findings(payload)

    def test_failure_never_forwards_diagnostics(self):
        marker = "PUBLIC_SYNTHETIC_" + "ERROR_MESSAGE"
        with (
            patch.object(scanner.shutil, "which", return_value="/tmp/fake"),
            patch.object(scanner, "run", side_effect=RuntimeError(marker)),
            patch("sys.argv", ["check_secrets.py"]),
        ):
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = scanner.main()
            self.assertEqual(code, 2)
            self.assertNotIn(marker, stdout.getvalue() + stderr.getvalue())
            self.assertEqual(json.loads(stdout.getvalue())["status"], "scanner_failed")

    def test_inconsistent_exit_code_is_not_a_clean_scan(self):
        with patch.object(
            scanner,
            "run",
            return_value=subprocess.CompletedProcess([], 1, b"[]", b"ignored"),
        ):
            with self.assertRaises(scanner.ScanError):
                scanner.scan("fake", "dir", Path("/tmp"), Path("/tmp/config"))

    def test_private_paths_are_excluded(self):
        for name in ["apps/api/.env.local", "secrets/private.key", ".mcp.json"]:
            self.assertTrue(scanner.private(Path(name)))

    def test_only_reviewed_example_is_included_in_scan(self):
        self.assertFalse(scanner.private(Path(".env.example")))
        self.assertFalse(scanner.private(Path("apps/web/.env.example")))
        self.assertTrue(scanner.private(Path("apps/web/.env.local")))
        self.assertTrue(scanner.private(Path("docs/.env.example")))
        self.assertTrue(scanner.private(Path("apps/api/.env.example")))
        self.assertTrue(scanner.private(Path(".env.local")))

    def test_root_empty_example_in_inventory_but_not_ignored_by_scanner(self):
        with tempfile.TemporaryDirectory() as repo:
            root = Path(repo)
            (root / ".env.example").write_text("ABOGALIA_DATABASE_DSN=\n")
            result = subprocess.CompletedProcess([], 0, b".env.example\0", b"")
            with patch.object(scanner, "run", return_value=result):
                self.assertEqual(scanner.inventory(root), [Path(".env.example")])

    def test_root_other_env_names_tracked_fail_before_read(self):
        for name in (".env", ".env.local", ".env.example.private", "docs/.env.example"):
            result = subprocess.CompletedProcess([], 0, name.encode() + b"\0", b"")
            with (
                patch.object(scanner, "run", return_value=result),
                self.assertRaises(scanner.ScanError),
            ):
                scanner.inventory(Path("/tmp"))

    def test_parent_symlink_cannot_read_external_fixture(self):
        with (
            tempfile.TemporaryDirectory() as repo,
            tempfile.TemporaryDirectory() as external,
        ):
            root, outside = Path(repo), Path(external)
            (outside / "public.txt").write_text("public synthetic fixture")
            (root / "docs").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(scanner.ScanError):
                scanner.confined_file(root, Path("docs/public.txt"))

    def test_tracked_private_path_fails_before_reading(self):
        result = subprocess.CompletedProcess([], 0, b"apps/api/.env\0", b"")
        with patch.object(scanner, "run", return_value=result):
            with self.assertRaises(scanner.ScanError):
                scanner.inventory(Path("/tmp"))

    def test_absolute_scanner_location_normalizes_only_inside_scan_root(self):
        payload = json.dumps(
            [{"RuleID": "test", "File": "/tmp/source/docs/a.md", "StartLine": 1}]
        ).encode()
        self.assertEqual(
            scanner.sanitized_findings(payload, {"docs/a.md"}, Path("/tmp/source"))[0][
                "file"
            ],
            "docs/a.md",
        )
        with self.assertRaises(scanner.ScanError):
            scanner.sanitized_findings(payload, base=Path("/tmp/other"))


if __name__ == "__main__":
    unittest.main()
