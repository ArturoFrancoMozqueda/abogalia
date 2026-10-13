"""Run a pinned scanner without forwarding source, values or raw diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import string
import subprocess
import tempfile
from pathlib import Path

VERSION = "8.30.1"
ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {
    ".gitignore",
    ".node-version",
    ".python-version",
    "AGENTS.md",
    "README.md",
    "Makefile",
    "biome.json",
    "package.json",
    "pnpm-lock.yaml",
    "pnpm-workspace.yaml",
}
DIRECTORIES = {"apps", "docs", "scripts", ".github", "supabase"}
PRIVATE_NAMES = {".mcp.json", ".netrc", ".npmrc", "credentials", "id_rsa", "id_ed25519"}
PUBLIC_EXAMPLES = {Path("apps/web/.env.example")}


class ScanError(Exception):
    """Deliberately has no underlying diagnostic attached."""


def run(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess:
    # Do not forward runtime credentials or scanner override environment variables.
    env = {"PATH": os.defpath, "LANG": "C", "LC_ALL": "C"}
    try:
        return subprocess.run(args, cwd=cwd, env=env, capture_output=True, timeout=180, check=False)
    except (OSError, subprocess.SubprocessError):
        raise ScanError from None


def private(path: Path) -> bool:
    if path in PUBLIC_EXAMPLES:
        return False
    return any(
        part.startswith(".env")
        or part in PRIVATE_NAMES
        or part.endswith((".pem", ".key", ".p12", ".pfx"))
        for part in path.parts
    )


def confined_file(root: Path, relative: Path) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise ScanError
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ScanError
    if not current.resolve().is_relative_to(root.resolve()):
        raise ScanError
    return current


def inventory(root: Path) -> list[Path]:
    tracked_result = run(["git", "ls-files", "-z", "--cached"], cwd=root)
    if tracked_result.returncode:
        raise ScanError
    tracked = set(tracked_result.stdout.decode().split("\0")) - {""}
    result = run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
    )
    if result.returncode:
        raise ScanError
    files = []
    for name in sorted(set(result.stdout.decode().split("\0")) - {""}):
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ScanError
        if private(relative):
            if name in tracked:
                raise ScanError
            continue
        if relative.parts[0] not in DIRECTORIES and name not in ROOT_FILES:
            raise ScanError
        path = confined_file(root, relative)
        if not path.exists():  # Deleted tracked file.
            continue
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 20_000_000:
            raise ScanError
        files.append(relative)
    return files


def sanitized_findings(
    payload: bytes, allowed: set[str] | None = None, base: Path | None = None
) -> list[dict]:
    try:
        values = json.loads(payload)
        if not isinstance(values, list):
            raise ScanError
        findings = []
        for item in values:
            rule, name, line = item["RuleID"], item["File"], item["StartLine"]
            if not isinstance(rule, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", rule):
                raise ScanError
            if not isinstance(name, str) or not isinstance(line, int) or line < 1:
                raise ScanError
            if Path(name).is_absolute() and base is not None:
                name = str(Path(name).relative_to(base))
            if (
                any(ord(char) < 32 for char in name)
                or Path(name).is_absolute()
                or ".." in Path(name).parts
            ):
                raise ScanError
            name = name.removeprefix("./")
            if allowed is not None and name not in allowed:
                raise ScanError
            findings.append({"rule": rule, "file": name, "line": line})
        return findings
    except (ValueError, KeyError, TypeError, UnicodeError):
        raise ScanError from None


def scan(binary: str, mode: str, target: Path, config: Path, allowed=None) -> list[dict]:
    args = [
        binary,
        mode,
        "--redact=100",
        "--no-banner",
        "--no-color",
        "--ignore-gitleaks-allow",
        "--gitleaks-ignore-path",
        str(config.parent / "no-ignore"),
        "--config",
        str(config),
        "--report-format",
        "json",
        "--report-path",
        "-",
        "--log-level",
        "error",
        "--max-decode-depth",
        "5",
    ]
    if mode == "git":
        args.extend(["--log-opts=--all"])
    args.append(str(target))
    result = run(args, cwd=target)
    if result.returncode not in (0, 1):
        raise ScanError
    findings = sanitized_findings(result.stdout, allowed, target)
    if (result.returncode == 1) != bool(findings):
        raise ScanError
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", default="gitleaks")
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()
    try:
        binary = shutil.which(args.binary)
        if binary is None:
            raise ScanError
        version = run([binary, "version"], cwd=ROOT)
        if version.returncode or version.stdout.decode().strip() != VERSION:
            raise ScanError
        with tempfile.TemporaryDirectory(prefix="abogalia-scan-") as temporary:
            temp = Path(temporary)
            config = temp / "scanner.toml"
            config.write_text("[extend]\nuseDefault = true\n")
            copy = temp / "source"
            copy.mkdir()
            if args.self_test:
                marker = "ghp_" + "".join(
                    secrets.choice(string.ascii_letters + string.digits) for _ in range(36)
                )
                canary = copy / "synthetic.txt"
                canary.write_text('token = "' + marker + '"\n')
                detected = scan(binary, "dir", copy, config, {"synthetic.txt"})
                if not detected:
                    raise ScanError
                canary.unlink()
                if scan(binary, "dir", copy, config, set()):
                    raise ScanError
                print('{"status":"self_test_passed","positive":true,"negative":true}')
                return 0
            files = inventory(ROOT)
            if args.artifact:
                requested = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
                relative = requested.relative_to(ROOT)
                artifact = confined_file(ROOT, relative)
                if relative != Path("apps/web/build/client") or not artifact.is_dir():
                    raise ScanError
                files = []
                for path in artifact.rglob("*"):
                    confined_file(ROOT, path.relative_to(ROOT))
                    if path.is_symlink():
                        raise ScanError
                    if path.is_file():
                        if private(path.relative_to(ROOT)) or path.stat().st_size > 20_000_000:
                            raise ScanError
                        files.append(path.relative_to(ROOT))
            for relative in files:
                dest = copy / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(confined_file(ROOT, relative), dest)
            findings = scan(binary, "dir", copy, config, {str(path) for path in files})
            if args.history:
                findings += scan(binary, "git", ROOT, config)
            for finding in findings:
                print(json.dumps(finding, ensure_ascii=True))
            print(
                json.dumps(
                    {
                        "status": "findings" if findings else "passed",
                        "files": len(files),
                        "findings": len(findings),
                        "history": args.history,
                        "scanner": VERSION,
                    }
                )
            )
            return 1 if findings else 0
    except Exception:
        # No exception message, traceback, stdout/stderr or report is forwarded.
        print('{"status":"scanner_failed","diagnostics":"suppressed"}')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
