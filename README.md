# Astria AI Skills

Skills and a CLI for the [Astria](https://www.astria.ai) API — AI image & video
generation, fine-tuning (tunes / references), prompt writing, and automated
photoshoot packs — packaged as native OpenAI/Codex and Claude plugins.

## Install in Codex

Add this repository marketplace, then install Astria:

```bash
codex plugin marketplace add astriaai/skills --ref main
codex plugin add astria@astria
```

To fetch a newer repository snapshot:

```bash
codex plugin marketplace upgrade astria
codex plugin add astria@astria
```

Start a new task after installing or upgrading so the refreshed skills load.

ChatGPT workspace administrators can import `astriaai/skills` as a GitHub
marketplace. Imported marketplaces sync daily and can be refreshed immediately
with **Sync now**. Public web, desktop, and mobile availability begins after
OpenAI reviews and publishes the plugin in the universal directory.

## Install in other agents

The quickest way — cross-agent, works in Claude Code, Cursor, and other
agents:

```bash
npx skills add astriaai/skills
```

Inside Claude Code, install via the plugin marketplace:

```
/plugin marketplace add astriaai/skills
/plugin install astria@astria
```

Then authenticate once:

```
astria login
```

`astria login` prompts for an API key — get one at
[astria.ai/users/edit/api](https://www.astria.ai/users/edit/api). It is stored
in `~/.astria/config.json`. **No environment variables to export.**

The skills then load automatically when relevant, and every Astria operation
runs through the bundled `astria` CLI — so you only ever approve
`Bash(astria:*)`, never raw network access.

**Not using Claude Code?** The `astria` CLI installs standalone from
[`astriaai/cli`](https://github.com/astriaai/cli):

```
curl -fsSL https://raw.githubusercontent.com/astriaai/cli/main/install.sh | sh
```

The plugin bundles a vendored copy of that same CLI, so a marketplace install
needs nothing extra.

## Developing and releasing

Run `scripts/sync-plugin.sh` after adding or renaming a skill. It rebuilds the
self-contained OpenAI plugin in `plugins/astria` and refreshes all
`~/.claude/skills` and `~/.codex/skills` symlinks. CLI synchronization invokes
it automatically.

Prepare releases with one command:

```bash
scripts/release-plugin.sh X.Y.Z
```

See [`docs/PUBLISHING.md`](docs/PUBLISHING.md) for the complete publishing and
upgrade flow.

## Requirements

- **Python 3.8+** and **curl** — both standard on macOS and Linux. The `astria`
  CLI uses only the Python standard library; nothing to `pip install`.

## Skills

| Skill | What it does |
|-------|--------------|
| **astria-api** | The `astria` CLI reference — tunes, prompts, packs, generate, video, variate |
| **prompt-writing** | Prompt syntax, parameters, and writing effective prompts |
| **packs-guide** | Pack templates, categories, and photoshoot workflows |
| **unique-headshot** | Generate diverse, realistic headshots with no reference |
| **navigation** | Astria app sitemap |
| **landing-page-editor** | Edit a workspace's magazine-style landing page |
| **templatize-page** | Turn a lookbook URL into a pose-swap pack |
| **storyboard** | Build a text-only cinematic video sequence from a draft or ordered image references |
| **artboard** | Legacy alias for Storyboard |

## The `astria` CLI

`astria` wraps the Astria API. A taste:

```bash
astria login                          # store an API key
astria whoami                         # show the account
astria models                         # current model -> tune-id mapping
astria tunes list --title "dress"     # find references
astria generate --text "<faceid:123:1> woman, white studio" --num-images 4
astria video --video-model seedance2_fast_720p \
  --video-prompt "<faceid:1234:1> woman walks down a runway" --duration 5
astria video --video-model seedance2_fast_720p \
  --video-prompt "woman wearing a dress walks down a runway" \
  --reference woman=./model.jpg --reference dress=./dress.jpg
astria video --video-model seedance2_fast_720p \
  --video-prompt "transition through these looks in order" \
  --image-reference ./look-1.jpg --image-reference ./look-2.jpg
astria variate ./source.mp4 --reference ./dress.jpg \
  --brief "Keep the performance and replace the wardrobe" --wait
astria packs list
astria api GET /prompts --query limit=5   # raw escape hatch
```

Run `astria --help`, or see the **astria-api** skill for the full reference.
`astria help` is equivalent, including command paths such as
`astria help variate`; use `astria -v`, `astria --version`, or
`astria version` for the installed version.

Credentials resolve from environment variables first (`ASTRIA_API_KEY` /
`ASTRIA_AUTH_TOKEN`, …), then `~/.astria/config.json`. Scope any command to a
workspace with `-w <id>` (or `-w all`).

**Profiles** work like the AWS CLI — separate credentials and base URLs per
profile, handy for a local dev server:

```bash
astria --profile localhost login --base-url http://localhost:3000
ASTRIA_PROFILE=localhost astria whoami
```

`--profile <name>` (before the subcommand) or `ASTRIA_PROFILE` selects one;
each lives in its own `~/.astria/config.<name>.json`.

## License

MIT
