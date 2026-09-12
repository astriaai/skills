# Publishing the Astria plugin

## Prepare a release

Run the only supported release command:

```bash
scripts/release-plugin.sh X.Y.Z
```

It updates the Claude and OpenAI versions together, materializes the native
plugin under `plugins/astria`, refreshes every local Claude and Codex skill
symlink, validates source parity, and writes an upload-ready archive to `dist/`.

Commit the source and generated plugin together, tag the same version as
`vX.Y.Z`, and push. GitHub Actions rejects stale generated output, attaches the
archive and checksum to the tagged GitHub release, and leaves a build artifact
on every main-branch build.

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
