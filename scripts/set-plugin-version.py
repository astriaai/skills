#!/usr/bin/env python3
"""Set one release version across Claude and OpenAI plugin metadata."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def update(path, mutator):
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    mutator(data)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    if len(sys.argv) != 2 or not SEMVER.fullmatch(sys.argv[1]):
        raise SystemExit("Usage: scripts/set-plugin-version.py <semver>")
    version = sys.argv[1]

    for path in (
        ROOT / ".claude-plugin" / "plugin.json",
        ROOT / "plugins" / "astria" / "plugin.json",
        ROOT / "plugins" / "astria" / ".codex-plugin" / "plugin.json",
    ):
        update(path, lambda data: data.__setitem__("version", version))

    def update_marketplace(data):
        data["metadata"]["version"] = version
        data["plugins"][0]["version"] = version

    update(ROOT / ".claude-plugin" / "marketplace.json", update_marketplace)
    print(f"Set Astria plugin version -> {version}")


if __name__ == "__main__":
    main()
