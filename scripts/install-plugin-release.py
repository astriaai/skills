#!/usr/bin/env python3
"""Download and verify a release marketplace; optionally register it with Codex."""

import argparse
import hashlib
import io
import json
import re
import shlex
import shutil
import stat
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


REPOSITORY = "astriaai/skills"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent": "astria-plugin-installer"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def extract_verified(payload, checksum, destination):
    fields = checksum.split()
    if not fields or not re.fullmatch(r"[0-9a-f]{64}", fields[0]):
        raise ValueError("invalid release checksum")
    if hashlib.sha256(payload).hexdigest() != fields[0]:
        raise ValueError("release archive does not match its checksum")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for member in archive.infolist():
            path = PurePosixPath(member.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in member.filename:
                raise ValueError("release archive contains an unsafe path")
            if stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError("release archive contains a symlink")
        archive.extractall(destination)
        for member in archive.infolist():
            path = destination / member.filename
            if path.is_file() and member.external_attr >> 16 & 0o111:
                path.chmod(0o755)
    for manifest in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json",
                     ".grok-plugin/marketplace.json", ".cursor-plugin/marketplace.json"):
        if not (destination / manifest).is_file():
            raise ValueError(f"release marketplace is missing {manifest}")


def install(version, destination):
    if not SEMVER.fullmatch(version):
        raise ValueError("version must be semantic version without the v prefix")
    # Never replace an installed version or an existing user directory.
    if destination.exists():
        raise ValueError(f"destination already exists; choose a new --directory: {destination}")
    name = f"astria-marketplace-{version}.zip"
    base = f"https://github.com/{REPOSITORY}/releases/download/v{version}"
    payload = download(f"{base}/{name}")
    checksum = download(f"{base}/{name}.sha256").decode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".astria-release-", dir=destination.parent) as temporary:
        staged = Path(temporary) / "marketplace"
        staged.mkdir()
        extract_verified(payload, checksum, staged)
        staged.rename(destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="semantic version; defaults to the latest published release")
    parser.add_argument("--directory", type=Path, help="persistent destination (must not exist)")
    parser.add_argument("--register-codex", action="store_true", help="register this local marketplace and install astria@astria")
    args = parser.parse_args()
    if args.register_codex and shutil.which("codex") is None:
        parser.error("codex is required for --register-codex")
    version = args.version
    if version is None:
        release = json.loads(download(f"https://api.github.com/repos/{REPOSITORY}/releases/latest"))
        version = release["tag_name"].removeprefix("v")
    destination = (args.directory or Path.home() / ".local/share/astria/plugins" / version).expanduser().resolve()
    try:
        install(version, destination)
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, f"install-plugin-release: {error}\n")
    print(f"Verified and extracted Astria {version} to {destination}")
    if args.register_codex:
        # An existing Git marketplace may require migration in the host's settings.
        subprocess.run(["codex", "plugin", "marketplace", "add", str(destination)], check=True)
        subprocess.run(["codex", "plugin", "add", "astria@astria"], check=True)
    else:
        print(f"Codex: codex plugin marketplace add {shlex.quote(str(destination))}")
        print("       codex plugin add astria@astria")
    print(f"Claude Code: /plugin marketplace add {destination}")
    print("             /plugin install astria@astria")
    print(f"Grok Build: grok plugin install {shlex.quote(str(destination / 'plugins/astria-grok'))} --trust")
    print(f"Cursor: copy {destination / 'plugins/astria-grok'} to ~/.cursor/plugins/local/astria/")


if __name__ == "__main__":
    main()
