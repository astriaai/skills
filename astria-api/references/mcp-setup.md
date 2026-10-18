# Connect Astria MCP

Use this when Astria tools are missing or need authentication for the user's
requested Astria task. Reuse working tools regardless of their host namespace.
This setup connects the account; it does not submit a generation.

## Local Codex host

This applies to Codex CLI, IDE, and desktop tasks running on the user's local
Codex host. A terminal in a hosted ChatGPT container is not that host: changing
its configuration will not register tools in ChatGPT web or mobile.

1. Inspect the available Astria tools first. If already connected, use
   `get_profile` and continue the requested task without adding a server.
2. If setup is needed, run `codex mcp list` on the local host. Reuse a server
   configured for `https://mcp.astria.ai/mcp`, including one supplied by an
   installed plugin. Do not overwrite a server with a different URL or add a
   duplicate to work around authentication. An existing disabled connection
   should be enabled through the host's connection controls.
3. When no Astria connection exists and the name `astria` is unused, run:

   ```bash
   codex mcp add astria --url https://mcp.astria.ai/mcp
   ```

   If `astria` belongs to a different server, use an unused descriptive name
   such as `astria-official` and use that name for subsequent commands.
4. The add command may start OAuth itself. Follow its result; do not launch a
   second login while one is pending. If login is still required, run
   `codex mcp login <configured-name>`. For a plugin-provided connection, use
   the host's Authenticate action instead of adding a second configuration.
5. Let the user complete Astria sign-in and consent in the browser. Never ask
   them to paste an API key, password, token, or authorization code into chat.
   On denial or timeout, report that result and stop setup rather than retrying
   authentication repeatedly or changing security settings.
6. Confirm the command's result. If tools have not loaded in this conversation,
   use the host's supported reload action or ask the user to start a new chat.
   Once tools are available, call `get_profile` to verify the connected account
   before continuing. Saving configuration alone is not a verified connection.

Run these commands for the user when the local host permits it; do not merely
paste instructions and stop. Follow the host's actual permission requirements.
If `codex` is unavailable, use an available native MCP setup action or explain
the missing capability; do not install another host or invent an installation
API. Preserve existing server configuration and account choices.

## Hosted ChatGPT web or mobile

Do not run `codex mcp add` in a cloud sandbox and claim it connects ChatGPT.
If a suitable Astria plugin is available through the host's plugin discovery
tools, use its supported install/connect flow and wait for connection to be
confirmed. Otherwise explain that agent-driven custom MCP registration is not
available through the known hosted tools. The supported custom-server flow is
**Plugins → Add custom MCP server**, using `https://mcp.astria.ai/mcp` and OAuth;
the user completes sign-in and the host's required confirmations. Keep any
text-only work moving while connection is unavailable.

## Other hosts

Use the host's native Astria connection/login flow. For Claude's MCP-backed
plugin, connect from its Connectors tab. Codex commands do not configure Claude
or other hosts.
