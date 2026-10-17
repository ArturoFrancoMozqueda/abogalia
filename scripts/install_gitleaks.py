"""Install only a fixed official release after checking its published checksum."""

import argparse
import hashlib
import platform
import tarfile
import tempfile
import urllib.request
from pathlib import Path

VERSION = "8.30.1"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        systems = {"Darwin": "darwin", "Linux": "linux"}
        arches = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x64"}
        asset = (
            f"gitleaks_{VERSION}_{systems[platform.system()]}_{arches[platform.machine()]}.tar.gz"
        )
        base = f"https://github.com/gitleaks/gitleaks/releases/download/v{VERSION}/"
        with urllib.request.urlopen(
            base + f"gitleaks_{VERSION}_checksums.txt", timeout=30
        ) as response:
            checksums = response.read().decode()
        expected = next(
            line.split()[0] for line in checksums.splitlines() if line.split()[-1] == asset
        )
        with urllib.request.urlopen(base + asset, timeout=30) as response:
            payload = response.read()
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError
        with tempfile.TemporaryDirectory(prefix="abogalia-release-") as temp:
            archive = Path(temp) / "release.tar.gz"
            archive.write_bytes(payload)
            with tarfile.open(archive) as tar:
                member = tar.getmember("gitleaks")
                if not member.isfile():
                    raise ValueError
                binary = tar.extractfile(member).read()
            args.destination.mkdir(parents=True, exist_ok=True)
            path = args.destination / "gitleaks"
            if path.is_symlink():
                raise ValueError
            path.write_bytes(binary)
            path.chmod(0o700)
        print(f"Gitleaks {VERSION}: official checksum verified; installed.")
        return 0
    except Exception:
        print("Gitleaks installation failed; diagnostics suppressed.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
