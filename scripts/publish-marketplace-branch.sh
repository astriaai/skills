#!/usr/bin/env bash
# Publish a released astria-marketplace-X.Y.Z.zip as the `marketplace` branch.
#
# ChatGPT workspace admins (Admin > Plugins > Add > Import marketplace) and
# `codex plugin marketplace add astriaai/skills --ref marketplace` read built
# packages from Git, while main only holds sources. Each release appends one
# commit whose tree is exactly the extracted ZIP, so Git upgrades fast-forward.
#
# Usage: scripts/publish-marketplace-branch.sh dist/astria-marketplace-X.Y.Z.zip
set -euo pipefail

zip=$1
branch=marketplace
version=$(basename "$zip" .zip)
version=${version#astria-marketplace-}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

unzip -q "$zip" -d "$tmp/tree"
test -f "$tmp/tree/.agents/plugins/marketplace.json"

git fetch --quiet origin "+refs/heads/$branch:refs/remotes/origin/$branch" 2>/dev/null || true
parent=$(git rev-parse --quiet --verify "refs/remotes/origin/$branch" || true)

export GIT_INDEX_FILE="$tmp/index"
git --work-tree="$tmp/tree" add --all --force .
tree=$(git write-tree)
unset GIT_INDEX_FILE

if [ -n "$parent" ] && [ "$(git rev-parse "$parent^{tree}")" = "$tree" ]; then
  echo "$branch already matches $version"
  exit 0
fi

commit=$(git -c user.name="${GIT_AUTHOR_NAME:-github-actions[bot]}" \
  -c user.email="${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}" \
  commit-tree "$tree" ${parent:+-p "$parent"} -m "Astria plugin marketplace $version")
git push origin "$commit:refs/heads/$branch"
echo "Published $version to $branch ($commit)"
