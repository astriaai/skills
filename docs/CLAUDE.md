# Astria for Claude

Generate images and videos, edit images, reuse references, and run photoshoot
templates with Astria directly in Claude. The plugin includes nine shared
Astria skills and connects to `https://mcp.astria.ai/mcp`. No local executable,
Python installation, API key, or client secret is needed for remote workflows.

## Connect

Install the plugin, open its **Connectors** tab, and connect Astria. When
prompted, choose **Sign in now**, then **Register automatically** (DCR); leave
client IDs, secrets, and custom headers empty. Claude
registers its OAuth client automatically through Dynamic Client Registration
(DCR), opens Astria sign-in and consent, and stores and refreshes credentials.
Each person connects their own Astria account. Ask Claude to identify the
connected account before using a shared workspace.

In Claude Code, install `astria@astria` from the `astriaai/skills` marketplace
and use `/mcp` to authenticate. For a local preview:

```sh
claude --plugin-dir ./plugins/astria-claude
```

On claude.ai, use **Customize > Plugins > Add > Upload plugin** to upload
`astria-claude-X.Y.Z.zip`, then connect Astria. The hosted connection works
across web, Claude Desktop, and the iOS and Android apps. Availability of
interactive displays and host controls depends on the Claude surface.

## Use Astria

- Ask Claude to generate an image or video, or edit an image at an accessible
  HTTPS URL. Generation uses your Astria credits.
- Ask to browse your Astria generations. The gallery is read-only and supports
  personal or shared workspaces, previews, refresh, and media links.
- Reuse existing references for a consistent person or product. Create a
  reference from accessible HTTPS images when needed.
- Run a photoshoot template on your references.

On hosts supporting MCP Apps, results display in the conversation with live
image and video previews. The widget refreshes pending results without
submitting another generation. Downloads use supported host controls or open
the original media. ChatGPT-specific global navigation is not a Claude feature;
ask Claude to open the Astria gallery. Hosts without interactive UI can still
retrieve status and returned media URLs.

Local uploads, video inspection/Variate, template authoring, and landing-page
editing need the separately installed Astria CLI and its independent login.
Some included skills describe these optional workflows; Claude mobile cannot
run terminal steps. An attachment is usable for generation only after an upload
tool provides a real HTTPS URL accessible to Astria.

## Privacy and support

OAuth credentials remain with the host. Embedded views receive only account-
authorized result metadata; they receive no access token or website cookies.
See [Astria privacy](https://www.astria.ai/privacy),
[Astria terms](https://www.astria.ai/terms), and
[support](mailto:support@astria.ai).

## Developer references

- [Plugin structure and testing](https://claude.com/docs/plugins/build)
- [Support across platforms](https://claude.com/docs/plugins/platform-support)
- [OAuth, DCR, callbacks, and refresh](https://claude.com/docs/connectors/building/authentication)
- [MCP Apps](https://claude.com/docs/connectors/building/mcp-apps/getting-started)
- [Directory publication](https://claude.com/docs/directory/publish)

The archive is a local preview. Public directory publication requires the
repository changes to be available on GitHub and Anthropic review. Submit the
remote MCP connector and plugin bundle from the same organization and use the
same endpoint for both. Package validation alone does not establish a
successful Claude OAuth connection or a mobile rendering test.
