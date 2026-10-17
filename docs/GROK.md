# Astria for Grok

Create product photos, virtual try-on images, professional headshots, fashion
lookbooks, image edits, and videos using your Astria account. The package
contains shared Astria skills, Grok Build and Cursor manifests, a logo,
and a hosted MCP connection. Grok Bot uses Cursor-compatible plugin packaging.

## Grok.com public connector catalog

The public Connectors catalog on `grok.com` is the target for Astria's
listing. It is separate from Grok Bot's bot marketplace, Grok Build plugin
marketplaces, and Cursor's plugin directory. Publishing this package to any
of those directories does not create a Grok.com connector tile.

Astria's production MCP endpoint is `https://mcp.astria.ai/mcp`. Grok's
[connector documentation](https://docs.x.ai/grok/connectors) explains how a
user can add it through **New Connector > Custom** and authenticate. That
creates a custom connection, not a public catalog listing.

As of October 11, 2026, the documented catalog has pre-configured OAuth
connectors, but the documentation provides no provider submission workflow.
The [official contact page](https://x.ai/contact) lists `support@x.ai` for
product inquiries. Ask that team for the catalog onboarding and review
process; this is a contact route, not a confirmed submission or approval.
Astria is not yet listed in that catalog. Grok-specific OAuth and tool
execution validation is pending.

Suggested listing metadata:

- Name: Astria
- Description: Create and edit AI images and videos
- Website: https://www.astria.ai
- MCP URL: https://mcp.astria.ai/mcp
- Transport: Streamable HTTP
- Authentication: OAuth with PKCE, dynamic client registration, refresh tokens
- Use cases: product photography, virtual try-on, headshots, fashion lookbooks,
  image editing, and video generation

## Grok Bot package: connect and use

When Astria is available in your Grok Bot marketplace, add it from **Connect
apps** and complete Astria sign-in and consent in the browser. Attach the
connector with `@` in a task. Each user connects their own Astria account;
installed connectors are available to all Bots on that user's account.
This local package is not yet a published marketplace listing.

Try: "Using Astria, identify my account and list the available image and
video models. Do not generate anything." Then request a product photoshoot,
headshots from supplied photos, a virtual try-on, or an image/video generation.
Generation and training use your Astria credits. Rechecking a submitted
prompt does not submit another paid generation.

## Preview in Grok Build

From the skills repository:

```sh
grok plugin validate ./dist/marketplace/plugins/astria-grok
grok plugin install ./dist/marketplace/plugins/astria-grok --trust
grok mcp doctor
```

Use `/mcps` to authenticate Astria and start a new session or refresh plugins.
For a published release, extract `astria-grok-X.Y.Z.zip` and install the
extracted plugin directory with the same commands. The marketplace ZIP also
contains this package and its Grok/Cursor catalogs. This source checkout no
longer contains a ready-to-install Git marketplace; upgrades require downloading
a new release. See the repository README for the verified download helper.

## Preview in Cursor

Copy the entire `dist/marketplace/plugins/astria-grok` folder into
`~/.cursor/plugins/local/astria/`, then restart Cursor or run **Developer:
Reload Window**. Use **Customize** to check the skills and MCP connection,
and **Settings > MCP** to authenticate Astria. Local imports must be enabled
by your organization's policy. Copy the folder rather than linking to a
checkout outside Cursor's local plugin directory.

## Connection and results

The MCP server is `https://mcp.astria.ai/mcp` over streamable HTTP. Both
`mcp.json` and `.mcp.json` declare the same connection. Astria supports OAuth
with PKCE and Dynamic Client Registration; compatible hosts manage browser
login, credential storage, and refresh. No API key, client secret, local
executable, or login hook is needed for remote workflows.

Read the connected account with `get_profile`. Discover live models before
generation. Media inputs must be accessible HTTPS URLs; an attachment or a
path on the Bot's computer is not automatically an Astria-accessible URL.
Use an available upload tool, or the separately installed Astria CLI when
local media handling is required.

Generation returns a prompt before rendering finishes. Retrieve completed
assets with `get_prompt`, preserving the original submission key on retries.
Show the returned image/video URLs when interactive MCP Apps rendering is
unavailable. Gallery widgets, MCP completion events, OAuth refresh, and media
display still require verification in the actual Grok Bot host.

Optional terminal workflows described in the shared skills require a
separately installed Astria CLI and independent CLI login. The package does
not install that CLI or configure scheduled jobs.

## Network, privacy, and support

The plugin connects to `mcp.astria.ai` for tools and OAuth discovery. Astria's
discovery metadata supplies authorization and token URLs on `mcp.astria.ai`
and registration on `www.astria.ai`; follow the advertised URLs. Sign in to Astria in the
host's browser flow. The package contains no credentials. User-supplied media
URLs and selected reference data are sent to Astria only for requested work.
Returned assets may use Astria's media CDN.

See [Astria privacy](https://www.astria.ai/privacy),
[terms](https://www.astria.ai/terms), and
[support](mailto:support@astria.ai). The plugin source is MIT licensed;
Astria's hosted service is governed by its terms.

## Packaging and publication

```sh
scripts/sync-plugin.sh --no-local-links
python3 scripts/validate-plugin.py
python3 scripts/build-plugin.py dist --target grok
```

The archive contains the plugin root with both manifests. Extract it for local
preview; the documented marketplace submission accepts a repository, not a
claim that building a ZIP publishes the plugin.

Cursor/Grok Bot public distribution still requires a public Git repository
containing the built plugin, plus Cursor review. Submit a separately hosted
generated repository if pursuing that route; this source-only repository and
its ZIP assets do not meet the repository requirement. For Grok Build's public
catalog, follow xAI's contribution rules. Local extraction and installation
are supported separately from public catalog approval.

References: [Grok Bot apps](https://docs.x.ai/grok-bot/computer-and-apps),
[Grok Build plugins](https://docs.x.ai/build/features/skills-plugins-marketplaces),
[Grok Build MCP](https://docs.x.ai/build/features/mcp-servers),
[Cursor plugin format](https://cursor.com/docs/reference/plugins),
[Cursor local previews](https://cursor.com/docs/plugins).
