#!/bin/sh
# Refresh the self-contained OpenAI plugin and every developer skill symlink.
# CI passes --no-local-links because it has no persistent developer home.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$ROOT/scripts/sync-plugin.py"

if [ "${1:-}" = "--no-local-links" ]; then
  [ "$#" -eq 1 ] || { echo "Usage: scripts/sync-plugin.sh [--no-local-links]" >&2; exit 2; }
else
  [ "$#" -eq 0 ] || { echo "Usage: scripts/sync-plugin.sh [--no-local-links]" >&2; exit 2; }
  "$ROOT/scripts/link-skills.sh"
fi
