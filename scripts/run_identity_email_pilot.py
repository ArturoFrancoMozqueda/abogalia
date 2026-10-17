"""One-shot private email pilot; fixed project, one mailbox, six reserved requests."""

import argparse
import fcntl
import getpass
import hashlib
import importlib.util
import json
import logging
import os
import re
import stat
import sys
import time
import warnings
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "https://spohytnxscljtitvmdab.supabase.co"
CAP = 6
TTL = 86400


class PilotUnavailable(Exception):
    def __init__(self):
        super().__init__("Email pilot unavailable")


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise PilotUnavailable from None


def mailbox_hash(mailbox):
    mailbox = mailbox.strip().lower()
    if len(mailbox) > 254 or not re.fullmatch(
        r"[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9.-]+\.[a-z]{2,}", mailbox
    ):
        raise PilotUnavailable
    if mailbox.endswith("@resend.dev"):
        raise PilotUnavailable
    return mailbox, hashlib.sha256(mailbox.encode()).hexdigest()


def private_fd(path, flags):
    fd = os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        metadata = os.fstat(fd)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o600
            or metadata.st_uid != os.getuid()
            or metadata.st_nlink != 1
            or metadata.st_size > 32768
        ):
            raise PilotUnavailable
        return fd
    except Exception:  # noqa: BLE001 - Never expose filesystem details.
        os.close(fd)
        raise PilotUnavailable from None


def private_directory(path, initialize):
    if initialize:
        try:
            path.mkdir(mode=0o700)
        except FileExistsError:
            pass
    metadata = path.lstat()
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o700
        or metadata.st_uid != os.getuid()
    ):
        raise PilotUnavailable
    if initialize:
        # Persist the new directory entry before creating authorization. Also
        # sync on a retry after mkdir succeeded but its first fsync failed.
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


@contextmanager
def marker_lock(directory, initialize=False):
    private_directory(directory, initialize)
    fd = private_fd(directory / "lock", os.O_RDWR | os.O_CREAT)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def write_marker(directory, data, initialize=False):
    flags = os.O_WRONLY | (os.O_CREAT | os.O_EXCL if initialize else 0)
    fd = private_fd(directory / "authorization.json", flags)
    os.ftruncate(fd, 0)
    with os.fdopen(fd, "w") as file:
        json.dump(data, file, separators=(",", ":"))
        file.flush()
        os.fsync(file.fileno())
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read_marker(directory, now):
    fd = private_fd(directory / "authorization.json", os.O_RDONLY)
    with os.fdopen(fd) as file:
        payload = file.read(32769)
        if len(payload) > 32768:
            raise PilotUnavailable
        data = json.loads(payload)
    if (
        set(data)
        != {
            "scope",
            "project",
            "mailbox_hash",
            "created",
            "expires",
            "reserved",
            "last",
            "smtp_ready",
        }
        or data["scope"] != "identity-pilot"
        or data["project"] != PROJECT
        or data["smtp_ready"] is not True
        or not isinstance(data["mailbox_hash"], str)
        or not re.fullmatch(r"[0-9a-f]{64}", data["mailbox_hash"])
        or any(
            type(data[key]) is not int
            for key in ("created", "expires", "reserved", "last")
        )
        or data["expires"] - data["created"] != TTL
        or not data["created"] <= now < data["expires"]
        or not 0 <= data["reserved"] <= CAP
        or (data["reserved"] == 0 and data["last"] != 0)
        or (data["reserved"] > 0 and not data["created"] <= data["last"] <= now)
    ):
        raise PilotUnavailable
    return data


def publishable_key(path):
    # Parse only this named public field. Other private values are not decoded,
    # validated, returned, installed into the environment or passed to providers.
    fd = private_fd(path, os.O_RDONLY)
    with os.fdopen(fd, "rb") as file:
        payload = file.read(32769)
    if len(payload) > 32768:
        raise PilotUnavailable
    selected = []
    for line in payload.splitlines():
        name, separator, value = line.partition(b"=")
        if name.strip() == b"ABOGALIA_SUPABASE_PUBLISHABLE_KEY" and separator:
            selected.append(value.strip())
    if len(selected) != 1 or not re.fullmatch(
        rb"sb_publishable_[A-Za-z0-9_-]+", selected[0]
    ):
        raise PilotUnavailable
    return selected[0].decode("ascii")


def provider_factory(key, transport=None):
    import httpx
    from abogalia_api.identity.config import Settings
    from abogalia_api.identity.provider import ProviderFailure, SupabaseProvider

    class PilotProvider(SupabaseProvider):
        def _request(self, method, path, **kwargs):
            if method != "POST" or path not in ("/signup", "/recover"):
                raise ProviderFailure()
            result = super()._request(method, path, **kwargs)
            if any(
                result.get(name)
                for name in ("access_token", "refresh_token", "session")
            ):
                raise ProviderFailure()
            return result

    # This ephemeral adapter has no API, session store or global runtime flags.
    settings = Settings(
        origin="http://127.0.0.1:5190",
        development_http=True,
        project_url=PROJECT,
        publishable_key=key,
        csrf_key=os.urandom(32),
        email_enabled=True,
    )
    client = httpx.Client(
        timeout=10, follow_redirects=False, trust_env=False, transport=transport
    )
    return PilotProvider(settings, client)


def launcher_helpers():
    spec = importlib.util.spec_from_file_location(
        "private_pilot_launcher", ROOT / "scripts/dev_identity_api.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def private_prompt(message):
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        return getpass.getpass(message)


def run(
    action,
    *,
    directory,
    env_file,
    prompt=private_prompt,
    clock=time.time,
    factory=provider_factory,
):
    if action not in ("initialize", "signup", "recover"):
        raise PilotUnavailable
    mailbox, digest = mailbox_hash(prompt("Buzón autorizado (entrada oculta): "))
    with marker_lock(directory, initialize=action == "initialize"):
        now = int(clock())
        if action == "initialize":
            if (
                prompt(
                    "Custom SMTP propio y buzón autorizado; Confirm/Reset solo Token, "
                    "OTP600/6d, pausa60 y JWT900 verificados; escribe LISTO (oculto): "
                )
                != "LISTO"
            ):
                raise PilotUnavailable
            write_marker(
                directory,
                {
                    "scope": "identity-pilot",
                    "project": PROJECT,
                    "mailbox_hash": digest,
                    "created": now,
                    "expires": now + TTL,
                    "reserved": 0,
                    "last": 0,
                    "smtp_ready": True,
                },
                initialize=True,
            )
            return {"status": "initialized", "reserved": 0}
        data = read_marker(directory, now)
        if digest != data["mailbox_hash"] or data["reserved"] >= CAP:
            raise PilotUnavailable
        if data["reserved"] and now - data["last"] < 60:
            raise PilotUnavailable
        key = publishable_key(env_file)
        password = (
            prompt("Contraseña para registro (entrada oculta): ")
            if action == "signup"
            else None
        )
        if password is not None and (
            not 8 <= len(password) <= 256 or any(ord(char) < 32 for char in password)
        ):
            raise PilotUnavailable
        now = int(clock())
        if not data["created"] <= now < data["expires"] or (
            data["reserved"] and now - data["last"] < 60
        ):
            raise PilotUnavailable
        data["reserved"] += 1
        data["last"] = now
        write_marker(directory, data)
        try:
            provider = factory(key)
            try:
                if action == "signup":
                    provider.register(mailbox, password)
                elif action == "recover":
                    provider.recover(mailbox)
                else:
                    raise PilotUnavailable
            finally:
                provider.client.close()
            status = "accepted"
        except Exception:  # noqa: BLE001 - Never echo provider values or exception codes.
            status = "request_failed"
        finally:
            password, mailbox, key = None, None, None
        return {"status": status, "reserved": data["reserved"]}


def main(argv=None):
    try:
        parser = Parser(description=__doc__, allow_abbrev=False)
        group = parser.add_mutually_exclusive_group(required=True)
        for action in ("initialize", "signup", "recover"):
            group.add_argument("--" + action, action="store_true")
        args = parser.parse_args(argv)
        # getpass must never fall back to echoing stdin inside tools or pipelines.
        if not sys.stdin.isatty() or not sys.stderr.isatty():
            raise PilotUnavailable
        sys.path.insert(0, str(ROOT / "apps/api/src"))
        helpers = launcher_helpers()
        logging.disable(sys.maxsize)
        # Prompts use /dev/tty through getpass; all library/native output is hidden.
        with helpers.silent_diagnostics():
            result = run(
                next(
                    action
                    for action in ("initialize", "signup", "recover")
                    if getattr(args, action)
                ),
                directory=ROOT / ".identity-pilot",
                env_file=ROOT / ".env",
            )
        result["diagnostics"] = "suppressed"
        code = 0 if result["status"] in ("initialized", "accepted") else 2
    except (Exception, KeyboardInterrupt):  # noqa: BLE001 - Fixed private-operation boundary.
        result, code = {"status": "pilot_unavailable", "diagnostics": "suppressed"}, 2
    print(json.dumps(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
