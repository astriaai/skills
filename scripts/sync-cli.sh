#!/bin/sh
# Vendor the astria CLI from the astriaai/cli repo into this plugin.
#
# astriaai/cli is the source of truth; the plugin ships a copy so marketplace
# installs need no bootstrap.
#
#   scripts/sync-cli.sh [REF]        REF = branch/tag, fetched from GitHub (default: main)
#   scripts/sync-cli.sh --from FILE  vendor a local CLI file
#
# The astriaai/cli pre-push hook calls the --from form to keep the embedded
# copy in lockstep with every CLI push.
set -eu

DEST="$(cd "$(dirname "$0")/.." && pwd)/bin/astria"

if [ "${1:-}" = "--from" ]; then
  SRC="${2:?sync-cli: --from needs a file path}"
  [ -f "$SRC" ] || { echo "sync-cli: $SRC not found" >&2; exit 1; }
  cp "$SRC" "$DEST"
  ORIGIN="$SRC"
else
  REF="${1:-main}"
  ORIGIN="astriaai/cli@$REF"
  curl -fsSL "https://raw.githubusercontent.com/astriaai/cli/$REF/astria" -o "$DEST"
fi

python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' "$DEST" \
  || { echo "sync-cli: vendored file is not valid Python" >&2; exit 1; }
chmod 0755 "$DEST"

echo "Vendored astria CLI ($ORIGIN) -> $DEST"
"$DEST" --version
