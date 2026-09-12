#!/usr/bin/env python3
"""Build a deterministic, upload-ready Astria plugin archive."""

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "astria"


def main():
    output_directory = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else ROOT / "dist"
    if len(sys.argv) > 2:
        raise SystemExit("Usage: scripts/build-plugin.py [output-directory]")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate-plugin.py")], check=True)
    version = json.loads((PLUGIN_ROOT / "plugin.json").read_text(encoding="utf-8"))["version"]
    output_directory.mkdir(parents=True, exist_ok=True)
    archive = output_directory / f"astria-{version}.zip"

    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(PLUGIN_ROOT.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(PLUGIN_ROOT).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            bundle.writestr(info, path.read_bytes())

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(f"Built {archive}")
    print(f"SHA-256 {digest}")


if __name__ == "__main__":
    main()
