# Astria AI plugin

[Astria](https://www.astria.ai) skills and OAuth-connected MCP tools for image
and video generation, references, prompt writing and photoshoot templates.
The plugin connects to `https://mcp.astria.ai/mcp`. Your agent host handles
Astria login and keeps the connection authenticated.

## Download a release

Download the ZIP and matching `.sha256` from [GitHub Releases](https://github.com/astriaai/skills/releases/latest).
Releases contain:

- `astria-marketplace-X.Y.Z.zip`: extract into a persistent directory to install
  in Codex, Claude Code, Grok Build, or Cursor.
- `astria-X.Y.Z.zip`: OpenAI directory upload package.
- `astria-claude-X.Y.Z.zip`: Claude web/desktop upload package.
- `astria-grok-X.Y.Z.zip`: standalone Grok Build/Cursor package.

From a source checkout, the download helper selects the latest release, checks
its SHA-256, and extracts it without changing your host configuration:

```bash
python3 scripts/install-plugin-release.py
# Or select an exact published version:
python3 scripts/install-plugin-release.py --version X.Y.Z
```

The default destination is `~/.local/share/astria/plugins/X.Y.Z`. The helper
prints installation commands with the full path. To upgrade, download a new
version and register its extracted marketplace. Local marketplaces are snapshots;
Git marketplace upgrade commands do not download new release ZIPs. If a host
already has an `astria` marketplace registered from the Git repository, migrate
that source to the extracted release path using the host's marketplace settings
before reinstalling. Keep the extracted folder for as long as it is registered.
The first release containing these new assets must be published before using
the helper; older releases do not contain the marketplace ZIP.

## Install in Codex

After extracting the marketplace ZIP to `/absolute/path/astria-marketplace`:

```bash
codex plugin marketplace add /absolute/path/astria-marketplace
codex plugin add astria@astria
```

Complete Astria OAuth through the plugin/MCP connection settings. Start a new
chat after installing or upgrading. The source repository no longer ships a
ready-to-install Git marketplace. ChatGPT administrator GitHub marketplace
imports need a repository containing built packages; use the reviewed public
plugin or a separately hosted generated repository for that distribution route.
See [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).

## Install in Claude (web, desktop and mobile)

Upload the release's `astria-claude-X.Y.Z.zip` through **Customize > Plugins >
Add > Upload plugin**, then connect Astria from its **Connectors** tab. Complete
Astria OAuth sign-in and consent; choose **Sign in now > Register automatically**
when prompted. See [Claude setup and limitations](docs/CLAUDE.md).
An upload does not publish a directory listing.

## Install in Claude Code

After extracting the marketplace ZIP:

```text
/plugin marketplace add /absolute/path/astria-marketplace
/plugin install astria@astria
```

Use `/mcp` to connect Astria. For a source preview, run
`scripts/sync-plugin.sh --no-local-links`, then
`claude --plugin-dir ./dist/marketplace/plugins/astria-claude`.
See [Claude local marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).

## Grok.com connector catalog

Astria's hosted MCP server is `https://mcp.astria.ai/mcp`. Users can connect
it through Grok's **New Connector > Custom** flow. A custom connection does
not create a public catalog listing. Astria's public listing and Grok-specific
validation are pending; see [Grok setup and publication](docs/GROK.md).

## Grok Bot, Grok Build, and Cursor

Extract the standalone Grok ZIP, or use `plugins/astria-grok` inside the
extracted marketplace. Install that directory in Grok Build:

```bash
grok plugin validate /absolute/path/astria-grok
grok plugin install /absolute/path/astria-grok --trust
```

For Cursor, copy that directory into `~/.cursor/plugins/local/astria/`, reload,
and authenticate Astria in MCP settings. Grok Bot marketplace distribution
still requires Cursor review and a public repository containing the built
plugin. Release ZIPs support local installation; this source-only repository
is no longer a valid public Cursor submission. See
[Cursor plugin distribution](https://cursor.com/docs/reference/plugins) and
[Grok setup](docs/GROK.md). Live Grok Bot validation remains pending.

## Install skills in other agents

```bash
npx skills add astriaai/skills
```

This installs skill instructions; it does not configure an MCP connection.
Add `https://mcp.astria.ai/mcp` in the agent's MCP settings and complete its
OAuth login. Hosts supporting DCR register their client automatically. The skills use discovered
tool names and schemas rather than assuming one agent's namespace.

## MCP workflows

- Discover current models, workspaces, references and photoshoot templates.
- Create references from HTTPS image URLs; generate images, edits and videos.
- Run existing templates on references or a new training set.
- Inspect prompt results and image review comments. Hosts supporting MCP
  events can receive completion notifications; other hosts check prompt status.

Generation submits promptly and renders asynchronously. Instructions preserve
submission keys across retries to avoid duplicate paid actions. No Python,
curl or local API-key file is required for these MCP workflows.

## Optional CLI workflows

The OpenAI/Codex package bundles the [Astria CLI](https://github.com/astriaai/cli) for
local file uploads/downloads, batch orchestration, video inspection/Variate,
workspace/template creation, landing-page HTML and agent handoff. These
capabilities need a terminal, Python 3.9+, curl and independent CLI login:

```bash
astria login
astria whoami
astria variate ./source.mp4 --reference ./dress.jpg \
  --brief "Keep the performance and replace the wardrobe" --wait
```

CLI login uses an API key from
[Astria account settings](https://www.astria.ai/users/edit/api); it is separate
from the host's OAuth connection. The plugin no longer checks CLI login at
session startup. For details see
[`astria-api/references/cli.md`](astria-api/references/cli.md). The CLI-only
Astria web-agent sandbox remains supported.

## Skills

`music-video`, `motion-design`, `storyboard`, and the legacy `artboard` alias
are served by Astria MCP. Discover them with
`list_skills` and read their current instructions with `get_skill`; they are
not bundled in the plugin. Named requests such as `/music-video` can be sent
as chat text, though these remote skills are not local slash-menu entries.
An authenticated Astria MCP connection is required to read them. Existing
plugin installations keep their bundled copies until upgraded.

| Skill | Purpose |
|-------|---------|
| **astria-api** | Goal-based routing, MCP results, references, generation, templates and pricing; optional CLI reference |
| **product-photoshoot** | Ecommerce product shots and coordinated lookbooks with stable SKU references |
| **virtual-try-on** | Garments and accessories on the chosen person, consistently across scenes |
| **headshots-from-photos** | Professional portraits of the real person in supplied photos |
| **prompt-writing** | Prompt syntax, parameters and writing effective prompts |
| **packs-guide** | Templates, categories and photoshoot workflows |
| **avatar** | New, original model faces as diverse, realistic headshots with explicit model/face-inpainting settings |
| **navigation** | Astria app sitemap |
| **store-photoshoot** | Store catalog to reusable photoshoot workflow; some steps need CLI/UI |
| **landing-page-editor** | Edit a workspace's landing HTML through optional CLI access |
| **mux** | Combine video and music, verify synchronization and save the final film |
| **fashion-music-track** | Music tracks for fashion brands, runway shows and campaign films |
| **behind-the-scenes** | Candid handheld films from behind the scenes of a fashion shoot |
| **unique-headshot** | Legacy alias for Avatar |

## Development and rollout

```bash
scripts/sync-plugin.sh --no-local-links
python3 scripts/validate-plugin.py
python3 scripts/build-plugin.py /tmp/astria-plugin-preview
```

The skills are canonical at the repository root. `packaging/` holds the source
manifests, marketplace templates, and assets. Generated directories are never
committed; CI builds and publishes ZIPs with checksums on version tags. Synchronization materializes
all three packages, marketplace catalogs and compatibility MCP configurations
under ignored `dist/marketplace/`; validation checks
source parity and tool examples against schemas generated from the shared CLI.
`scripts/sync-cli.sh` also synchronizes the sibling Rails MCP contract when
that checkout is present.

Before releasing this MCP version, deploy the Rails endpoint with OAuth
dynamic client registration (DCR). Discovery advertises `/oauth/register`,
so compatible hosts register their public client automatically and then open
Astria login/consent. HTTPS callbacks and native HTTP loopback IP callbacks
are supported. The existing `astria-chatgpt` seed remains available for a
predefined hosted ChatGPT connection. Production host login and callback
delivery remain rollout checks.

See [`docs/PUBLISHING.md`](docs/PUBLISHING.md) for release preparation,
connection registration and directory publication. Local package builds do
not publish a version or deploy the server.

## License

MIT
