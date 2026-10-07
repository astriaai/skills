#!/usr/bin/env python3
"""Build a deterministic, upload-ready Astria plugin archive."""

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", nargs="?", type=Path, default=ROOT / "dist")
    parser.add_argument("--target", choices=("openai", "claude"), default="openai")
    args = parser.parse_args()
    output_directory = args.output_directory.resolve()
    plugin_root = ROOT / "plugins" / ("astria-claude" if args.target == "claude" else "astria")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate-plugin.py")], check=True)
    manifest = plugin_root / (".claude-plugin/plugin.json" if args.target == "claude" else "plugin.json")
    version = json.loads(manifest.read_text(encoding="utf-8"))["version"]
    output_directory.mkdir(parents=True, exist_ok=True)
    prefix = "astria-claude" if args.target == "claude" else "astria"
    archive = output_directory / f"{prefix}-{version}.zip"

    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(plugin_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(plugin_root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            payload = path.read_bytes()
            if args.target == "openai" and relative == "plugin.json":
                metadata = json.loads(payload)
                metadata["name"] = "astria-mcp"
                payload = (json.dumps(metadata, indent=2) + "\n").encode("utf-8")
            bundle.writestr(info, payload)

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(f"Built {archive}")
    print(f"SHA-256 {digest}")


if __name__ == "__main__":
    main()
