"""Local synthetic file tests; never read the user's .env or generated keys."""

import importlib.util
import stat
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

SPEC = importlib.util.spec_from_file_location(
    "private_key_preparation",
    Path(__file__).resolve().parents[3] / "scripts/prepare_identity_private_keys.py",
)
PREPARATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARATION)


def test_private_keys_generated_without_overwriting_or_reading_env(tmp_path, capsys):
    private_env = tmp_path / ".env"
    private_env.write_text("PUBLIC_SYNTHETIC_UNTOUCHED")
    destination = tmp_path / ".env.identity-generated"
    PREPARATION.prepare(destination)
    assert stat.S_IMODE(destination.stat().st_mode) == 0o600
    values = dict(line.split("=", 1) for line in destination.read_text().splitlines())
    assert set(values) == set(PREPARATION.NAMES)
    assert len(values["ABOGALIA_CSRF_KEY"].encode()) >= 32
    Fernet(values["ABOGALIA_SESSION_CIPHER_KEY"].encode())
    original = destination.read_bytes()
    with pytest.raises(FileExistsError):
        PREPARATION.prepare(destination)
    assert destination.read_bytes() == original
    assert private_env.read_text() == "PUBLIC_SYNTHETIC_UNTOUCHED"
    assert capsys.readouterr() == ("", "")


def test_existing_symlink_is_not_followed_or_overwritten(tmp_path):
    existing = tmp_path / "existing"
    existing.write_text("PUBLIC_SYNTHETIC_UNTOUCHED")
    destination = tmp_path / ".env.identity-generated"
    destination.symlink_to(existing)
    with pytest.raises(FileExistsError):
        PREPARATION.prepare(destination)
    assert existing.read_text() == "PUBLIC_SYNTHETIC_UNTOUCHED"
