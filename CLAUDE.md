# Astria skills — repository guide

The canonical public skills live in top-level `<name>/SKILL.md` directories.
The root is a Claude marketplace plugin; `plugins/astria` is the generated
portable OpenAI/Codex package. The Astria web-agent sandbox also bundles these
skills with its independently authenticated CLI and private embedded skills.

## API transport

Installed plugins use OAuth-connected Astria MCP tools for supported API
operations. The host owns login, token storage and refresh. Use live tool
schemas; names may have a host namespace. Never read host credentials or
silently fall back to the CLI after an MCP authentication failure.

The CLI remains available for local files, downloads, video inspection/Variate,
workspace/template creation, landing pages, board edits and agent handoff.
It has separate authentication. The embedded Astria web-agent sandbox may
expose only the authenticated CLI; preserve that supported environment.
Conditional instructions live in `astria-api/references/cli.md`, not in the
default MCP entrypoint. Never build a second API client in skills.

`bin/astria` is vendored from [astriaai/cli](https://github.com/astriaai/cli).
Change the canonical CLI there, then run `scripts/sync-cli.sh [ref]`. Shared
operation definitions and argparse generate MCP schemas; add new remote-safe
parameters there and synchronize Rails through `bin/sync-astria-mcp`.

## Packaging

- `.claude-plugin/marketplace.json` owns the canonical skill list. Add each
  skill as a `"./<name>"` path.
- `mcp.json` owns the portable HTTPS endpoint. `scripts/sync-plugin.py`
  generates root and packaged `.mcp.json` HTTP compatibility configs.
- `scripts/sync-plugin.sh --no-local-links` copies canonical skills (including
  references), manifests, MCP configuration and the vendored CLI to
  `plugins/astria`. Without that flag it also refreshes developer symlinks.
- No SessionStart CLI-auth hook: OAuth is managed by the host.
- Keep skill frontmatter descriptions focused; retain shell permissions only
  for skills that actually need optional terminal workflows.
- Public skills must not depend on private web-chat browser command protocols.
  Composer tools apply only when the host exposes them.

## Validation

```bash
scripts/sync-plugin.sh --no-local-links
python3 scripts/validate-plugin.py
python3 scripts/build-plugin.py /tmp/astria-plugin-preview
```

The validator checks source/package parity, MCP wiring and skill JSON tool
examples against the vendored CLI's generated schemas. Also run relevant
Rails MCP specs if changing shared operation behavior. Deploying the endpoint,
registering OAuth clients and publishing a directory version are separate
release steps; see `docs/PUBLISHING.md`.
