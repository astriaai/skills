#!/bin/sh
# Symlink every skill in this repo into global personal skill dirs so they load
# in every project, and LIVE: an edit to a SKILL.md shows up in new sessions
# with no reinstall.
#
# Claude Code and Codex discover personal skills only one level deep
# (~/.claude/skills/<name>/SKILL.md, ~/.codex/skills/<name>/SKILL.md) and do not
# scan recursively, so each skill needs its own symlink. Re-run this after
# adding or renaming a skill.
#
# This is a maintainer convenience for developing the plugin locally — end
# users install it normally with `/plugin install astria@astria`.
#
#   scripts/link-skills.sh
set -eu

SKILLS_SRC="$(cd "$(dirname "$0")/.." && pwd)"

link_skills() {
  dest="$1"

  mkdir -p "$dest"

  # Link every skill directory (any top-level dir holding a SKILL.md).
  for dir in "$SKILLS_SRC"/*/; do
    [ -f "$dir/SKILL.md" ] || continue
    name="$(basename "$dir")"
    link="$dest/$name"
    if [ -e "$link" ] && [ ! -L "$link" ]; then
      echo "skip   $name (a real directory exists at $link)" >&2
      continue
    fi
    ln -sfn "$SKILLS_SRC/$name" "$link"
    echo "link   $name -> $dest"
  done

  # Prune symlinks that point into this repo's skills dir but no longer resolve
  # (a skill was removed or renamed).
  for link in "$dest"/*; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
      "$SKILLS_SRC"/*)
        [ -e "$link" ] || { rm "$link"; echo "prune  $(basename "$link") (dangling)"; } ;;
    esac
  done

  echo "done -> $dest"
}

link_skills "$HOME/.claude/skills"
link_skills "$HOME/.codex/skills"
