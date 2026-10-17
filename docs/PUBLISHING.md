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
It commits only canonical release metadata, creates an annotated
tag, and atomically pushes the branch and tag. It waits for the tagged GitHub
Actions run, verifies all four release archives against their published checksums
and local builds, downloads the marketplace and reinstalls `astria@astria`, and prints the OpenAI Platform
URL for the manual directory step. Use `--skip-local-install` only on a machine
that does not have the Codex marketplace configured.

`release-plugin.sh` remains the lower-level prepare-only command for debugging.
It updates the Claude and OpenAI versions together, materializes the native
packages under ignored `dist/marketplace/plugins/`, refreshes every local Claude and Codex skill
symlink, validates source parity, and writes upload archives and an installable marketplace ZIP to `dist/`.

Whenever the vendored CLI changes, `scripts/sync-cli.sh` invokes the same plugin
sync automatically. Adding or renaming a skill requires updating the existing
`packaging/marketplaces/claude.json` skill list; the sync then updates both the native plugin and every
developer symlink.

All packages use the host's MCP OAuth connection. The former CLI-auth
SessionStart hook is removed; neither package requires CLI login at startup.
`mcp.json` is the endpoint source of truth; synchronization generates the root
Claude `.mcp.json` and generated package MCP configurations.

## Distribution and upgrades

OpenAI pins a registered MCP app's URL and an existing plugin's MCP server set.
The API-host draft cannot be retargeted and the legacy skills-only plugin cannot
add MCP. The portable ChatGPT package therefore uses `astria-mcp` for a new
registration at `https://mcp.astria.ai/mcp`, keeping the public display name Astria.
The archive builder assigns this identifier only to the ChatGPT upload ZIP.
Codex and Claude Code source manifests keep their `astria` marketplace identifiers. All packages
use the dedicated hostname; do not restore the old API URL to satisfy a draft.

- Release users download `astria-marketplace-X.Y.Z.zip` and its checksum,
  extract it to a persistent directory, then register that local marketplace.
  `python3 scripts/install-plugin-release.py --version X.Y.Z` verifies and extracts
  the download and prints the commands. Upgrades require a new download and
  updating the registered local marketplace path; Git upgrade no longer applies.
- Developers generate `dist/marketplace/` and register that local directory.
  The canonical personal skill symlinks still reflect source edits immediately.
- Existing Git marketplace users must switch their registered Astria source to
  the extracted release directory through the host's marketplace settings.
  The source repository no longer provides a working Git marketplace.
- ChatGPT workspace GitHub imports require a separately hosted generated
  repository. This source-only repository cannot be used for those imports.
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

Claude Code marketplace distribution is separate from public directory approval.
Anthropic's [Software Directory Policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy),
section 4.B, excludes standalone AI image/video/audio generation unless Anthropic
expressly permits it in writing. The connector form requires a declaration that
it does not generate AI media. Astria cannot truthfully make that declaration;
obtain written permission before submitting either public directory listing.
Do not change descriptions or attestations to conceal the generation capability.

The generated Claude marketplace entry uses `plugins/astria-claude` relative
to the extracted marketplace root; canonical skills remain at the source
repository root. Sync generates all packages under `dist/marketplace/`. Build a separate
Claude upload archive with `scripts/build-plugin.py dist --target claude`, and
validate the folder with `claude plugin validate dist/marketplace/plugins/astria-claude`.

Claude chat and Cowork reject a top-level `bin/` directory. The Claude package
therefore contains the shared skills, manifest, fixed remote `.mcp.json`, and a
README. The OpenAI package retains its optional CLI. CI packages all four archives
and their checksums; no repository push or directory submission happens during
a local build.

At <https://claude.ai/directory/manage>, submit the MCP server first as a
connector using the universal URL `https://mcp.astria.ai/mcp` and OAuth DCR.
If the directory requires a Git repository, submit a separately hosted
generated repository containing the Claude package, from the same organization
and pair the listings. Do not submit this source-only repository as a built
plugin. For local Claude installation, upload the release ZIP instead. Directory terms and
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

## Grok.com public connector catalog

The Grok.com Connectors catalog is separate from the bot and CLI plugin
marketplaces below. A package release or custom MCP connection does not
publish a public connector tile. Grok's [connector documentation](https://docs.x.ai/grok/connectors)
describes user setup but currently gives no provider submission process.
Contact `support@x.ai`, as listed on the [official contact page](https://x.ai/contact),
to request catalog onboarding and review requirements. Public listing and
Grok-specific validation remain pending. See [Grok setup](GROK.md).

## Grok Bot and Grok Build

Synchronization generates `dist/marketplace/plugins/astria-grok`, its Grok
Build and Cursor manifests, and catalogs under `dist/marketplace/`. All metadata versions follow the existing
canonical manifest; the shared skills are copied from the same sources.
Both Grok MCP files use the fixed OAuth endpoint, without credentials or hooks.

Build `astria-grok-X.Y.Z.zip` with
`python3 scripts/build-plugin.py dist --target grok`. CI and the release
preparation script include this archive and its checksum. Extract the archive
for a local preview; marketplace submission uses the public repository.

The marketplace ZIP includes catalogs pointing at its bundled package folders.
Extract it to a persistent path before registering it with a host. See the
README for local installation and migration from the former Git marketplace.

Cursor/Grok Bot public distribution still requires a public repository with a
built plugin, plus review. This source-only repository and its release ZIPs do
not satisfy that catalog's repository submission requirement. A separately
hosted generated repository would be needed for that route. Grok.com connector
catalog onboarding is a separate process and is unaffected by this change.

## Source and artifact layout

- Top-level skill directories and `bin/astria`: canonical content.
- `packaging/openai/`: portable/native OpenAI manifests and assets.
- `.claude-plugin/plugin.json`: canonical Claude/Grok metadata.
- `packaging/marketplaces/`: canonical Claude and Codex catalog templates;
  the Claude template also owns the skill list.
- `dist/marketplace/`: generated catalogs and three complete packages (ignored).
- `dist/*.zip` and `dist/*.sha256`: deterministic release assets (ignored).

The source checkout contains no generated `plugins/` tree. The builder generates
packages automatically, so a fresh checkout can build any target without a
manual synchronization step. CI validates generated content instead of requiring
it to be committed. The release driver commits only the four versioned source
metadata files. No release is published by a local build.
