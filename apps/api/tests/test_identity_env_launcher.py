"""Private launcher tests use only temporary synthetic files and mocked serving."""

import asyncio
import importlib.util
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from cryptography.fernet import Fernet

SPEC = importlib.util.spec_from_file_location(
    "identity_env_launcher", Path(__file__).parents[3] / "scripts/dev_identity_api.py"
)
launcher = importlib.util.module_from_spec(SPEC)
# Dataclass resolution requires the module to be registered before execution.

sys.modules[SPEC.name] = launcher
SPEC.loader.exec_module(launcher)


@pytest.fixture(autouse=True)
def restore_logging():
    previous = logging.root.manager.disable
    yield
    logging.disable(previous)


@pytest.fixture
def private_file(tmp_path):
    def create(text=""):
        path = tmp_path / ".env"
        path.write_text(text, encoding="utf-8")
        path.chmod(0o600)
        return path

    return create


def synthetic_values():
    return {
        "ABOGALIA_IDENTITY_ENABLED": "1",
        "ABOGALIA_ENVIRONMENT": "development",
        "ABOGALIA_WEB_ORIGIN": "http://127.0.0.1:5190",
        "ABOGALIA_SUPABASE_URL": launcher.PROJECT,
        "ABOGALIA_SUPABASE_PUBLISHABLE_KEY": "sb_publishable_PUBLIC_SYNTHETIC_ONLY",
        "ABOGALIA_CSRF_KEY": "PUBLIC_SYNTHETIC_ONLY_" * 2,
        "ABOGALIA_SESSION_CIPHER_KEY": Fernet.generate_key().decode(),
        "ABOGALIA_DATABASE_DSN": (
            "host=db.spohytnxscljtitvmdab.supabase.co port=5432 dbname=postgres "
            "user=abogalia_identity_runtime sslmode=verify-full sslrootcert=system"
        ),
    }


def test_missing_and_blank_disable(tmp_path, private_file):
    assert not launcher.parse_private_file(tmp_path / "absent").enabled
    assert not launcher.parse_private_file(private_file()).enabled
    blank = "\n".join(name + "=" for name in launcher.NAMES)
    assert launcher.parse_private_file(private_file(blank)).values == {}


def test_exact_names_spaces_and_comments(private_file):
    path = private_file(
        "# Comment\nABOGALIA_DATABASE_DSN=host=public.invalid user=synthetic dbname=postgres\n"
        "ABOGALIA_IDENTITY_ENABLED=\n"
    )
    configuration = launcher.parse_private_file(path)
    assert len(configuration.values["ABOGALIA_DATABASE_DSN"].split(" ")) == 3
    assert "ABOGALIA_IDENTITY_ENABLED" not in configuration.values
    assert "PUBLIC" not in repr(configuration)


@pytest.mark.parametrize(
    "text",
    [
        "UNAPPROVED=",
        "VITE_PRIVATE=PUBLIC_SYNTHETIC",
        "PGHOST=PUBLIC_SYNTHETIC",
        "ABOGALIA_IDENTITY_ENABLED=0\nABOGALIA_IDENTITY_ENABLED=0",
        "export ABOGALIA_IDENTITY_ENABLED=0",
        "no-assignment",
        "ABOGALIA_CSRF_KEY='PUBLIC_SYNTHETIC'",
        'ABOGALIA_CSRF_KEY="PUBLIC_SYNTHETIC"',
        "ABOGALIA_CSRF_KEY=PUBLIC\nSYNTHETIC",
        "ABOGALIA_CSRF_KEY=PUBLIC\x00SYNTHETIC",
        "ABOGALIA_CSRF_KEY=PUBLIC\rSYNTHETIC",
        "ABOGALIA_CSRF_KEY=PUBLIC\tSYNTHETIC",
    ],
)
def test_restricted_grammar_fail_closed(private_file, text):
    with pytest.raises(launcher.LaunchUnavailable) as caught:
        launcher.parse_private_file(private_file(text))
    assert str(caught.value) == "Identity launcher unavailable"


@pytest.mark.parametrize(
    "payload",
    [
        "$(touch marker)",
        "${OTHER}",
        "`touch marker`",
        "value;touch marker",
        "value|cat",
        "value&cat",
        "value>marker",
        "value<marker",
    ],
)
def test_shell_payload_rejected_never_executed(private_file, payload, tmp_path):
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.parse_private_file(private_file("ABOGALIA_CSRF_KEY=" + payload))
    assert not (tmp_path / "marker").exists()


@pytest.mark.parametrize("mode", [0o644, 0o400, 0o666, 0o700])
def test_permissions_fail_closed(private_file, mode):
    path = private_file()
    path.chmod(mode)
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.parse_private_file(path)


def test_owner_fail_closed(private_file, monkeypatch):
    path = private_file()
    monkeypatch.setattr(launcher.os, "getuid", lambda: -1)
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.parse_private_file(path)


def test_symlink_hardlink_directory_fifo_fail_closed(private_file, tmp_path):
    original = private_file()
    link = tmp_path / "symlink"
    link.symlink_to(original)
    hard = tmp_path / "hardlink"
    os.link(original, hard)
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo, 0o600)
    for path in (link, original, hard, tmp_path, fifo):
        with pytest.raises(launcher.LaunchUnavailable):
            launcher.parse_private_file(path)


def test_size_and_encoding_fail_closed(private_file):
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.parse_private_file(private_file("#" * 32769))
    path = private_file()
    path.write_bytes(b"\xff")
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.parse_private_file(path)


def test_enabled_configuration_validates_without_network(monkeypatch):
    import psycopg

    def forbidden(*_, **__):
        raise AssertionError("Unexpected connection")

    monkeypatch.setattr(psycopg, "connect", forbidden)
    launcher.validate_private_configuration(launcher.PrivateConfiguration(synthetic_values()))


def test_enabled_launcher_from_clean_shell_without_pythonpath(private_file, tmp_path):
    values = synthetic_values()
    path = private_file("\n".join(name + "=" + value for name, value in values.items()))
    program = """
import importlib.util
import sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('clean_launcher', sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
raise SystemExit(module.main([], env_file=Path(sys.argv[2]),
                             factory=lambda: object(), serve=lambda _: None))
"""
    result = subprocess.run(
        [sys.executable, "-c", program, str(SPEC.origin), str(path)],
        cwd=tmp_path,
        env={"PATH": os.defpath},
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"status": "stopped"}
    assert result.stderr == ""


@pytest.mark.parametrize(
    "mutation",
    [
        "origin",
        "project",
        "environment",
        "missing",
        "enabled",
        "email",
        "publishable",
        "cipher",
        "csrf",
        "role",
        "host",
        "hostaddr",
        "options",
        "tls",
        "transaction_port",
    ],
)
def test_invalid_configuration_fail_closed(mutation):
    values = synthetic_values()
    changes = {
        "origin": ("ABOGALIA_WEB_ORIGIN", "http://127.0.0.1:5191"),
        "project": ("ABOGALIA_SUPABASE_URL", "https://unapproved.invalid"),
        "environment": ("ABOGALIA_ENVIRONMENT", "production"),
        "enabled": ("ABOGALIA_IDENTITY_ENABLED", "yes"),
        "email": ("ABOGALIA_AUTH_EMAIL_READY", "yes"),
        "publishable": ("ABOGALIA_SUPABASE_PUBLISHABLE_KEY", "PUBLIC_SYNTHETIC_INVALID"),
        "cipher": ("ABOGALIA_SESSION_CIPHER_KEY", "PUBLIC_SYNTHETIC_INVALID"),
        "csrf": ("ABOGALIA_CSRF_KEY", "PUBLIC"),
    }
    if mutation in changes:
        name, value = changes[mutation]
        values[name] = value
    elif mutation == "missing":
        del values["ABOGALIA_DATABASE_DSN"]
    else:
        dsn = values["ABOGALIA_DATABASE_DSN"]
        replacements = {
            "role": ("abogalia_identity_runtime", "postgres"),
            "host": ("db.spohytnxscljtitvmdab.supabase.co", "unapproved.invalid"),
            "tls": ("verify-full", "require"),
            "transaction_port": ("5432", "6543"),
        }
        if mutation in replacements:
            old, new = replacements[mutation]
            dsn = dsn.replace(old, new)
        else:
            dsn += " " + mutation + "=PUBLIC_SYNTHETIC"
        values["ABOGALIA_DATABASE_DSN"] = dsn
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.validate_private_configuration(launcher.PrivateConfiguration(values))


def test_inherited_configuration_cannot_enable_missing_file(tmp_path, monkeypatch, capsys):
    environment = {
        "ABOGALIA_IDENTITY_ENABLED": "1",
        "ABOGALIA_SUPABASE_URL": "PUBLIC_SYNTHETIC",
        "PGHOSTADDR": "PUBLIC_SYNTHETIC",
        "PGSERVICE": "PUBLIC_SYNTHETIC",
    }
    monkeypatch.setattr(launcher.os, "environ", environment)
    observed = []

    def factory():
        assert environment == {"ABOGALIA_IDENTITY_ENABLED": "0", "PGPASSFILE": os.devnull}
        observed.append(True)
        return object()

    assert (
        launcher.main([], env_file=tmp_path / "absent", factory=factory, serve=lambda _: None) == 0
    )
    assert observed == [True]
    assert json.loads(capsys.readouterr().out) == {"status": "stopped"}


def test_library_diagnostics_and_exception_suppressed(private_file, monkeypatch, capsys):
    monkeypatch.setattr(launcher.os, "environ", {})

    def factory():
        print("PUBLIC_SYNTHETIC_DIAGNOSTIC")
        print("PUBLIC_SYNTHETIC_DIAGNOSTIC", file=sys.stderr)
        logging.error("PUBLIC_SYNTHETIC_DIAGNOSTIC")
        raise RuntimeError("PUBLIC_SYNTHETIC_EXCEPTION")

    assert launcher.main([], env_file=private_file(), factory=factory, serve=lambda _: None) == 2
    output = capsys.readouterr()
    assert output.err == ""
    assert json.loads(output.out) == {"status": "launcher_unavailable"}


def test_invalid_cli_input_not_echoed(capsys):
    assert launcher.main(["--PUBLIC_SYNTHETIC\nINPUT"]) == 2
    output = capsys.readouterr()
    assert output.err == ""
    assert json.loads(output.out) == {"status": "invalid_arguments"}


def test_cached_global_app_denied(monkeypatch):
    monkeypatch.setitem(sys.modules, "abogalia_api.main", object())
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.build_app()


def test_uvicorn_configuration(monkeypatch):
    import uvicorn

    observed = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **options: observed.append(options))
    launcher.serve_app(object())
    assert observed == [
        {
            "host": "127.0.0.1",
            "port": 8090,
            "reload": False,
            "workers": 1,
            "access_log": False,
            "log_config": None,
            "log_level": "critical",
        }
    ]


def test_fresh_real_app_with_empty_file_ignores_inherited_identity(
    private_file, monkeypatch, capsys
):
    monkeypatch.setattr(launcher.os, "environ", synthetic_values())
    monkeypatch.delitem(sys.modules, "abogalia_api.main", raising=False)
    observed = []

    def serve(app):
        assert app.state.identity.settings.configured is False

        async def verify():
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://local.invalid",
                trust_env=False,
            ) as client:
                assert (await client.get("/api/health")).status_code == 200
                assert (await client.get("/api/auth/session")).json() == {"authenticated": False}

        asyncio.run(verify())
        observed.append(True)

    assert launcher.main([], env_file=private_file(), serve=serve) == 0
    assert observed == [True]
    assert json.loads(capsys.readouterr().out) == {"status": "stopped"}


@pytest.mark.parametrize(
    "hostname", ["aws-0-us-east-1.pooler.supabase.com", "aws-1-us-east-1.pooler.supabase.com"]
)
def test_session_pooler_role_bound_to_project(hostname):
    values = synthetic_values()
    for name, role in (("ABOGALIA_DATABASE_DSN", "abogalia_identity_runtime"),):
        values[name] = (
            f"host={hostname} port=5432 dbname=postgres "
            f"user={role}.spohytnxscljtitvmdab sslmode=verify-full"
        )
    launcher.validate_private_configuration(launcher.PrivateConfiguration(values))


def test_pooler_other_project_denied():
    values = synthetic_values()
    values["ABOGALIA_DATABASE_DSN"] = (
        "host=aws-0-us-east-1.pooler.supabase.com port=5432 dbname=postgres "
        "user=abogalia_identity_runtime.unapproved sslmode=verify-full"
    )
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.validate_private_configuration(launcher.PrivateConfiguration(values))


def test_native_fd_diagnostics_suppressed(private_file, monkeypatch, capfd):
    monkeypatch.setattr(launcher.os, "environ", {})

    def factory():
        os.write(1, b"PUBLIC_SYNTHETIC_NATIVE_OUTPUT\n")
        os.write(2, b"PUBLIC_SYNTHETIC_NATIVE_ERROR\n")
        raise RuntimeError("PUBLIC_SYNTHETIC_EXCEPTION")

    assert launcher.main([], env_file=private_file(), factory=factory) == 2
    output = capfd.readouterr()
    assert output.err == ""
    assert json.loads(output.out) == {"status": "launcher_unavailable"}
    os.write(1, b"PUBLIC_SYNTHETIC_RESTORED\n")
    assert capfd.readouterr().out == "PUBLIC_SYNTHETIC_RESTORED\n"


@pytest.mark.parametrize("kind", ["auth", "direct", "pooler"])
def test_retired_project_cannot_be_launched(kind):
    values = synthetic_values()
    if kind == "auth":
        values["ABOGALIA_SUPABASE_URL"] = "https://xggefantvuwpilksfdoy.supabase.co"
    elif kind == "direct":
        values["ABOGALIA_DATABASE_DSN"] = values["ABOGALIA_DATABASE_DSN"].replace(
            "spohytnxscljtitvmdab", "xggefantvuwpilksfdoy"
        )
    else:
        values["ABOGALIA_DATABASE_DSN"] = (
            "host=aws-0-us-east-1.pooler.supabase.com port=5432 dbname=postgres "
            "user=abogalia_identity_runtime.xggefantvuwpilksfdoy sslmode=verify-full"
        )
    with pytest.raises(launcher.LaunchUnavailable):
        launcher.validate_private_configuration(launcher.PrivateConfiguration(values))


def test_http_launcher_accepts_legacy_name_but_never_injects_its_value():
    values = synthetic_values()
    values["ABOGALIA_AUTH_SESSION_CHECK_DSN"] = "PUBLIC_SYNTHETIC_UNUSED"
    configuration = launcher.PrivateConfiguration(values)
    launcher.validate_private_configuration(configuration)
    environment = {"ABOGALIA_AUTH_SESSION_CHECK_DSN": "PUBLIC_SYNTHETIC_INHERITED"}
    launcher.install_environment(configuration, environment)
    assert "ABOGALIA_AUTH_SESSION_CHECK_DSN" not in environment
    assert environment["ABOGALIA_IDENTITY_ENABLED"] == "1"
