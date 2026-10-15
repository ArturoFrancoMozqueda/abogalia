"""User-operated local key generation; no .env reads, values, or overwrites."""

import json
import os
import secrets
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / ".env.identity-generated"
NAMES = ("ABOGALIA_CSRF_KEY", "ABOGALIA_SESSION_CIPHER_KEY")


def prepare(destination):
    from cryptography.fernet import Fernet

    parent = destination.parent.lstat()
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.getuid():
        raise ValueError("Private key preparation unavailable")
    values = (secrets.token_urlsafe(48), Fernet.generate_key().decode("ascii"))
    payload = "".join(
        f"{name}={value}\n" for name, value in zip(NAMES, values, strict=True)
    )
    fd = os.open(
        destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        os.fchmod(handle.fileno(), 0o600)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def main():
    if len(sys.argv) != 1:
        print(json.dumps({"status": "invalid_arguments"}))
        return 2
    try:
        prepare(DESTINATION)
    except FileExistsError:
        print(json.dumps({"status": "already_exists", "overwritten": False}))
        return 2
    except Exception:
        print(
            json.dumps({"status": "preparation_unavailable", "values": "not_disclosed"})
        )
        return 2
    print(
        json.dumps(
            {"status": "prepared", "variables": NAMES, "values": "not_disclosed"}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
