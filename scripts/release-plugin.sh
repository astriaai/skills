#!/bin/sh
# One release path: versions metadata, refreshes dev links, validates, and builds.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:?Usage: scripts/release-plugin.sh <semver>}"
[ "$#" -eq 1 ] || { echo "Usage: scripts/release-plugin.sh <semver>" >&2; exit 2; }

python3 "$ROOT/scripts/set-plugin-version.py" "$VERSION"
"$ROOT/scripts/sync-plugin.sh"
python3 "$ROOT/scripts/validate-plugin.py" --expected-version "$VERSION"
python3 "$ROOT/scripts/build-plugin.py" "$ROOT/dist"

echo "Release files are ready. Commit, tag v$VERSION, and push; GitHub Actions publishes the archive."
echo "OpenAI public-directory updates still require review and Publish in the OpenAI Platform portal."
