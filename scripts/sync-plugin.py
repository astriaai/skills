#!/usr/bin/env python3
"""Materialize the OpenAI, Claude, and Grok plugins from canonical sources."""

import json
import os
import shutil
import stat
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE_ROOT = ROOT / "dist" / "marketplace"
PLUGIN_ROOT = MARKETPLACE_ROOT / "plugins" / "astria"
CLAUDE_ROOT = MARKETPLACE_ROOT / "plugins" / "astria-claude"
GROK_ROOT = MARKETPLACE_ROOT / "plugins" / "astria-grok"
CLAUDE_MARKETPLACE = ROOT / "packaging" / "marketplaces" / "claude.json"


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def ignored(_directory, names):
    return {name for name in names if name == "__pycache__" or name.endswith(".pyc")}


def sync_tree(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{destination.name}-", dir=destination.parent))
    staged = temporary / destination.name
    try:
        shutil.copytree(source, staged, ignore=ignored)
        if destination.exists():
            shutil.rmtree(destination)
        staged.rename(destination)
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def copy_file(source, destination, executable=False):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.tmp")
    shutil.copy2(source, temporary)
    if executable:
        temporary.chmod(temporary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    os.replace(temporary, destination)


def skill_sources():
    plugin = read_json(CLAUDE_MARKETPLACE)["plugins"][0]
    return [(Path(entry).name, ROOT / Path(entry).name) for entry in plugin["skills"]]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sync_grok():
    manifest = read_json(ROOT / ".claude-plugin" / "plugin.json")
    manifest.update({
        "keywords": ["astria", "astria photoshoots", "astria image generation", "astria video"],
        "logo": "assets/logo.png",
    })
    write_json(GROK_ROOT / ".grok-plugin" / "plugin.json", manifest)
    write_json(GROK_ROOT / ".cursor-plugin" / "plugin.json", {
        **manifest,
        "skills": "./skills/",
        "mcpServers": "./mcp.json",
    })
    sync_tree(PLUGIN_ROOT / "skills", GROK_ROOT / "skills")
    for filename in (".mcp.json", "mcp.json"):
        copy_file(ROOT / ".mcp.json", GROK_ROOT / filename)
    copy_file(PLUGIN_ROOT / "assets" / "logo.png", GROK_ROOT / "assets" / "logo.png")
    copy_file(ROOT / "LICENSE", GROK_ROOT / "LICENSE")
    copy_file(ROOT / "docs" / "GROK.md", GROK_ROOT / "README.md")

    entry = {
        "name": manifest["name"],
        "description": manifest["description"],
        "version": manifest["version"],
        "homepage": manifest["homepage"],
        "category": "creative",
        "keywords": manifest["keywords"],
    }
    marketplace = {"name": "astria", "owner": manifest["author"]}
    write_json(MARKETPLACE_ROOT / ".grok-plugin" / "marketplace.json", {
        **marketplace,
        "description": manifest["description"],
        "plugins": [{**entry, "domains": ["astria.ai"], "source": {"type": "local", "path": "./plugins/astria-grok"}}],
    })
    write_json(MARKETPLACE_ROOT / ".cursor-plugin" / "marketplace.json", {
        **marketplace,
        "metadata": {"description": manifest["description"], "version": manifest["version"]},
        "plugins": [{**entry, "source": "./plugins/astria-grok"}],
    })


def main():
    # This entire directory is build output. Remove files from older layouts
    # so stale payloads cannot leak into a release marketplace.
    if MARKETPLACE_ROOT.exists():
        shutil.rmtree(MARKETPLACE_ROOT)
    sync_tree(ROOT / "packaging" / "openai", PLUGIN_ROOT)
    copy_file(CLAUDE_MARKETPLACE, MARKETPLACE_ROOT / ".claude-plugin" / "marketplace.json")
    copy_file(ROOT / "packaging" / "marketplaces" / "codex.json", MARKETPLACE_ROOT / ".agents" / "plugins" / "marketplace.json")
    sources = skill_sources()
    names = [name for name, _source in sources]
    if len(names) != len(set(names)):
        raise SystemExit("sync-plugin: duplicate skill names in Claude marketplace")

    staging = Path(tempfile.mkdtemp(prefix=".skills-", dir=PLUGIN_ROOT))
    try:
        for name, source in sources:
            if not (source / "SKILL.md").is_file():
                raise SystemExit(f"sync-plugin: missing {source / 'SKILL.md'}")
            shutil.copytree(source, staging / name, ignore=ignored)

        destination = PLUGIN_ROOT / "skills"
        if destination.exists():
            shutil.rmtree(destination)
        staging.rename(destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)

    copy_file(ROOT / "bin" / "astria", PLUGIN_ROOT / "bin" / "astria", executable=True)
    copy_file(ROOT / "mcp.json", PLUGIN_ROOT / "mcp.json")
    portable_mcp = read_json(ROOT / "mcp.json")
    compatibility_mcp = {"mcpServers": {
        name: {**server, "type": "http"}
        for name, server in portable_mcp["mcpServers"].items()
    }}
    (ROOT / ".mcp.json").write_text(json.dumps(compatibility_mcp, indent=2) + "\n", encoding="utf-8")
    copy_file(ROOT / ".mcp.json", PLUGIN_ROOT / ".mcp.json")
    # OAuth login is handled by the host; no CLI login hook is packaged.
    if (PLUGIN_ROOT / "hooks").exists():
        shutil.rmtree(PLUGIN_ROOT / "hooks")
    copy_file(ROOT / ".claude-plugin" / "plugin.json", PLUGIN_ROOT / ".claude-plugin" / "plugin.json")

    CLAUDE_ROOT.mkdir(parents=True, exist_ok=True)
    sync_tree(PLUGIN_ROOT / "skills", CLAUDE_ROOT / "skills")
    copy_file(ROOT / ".claude-plugin" / "plugin.json", CLAUDE_ROOT / ".claude-plugin" / "plugin.json")
    copy_file(ROOT / ".mcp.json", CLAUDE_ROOT / ".mcp.json")
    copy_file(ROOT / "docs" / "CLAUDE.md", CLAUDE_ROOT / "README.md")
    sync_grok()
    copy_file(ROOT / "README.md", MARKETPLACE_ROOT / "README.md")
    copy_file(ROOT / "LICENSE", MARKETPLACE_ROOT / "LICENSE")

    print(f"Synced {len(sources)} skills -> {PLUGIN_ROOT}, {CLAUDE_ROOT}, and {GROK_ROOT}")


if __name__ == "__main__":
    main()
