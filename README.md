# Astria AI plugin

[Astria](https://www.astria.ai) skills and OAuth-connected MCP tools for image
and video generation, references, prompt writing and photoshoot templates.
The plugin connects to `https://mcp.astria.ai/mcp`. Your agent host handles
Astria login and keeps the connection authenticated.

## Install in Codex

```bash
codex plugin marketplace add astriaai/skills --ref main
codex plugin add astria@astria
```

Connect Astria through the host's plugin/MCP connection settings and complete
its OAuth login. Start a new task after installation or upgrade so refreshed
skills and tools load. For a newer repository snapshot:

```bash
codex plugin marketplace upgrade astria
codex plugin add astria@astria
```

ChatGPT workspace administrators can import `astriaai/skills` as a GitHub
marketplace. Imported marketplaces can be refreshed with **Sync now**. Public
directory availability requires a reviewed, published OpenAI plugin version
and its registered Astria connection.

## Install in Claude (web, desktop and mobile)

Build the Claude archive with:

```bash
python3 scripts/build-plugin.py /tmp/astria-plugin-preview --target claude
```

Upload `astria-claude-X.Y.Z.zip` through **Customize > Plugins > Add > Upload
plugin**, then connect Astria from its **Connectors** tab. Complete Astria
OAuth sign-in and consent; choose **Sign in now > Register automatically**
when prompted. DCR registers Claude's public client without a client secret.
The remote connection works in the iOS and Android apps as well. Interactive
previews use the same MCP Apps resources as ChatGPT, when supported by the host.
Ask Claude to open the Astria gallery to browse generations.

The Claude marketplace points at `plugins/astria-claude`, a package without a
top-level `bin/` directory (which Claude chat and Cowork reject). Its twelve
skills and MCP endpoint are generated from the same sources as OpenAI/Codex.
See [Claude setup and limitations](docs/CLAUDE.md). A local archive does not
publish a directory listing.

## Install in Claude Code

```text
/plugin marketplace add astriaai/skills
/plugin install astria@astria
```

Use `/mcp` to connect/authenticate Astria, or preview the local package with
`claude --plugin-dir ./plugins/astria-claude`. The `.mcp.json` uses a fixed
HTTPS URL; no API key, client secret, shell process, or CLI login hook is
required. CLI-only workflows require a separately installed Astria CLI.

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

The plugin still bundles the [Astria CLI](https://github.com/astriaai/cli) for
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

| Skill | Purpose |
|-------|---------|
| **astria-api** | Goal-based routing, MCP results, references, generation, templates and pricing; optional CLI reference |
| **product-photoshoot** | Ecommerce product shots and coordinated lookbooks with stable SKU references |
| **virtual-try-on** | Garments and accessories on the chosen person, consistently across scenes |
| **headshots-from-photos** | Professional portraits of the real person in supplied photos |
| **prompt-writing** | Prompt syntax, parameters and writing effective prompts |
| **packs-guide** | Templates, categories and photoshoot workflows |
| **unique-headshot** | Diverse, realistic headshots with explicit model/face-inpainting settings |
| **navigation** | Astria app sitemap |
| **store-photoshoot** | Store catalog to reusable photoshoot workflow; some steps need CLI/UI |
| **landing-page-editor** | Edit a workspace's landing HTML through optional CLI access |
| **storyboard** | Text-only cinematic video sequence from a draft or ordered images |
| **artboard** | Legacy alias for Storyboard |

## Development and rollout

```bash
scripts/sync-plugin.sh --no-local-links
python3 scripts/validate-plugin.py
python3 scripts/build-plugin.py /tmp/astria-plugin-preview
```

The skills are canonical at the repository root. Synchronization materializes
both packages and both compatibility MCP configurations; validation checks
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
