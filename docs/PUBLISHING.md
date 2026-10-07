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

Both packages use the host's MCP OAuth connection. The former CLI-auth
SessionStart hook is removed; neither package requires CLI login at startup.
`mcp.json` is the endpoint source of truth; synchronization generates the root
Claude `.mcp.json` and both native package MCP configurations.

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

## MCP rollout prerequisites

The package now uses skills plus OAuth-connected HTTPS MCP by default, with a
bundled CLI for capabilities not exposed remotely. Before publishing:

1. Deploy the Rails MCP/OAuth implementation, including `/oauth/register`
   and its discovery metadata, using `bin/deploy` in SDBooth.
2. Register the ChatGPT connection through DCR or the existing public OAuth
   client `astria-chatgpt` and its exact callback. Scan its tools/events and
   test consent, refresh and revocation. After registration, add the returned
   OpenAI app identity to the plugin mapping; never fabricate that identity.
3. For direct Codex/Claude connections, use the package's remote MCP endpoint
   and complete host OAuth login. DCR registers a separate public client with
   the callback supplied by the host; no manual client ID is needed. Native
   HTTP loopback IP callbacks are supported with S256 PKCE and user consent.
4. Verify a generation and completion notification in the target host. Events
   use the host's callback; local clients without event support poll prompts.
5. Publish the reviewed plugin version through the appropriate marketplace.

The local package validator and archive build establish wiring/source parity,
not deployed endpoint availability or successful production host login.
MCP workflows need no local Python/curl installation or CLI API key; optional
terminal workflows retain separate CLI authentication.

## Claude directory

The Claude marketplace entry uses `plugins/astria-claude`; canonical skills
remain at the repository root. Sync generates both packages. Build a separate
Claude upload archive with `scripts/build-plugin.py dist --target claude`, and
validate the folder with `claude plugin validate plugins/astria-claude`.

Claude chat and Cowork reject a top-level `bin/` directory. The Claude package
therefore contains the nine skills, manifest, fixed remote `.mcp.json`, and a
README. The OpenAI package retains its optional CLI. CI packages both archives
and their checksums; no repository push or directory submission happens during
a local build.

At <https://claude.ai/directory/manage>, submit the MCP server first as a
connector using the universal URL `https://mcp.astria.ai/mcp` and OAuth DCR.
Submit the plugin bundle from `astriaai/skills`, folder `plugins/astria-claude`,
from the same organization and pair the listings. The repository must contain
the generated Claude package on the submitted branch. Directory terms and
review remain separate from creating a local package.

Before claiming parity, test Astria consent, `get_profile`, generation results,
gallery, media saving, token refresh and revocation in actual Claude hosts.
Use a HTTPS media URL for input; a phone attachment is not automatically an
Astria-accessible URL. The global gallery navigation metadata is ChatGPT-only;
Claude opens the same gallery through `open_astria`. Record mobile and UI
results separately from package/protocol validation.

References: [plugin layout](https://claude.com/docs/plugins/build),
[platform support](https://claude.com/docs/plugins/platform-support),
[OAuth requirements](https://claude.com/docs/connectors/building/authentication),
[directory publication](https://claude.com/docs/directory/publish).
