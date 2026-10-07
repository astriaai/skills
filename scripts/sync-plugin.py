#!/usr/bin/env python3
"""Materialize the OpenAI and Claude plugins from the canonical skill sources."""

import json
import os
import shutil
import stat
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "astria"
CLAUDE_ROOT = ROOT / "plugins" / "astria-claude"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


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


def main():
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
    sync_tree(ROOT / ".claude-plugin", PLUGIN_ROOT / ".claude-plugin")

    CLAUDE_ROOT.mkdir(parents=True, exist_ok=True)
    sync_tree(PLUGIN_ROOT / "skills", CLAUDE_ROOT / "skills")
    copy_file(ROOT / ".claude-plugin" / "plugin.json", CLAUDE_ROOT / ".claude-plugin" / "plugin.json")
    copy_file(ROOT / ".mcp.json", CLAUDE_ROOT / ".mcp.json")
    copy_file(ROOT / "docs" / "CLAUDE.md", CLAUDE_ROOT / "README.md")

    print(f"Synced {len(sources)} skills -> {PLUGIN_ROOT} and {CLAUDE_ROOT}")


if __name__ == "__main__":
    main()
