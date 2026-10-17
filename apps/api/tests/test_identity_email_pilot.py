"""Synthetic private pilot inputs and mock HTTP only; never real mail/configuration."""

import importlib.util
import json
import os
from pathlib import Path

import httpx
import pytest

SPEC = importlib.util.spec_from_file_location(
    "email_pilot", Path(__file__).parents[3] / "scripts/run_identity_email_pilot.py"
)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)
MAIL = "public-synthetic@example.invalid"
PASSWORD = "PUBLIC_SYNTHETIC_PASSWORD_ONLY"


@pytest.fixture
def setup(tmp_path):
    directory = tmp_path / "pilot"
    config = tmp_path / "private-config"
    config.write_text(
        "ABOGALIA_SUPABASE_PUBLISHABLE_KEY=sb_publishable_PUBLIC_SYNTHETIC\nOTHER=PUBLIC_UNREAD_CONFIGURATION\n"
    )
    config.chmod(0o600)
    now = [1000]
    calls = []

    def invoke(action, inputs, factory=None):
        answers = iter(inputs)
        return pilot.run(
            action,
            directory=directory,
            env_file=config,
            prompt=lambda _: next(answers),
            clock=lambda: now[0],
            factory=factory or mocked,
        )

    def transport(request):
        calls.append(request)
        return httpx.Response(200, json={"user": {"id": "PUBLIC_SYNTHETIC_USER"}})

    def mocked(key):
        return pilot.provider_factory(key, transport=httpx.MockTransport(transport))

    return directory, config, now, calls, invoke


def initialize(setup):
    return setup[-1]("initialize", [MAIL, "LISTO"])


def test_initialize_no_network_plaintext_or_overwrite(setup):
    directory, _, _, calls, invoke = setup
    assert initialize(setup) == {"status": "initialized", "reserved": 0}
    content = (directory / "authorization.json").read_text()
    assert MAIL not in content and PASSWORD not in content and not calls
    assert directory.stat().st_mode & 0o777 == 0o700
    assert (directory / "authorization.json").stat().st_mode & 0o777 == 0o600
    with pytest.raises((pilot.PilotUnavailable, FileExistsError)):
        initialize(setup)
    assert invoke("recover", [MAIL])["reserved"] == 1


def test_marker_assertion_required_before_any_request(setup):
    directory, _, _, calls, invoke = setup
    with pytest.raises(pilot.PilotUnavailable):
        invoke("initialize", [MAIL, "NO"])
    assert not calls and not (directory / "authorization.json").exists()
    with pytest.raises((pilot.PilotUnavailable, FileNotFoundError)):
        invoke("signup", [MAIL, PASSWORD])
    assert not calls


def test_signup_recover_fixed_transport_and_no_global_ready(setup, monkeypatch):
    _, _, now, calls, invoke = setup
    monkeypatch.setenv("ABOGALIA_AUTH_EMAIL_READY", "0")
    initialize(setup)
    assert invoke("signup", [MAIL, PASSWORD]) == {"status": "accepted", "reserved": 1}
    now[0] += 60
    assert invoke("recover", [MAIL]) == {"status": "accepted", "reserved": 2}
    assert [str(call.url) for call in calls] == [
        "https://spohytnxscljtitvmdab.supabase.co/auth/v1/signup",
        "https://spohytnxscljtitvmdab.supabase.co/auth/v1/recover",
    ]
    assert json.loads(calls[0].content) == {"email": MAIL, "password": PASSWORD}
    assert json.loads(calls[1].content) == {"email": MAIL}
    assert os.environ["ABOGALIA_AUTH_EMAIL_READY"] == "0"


@pytest.mark.parametrize(
    "mutation", ["mailbox", "expired", "future", "smtp", "permissions", "symlink"]
)
def test_bad_marker_or_mailbox_never_sends(setup, mutation):
    directory, _, now, calls, invoke = setup
    initialize(setup)
    marker = directory / "authorization.json"
    if mutation == "expired":
        now[0] += pilot.TTL
    elif mutation == "future":
        now[0] -= 1
    elif mutation == "smtp":
        data = json.loads(marker.read_text())
        data["smtp_ready"] = False
        marker.write_text(json.dumps(data))
    elif mutation == "permissions":
        marker.chmod(0o644)
    elif mutation == "symlink":
        target = directory / "other"
        marker.rename(target)
        marker.symlink_to(target)
    mailbox = "other-public@example.invalid" if mutation == "mailbox" else MAIL
    with pytest.raises((pilot.PilotUnavailable, OSError)):
        invoke("recover", [mailbox])
    assert not calls


def test_reservation_durable_before_request_timeout_and_no_retry(setup):
    directory, _, now, calls, invoke = setup
    initialize(setup)

    def factory(key):
        def timeout(request):
            assert json.loads((directory / "authorization.json").read_text())["reserved"] == 1
            calls.append(request)
            raise httpx.ReadTimeout("PUBLIC_SYNTHETIC_FAILURE")

        return pilot.provider_factory(key, transport=httpx.MockTransport(timeout))

    assert invoke("recover", [MAIL], factory) == {"status": "request_failed", "reserved": 1}
    assert len(calls) == 1
    with pytest.raises(pilot.PilotUnavailable):
        invoke("recover", [MAIL])
    now[0] += 60
    assert invoke("recover", [MAIL])["reserved"] == 2


def test_cap_and_lock_do_not_allow_extra_request(setup):
    directory, _, now, calls, invoke = setup
    initialize(setup)
    with pilot.marker_lock(directory):
        with pytest.raises(BlockingIOError):
            invoke("recover", [MAIL])
    for count in range(1, 7):
        assert invoke("recover", [MAIL])["reserved"] == count
        now[0] += 60
    with pytest.raises(pilot.PilotUnavailable):
        invoke("recover", [MAIL])
    assert len(calls) == 6
    now[0] += pilot.TTL
    with pytest.raises((pilot.PilotUnavailable, FileExistsError)):
        initialize(setup)


def test_marker_failure_never_requests_or_truncates_hardlink(setup, monkeypatch):
    directory, _, _, calls, invoke = setup
    initialize(setup)
    marker = directory / "authorization.json"
    before = marker.read_bytes()
    os.link(marker, directory / "hardlink")
    with pytest.raises(pilot.PilotUnavailable):
        invoke("recover", [MAIL])
    assert not calls and marker.read_bytes() == before
    (directory / "hardlink").unlink()
    monkeypatch.setattr(
        pilot.os, "fsync", lambda _: (_ for _ in ()).throw(OSError("PUBLIC_SYNTHETIC_FAILURE"))
    )
    with pytest.raises(OSError):
        invoke("recover", [MAIL])
    assert not calls


@pytest.mark.parametrize(
    "result", [{"access_token": "PUBLIC_SYNTHETIC_TOKEN"}, {"session": {"PUBLIC": True}}]
)
def test_unexpected_session_discarded(setup, result):
    _, _, _, _, invoke = setup
    initialize(setup)

    def factory(key):
        return pilot.provider_factory(
            key, transport=httpx.MockTransport(lambda _: httpx.Response(200, json=result))
        )

    output = invoke("signup", [MAIL, PASSWORD], factory)
    assert output == {"status": "request_failed", "reserved": 1}
    assert "PUBLIC" not in json.dumps(output)


def test_env_public_field_only_and_private_permissions(setup):
    _, config, _, calls, invoke = setup
    initialize(setup)
    assert pilot.publishable_key(config) == "sb_publishable_PUBLIC_SYNTHETIC"
    config.chmod(0o644)
    with pytest.raises(pilot.PilotUnavailable):
        invoke("recover", [MAIL])
    assert not calls


def test_tty_required_unknown_arguments_redacted(monkeypatch, capsys):
    monkeypatch.setattr(pilot.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(pilot, "private_prompt", lambda _: pytest.fail("No prompt allowed"))
    assert pilot.main(["--signup"]) == 2
    assert pilot.main(["--PUBLIC_SYNTHETIC\nVALUE"]) == 2
    output = capsys.readouterr()
    assert output.err == "" and "PUBLIC_SYNTHETIC" not in output.out


def test_expiry_during_password_input_never_reserves(setup):
    directory, config, now, calls, _ = setup
    initialize(setup)

    def prompt(message):
        if message.startswith("Contraseña"):
            now[0] += pilot.TTL
            return PASSWORD
        return MAIL

    with pytest.raises(pilot.PilotUnavailable):
        pilot.run(
            "signup",
            directory=directory,
            env_file=config,
            prompt=prompt,
            clock=lambda: now[0],
            factory=lambda _: pytest.fail("No request allowed"),
        )
    assert not calls and json.loads((directory / "authorization.json").read_text())["reserved"] == 0


def test_initialize_syncs_parent_before_marker_and_success(setup, monkeypatch):
    directory, _, _, calls, _ = setup
    original = pilot.os.fsync
    events = []

    def observe(fd):
        inode = os.fstat(fd).st_ino
        if inode == directory.parent.stat().st_ino:
            assert not (directory / "authorization.json").exists()
            assert not (directory / "lock").exists()
            events.append("parent")
        elif inode == directory.stat().st_ino:
            events.append("directory")
        else:
            events.append("marker")
        original(fd)

    monkeypatch.setattr(pilot.os, "fsync", observe)
    assert initialize(setup) == {"status": "initialized", "reserved": 0}
    assert events == ["parent", "marker", "directory"]
    assert not calls


def test_parent_sync_failure_closes_fd_and_blocks_marker_and_requests(setup, monkeypatch):
    directory, _, _, calls, invoke = setup
    original = pilot.os.fsync
    parent_attempts = []
    failed_fds = []

    def fail_once(fd):
        if os.fstat(fd).st_ino == directory.parent.stat().st_ino:
            parent_attempts.append(True)
            if len(parent_attempts) == 1:
                failed_fds.append(fd)
                raise OSError("PUBLIC_SYNTHETIC_SYNC_FAILURE")
        original(fd)

    monkeypatch.setattr(pilot.os, "fsync", fail_once)
    with pytest.raises(OSError):
        initialize(setup)
    with pytest.raises(OSError):
        os.fstat(failed_fds[0])
    assert not (directory / "authorization.json").exists()
    assert not (directory / "lock").exists()
    with pytest.raises(FileNotFoundError):
        invoke("recover", [MAIL])
    assert not calls
    # Existing directory from the failed attempt must be synced on retry too.
    assert initialize(setup) == {"status": "initialized", "reserved": 0}
    assert len(parent_attempts) == 2 and not calls


def test_retired_project_marker_rejected_before_request(setup):
    directory, _, _, calls, invoke = setup
    initialize(setup)
    marker = directory / "authorization.json"
    data = json.loads(marker.read_text())
    data["project"] = "https://xggefantvuwpilksfdoy.supabase.co"
    marker.write_text(json.dumps(data))
    with pytest.raises(pilot.PilotUnavailable):
        invoke("recover", [MAIL])
    assert not calls
    assert json.loads(marker.read_text())["reserved"] == 0
