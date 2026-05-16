#!/bin/sh
# Vendor the astria CLI from the astriaai/cli repo into this plugin.
#
# astriaai/cli is the source of truth; the plugin ships a copy so marketplace
# installs need no bootstrap. Run this on each CLI release.
#
#   scripts/sync-cli.sh [REF]      REF = branch or tag (default: main)
set -eu

REF="${1:-main}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/plugins/astria/bin/astria"
URL="https://raw.githubusercontent.com/astriaai/cli/$REF/astria"

curl -fsSL "$URL" -o "$DEST"
python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$DEST" \
  || { echo "sync-cli: downloaded file is not valid Python" >&2; exit 1; }
chmod 0755 "$DEST"

echo "Vendored astria CLI ($REF) -> $DEST"
"$DEST" --version
