# Astria Claude Skills — repository guide

This repo is a **Claude Code plugin marketplace**. It is consumed two ways:

1. **Install** — `npx skills add astriaai/skills` (cross-agent), or
   `/plugin marketplace add astriaai/skills` in Claude Code. The repo root *is*
   the plugin. See `README.md`.
2. **Astria web chat agent** — the `worker/chat-helper` worker bundles these
   skills and the `astria` CLI into its sandbox, alongside its own private
   embedded skills (`worker/chat-helper/embedded-skills/`) and system prompt.

## Layout

The repo root is the plugin — skill directories sit at the top level so
`npx skills` discovers them, mirroring `higgsfield-ai/skills`.

```
.claude-plugin/
  marketplace.json                  marketplace catalog + skill list
  plugin.json                       plugin manifest
<name>/SKILL.md                     public skills (one dir per skill, at root)
bin/astria                          the astria CLI — VENDORED, see below
hooks/hooks.json                    SessionStart auth check
scripts/sync-cli.sh                 re-vendor the CLI from astriaai/cli
README.md                           install + usage
```

Adding or renaming a skill: create/rename its top-level `<name>/SKILL.md`
directory and update the `skills` array in `.claude-plugin/marketplace.json`.

## The `astria` CLI

`bin/astria` is the single entry point for the Astria API. It
resolves credentials from environment variables first, then
`~/.astria/config.json` (written by `astria login`). Every skill calls
`astria …` — never raw `curl`, never API tokens in skill text.

This is deliberate: it keeps the permission surface to one rule
(`Bash(astria:*)`), and marketplace users run `astria login` once instead of
exporting a fistful of environment variables.

**Source of truth: the [`astriaai/cli`](https://github.com/astriaai/cli) repo.**
`bin/astria` is a *vendored copy* so marketplace installs and the
web agent need no bootstrap. Edit the CLI in `astriaai/cli`, then re-vendor here
with `scripts/sync-cli.sh [ref]`. Standalone users install it directly via
`curl -fsSL https://raw.githubusercontent.com/astriaai/cli/main/install.sh | sh`.

## Conventions for skills

- Each `SKILL.md` has `name`, `description`, and — if it runs commands —
  `allowed-tools` frontmatter (e.g. `Bash(astria:*)`), which pre-authorizes
  those tools so the skill runs without permission prompts.
- Public skills must NOT reference environment variables, raw `curl`, or the
  `[ASTRIA_*]` web-chat browser protocol. Those belong to the embedded layer
  in `worker/chat-helper/` (private), which the web agent loads on top.
- Document any new API surface as `astria` CLI verbs in the `astria-api` skill;
  add the verb to `bin/astria`.

## Testing

```bash
bin/astria --help
python3 -m py_compile bin/astria
bin/astria login --api-key <key> && bin/astria whoami
```
