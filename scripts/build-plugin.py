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
    parser.add_argument("--target", choices=("openai", "openai-skills-only", "openai-studio", "claude", "grok", "marketplace"), default="openai")
    args = parser.parse_args()
    output_directory = args.output_directory.resolve()
    targets = {
        "openai": ("astria", "plugin.json"),
        "openai-skills-only": ("astria-skills-only", "plugin.json"),
        "openai-studio": ("astria-studio", "plugin.json"),
        "claude": ("astria-claude", ".claude-plugin/plugin.json"),
        "grok": ("astria-grok", ".grok-plugin/plugin.json"),
        "marketplace": ("astria-marketplace", "plugins/astria/plugin.json"),
    }
    prefix, manifest_path = targets[args.target]
    marketplace_root = ROOT / "dist" / "marketplace"
    if output_directory == marketplace_root or marketplace_root in output_directory.parents:
        parser.error("output directory must be outside the generated marketplace")
    skills_only = args.target in ("openai-skills-only", "openai-studio")
    plugin_name = "astria" if skills_only else prefix
    plugin_root = marketplace_root if args.target == "marketplace" else marketplace_root / "plugins" / plugin_name

    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync-plugin.py")], check=True)

    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate-plugin.py")], check=True)
    manifest = plugin_root / manifest_path
    version = json.loads(manifest.read_text(encoding="utf-8"))["version"]
    output_directory.mkdir(parents=True, exist_ok=True)
    archive = output_directory / f"{prefix}-{version}.zip"

    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(plugin_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(plugin_root).as_posix()
            if skills_only and relative in ("mcp.json", ".mcp.json"):
                continue
            info = zipfile.ZipInfo(relative, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            payload = path.read_bytes()
            if skills_only and path.name == "plugin.json":
                metadata = json.loads(payload)
                metadata.pop("mcpServers", None)
                if args.target == "openai-studio":
                    metadata["name"] = "astria-studio"
                metadata["description"] = "Astria creative skills with agent-assisted local MCP setup. Connect an Astria account through your host to generate images and videos."
                if relative == "plugin.json":
                    settings = metadata["extensions"]["com.openai"]
                    settings.pop("review", None)
                    settings["publication"]["release_notes"] = "Updated creative skills and agent-assisted MCP setup for local Codex hosts. This is a skills-only package; account connection is separate."
                    settings["interface"]["longDescription"] = metadata["description"]
                    if args.target == "openai-studio":
                        settings["interface"]["displayName"] = "Astria Studio"
                elif relative == ".codex-plugin/plugin.json":
                    metadata["interface"]["longDescription"] = metadata["description"]
                    if args.target == "openai-studio":
                        metadata["interface"]["displayName"] = "Astria Studio"
                payload = (json.dumps(metadata, indent=2) + "\n").encode("utf-8")
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
