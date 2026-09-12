# Publishing the Astria plugin

## Publish a release

Start with a clean `main` branch whose HEAD matches `origin/main`, then preview
the release without changing the repository:

```bash
scripts/release-driver.py X.Y.Z --dry-run
```

Publish with:

```bash
scripts/release-driver.py X.Y.Z --publish
```

The driver fetches tags and `origin/main`, refuses dirty, detached, stale, or
already-tagged releases, then runs the existing `release-plugin.sh` preparation.
It commits only the generated plugin and release metadata, creates an annotated
tag, and atomically pushes the branch and tag. It waits for the tagged GitHub
Actions run, verifies the release archive against both its published checksum
and the local build, reinstalls `astria@astria`, and prints the OpenAI Platform
URL for the manual directory step. Use `--skip-local-install` only on a machine
that does not have the Codex marketplace configured.

`release-plugin.sh` remains the lower-level prepare-only command for debugging.
It updates the Claude and OpenAI versions together, materializes the native
plugin under `plugins/astria`, refreshes every local Claude and Codex skill
symlink, validates source parity, and writes an upload-ready archive to `dist/`.

Whenever the vendored CLI changes, `scripts/sync-cli.sh` invokes the same plugin
sync automatically. Adding or renaming a skill requires updating the existing
Claude marketplace list; the sync then updates both the native plugin and every
developer symlink.

## Distribution and upgrades

- Codex developers can install this repository marketplace and reinstall the
  `astria@astria` plugin after local changes. The local skills remain live
  symlinks, so new tasks immediately use the edited source.
- ChatGPT workspace administrators can import `astriaai/skills` as a GitHub
  marketplace. ChatGPT syncs imported repositories daily; **Sync now** applies
  a valid update immediately, while an invalid update leaves the previous
  working version installed.
- Public-directory users receive only versions that Astria submits, passes
  OpenAI review, and publishes in the OpenAI Platform portal. Upload the
  `dist/astria-X.Y.Z.zip` asset as a new version. Review and publishing cannot
  be automated by repository code.

The current package is skills plus a bundled CLI. A public mobile release that
performs authenticated Astria actions must also use a stable HTTPS MCP endpoint
with OAuth; phones cannot reuse a developer's local `~/.astria/config.json`.
