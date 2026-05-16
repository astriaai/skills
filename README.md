# Astria Claude Code Plugin

Skills and a CLI for the [Astria](https://www.astria.ai) API — AI image & video
generation, fine-tuning (tunes / references), prompt writing, and automated
photoshoot packs — packaged as a Claude Code plugin.

## Install

In Claude Code:

```
/plugin marketplace add astriaai/astria-claude-skills
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

## Requirements

- **Python 3.8+** and **curl** — both standard on macOS and Linux. The `astria`
  CLI uses only the Python standard library; nothing to `pip install`.

## Skills

| Skill | What it does |
|-------|--------------|
| **astria-api** | The `astria` CLI reference — tunes, prompts, packs, generate, video |
| **prompt-writing** | Prompt syntax, parameters, and writing effective prompts |
| **packs-guide** | Pack templates, categories, and photoshoot workflows |
| **unique-headshot** | Generate diverse, realistic headshots with no reference |
| **navigation** | Astria app sitemap |
| **landing-page-editor** | Edit a workspace's magazine-style landing page |
| **templatize-page** | Turn a lookbook URL into a pose-swap pack |
| **instagram-movie-producer** | Build fast-cut Instagram Reels with keyframed video |

## The `astria` CLI

`astria` wraps the Astria API. A taste:

```bash
astria login                          # store an API key
astria whoami                         # show the account
astria models                         # current model -> tune-id mapping
astria tunes list --title "dress"     # find references
astria generate --text "<faceid:123:1> woman, white studio" --num-images 4
astria video  --text "a model on a runway" \
              --video-model seedance2_fast_720p --video-prompt "camera tracks her"
astria packs list
astria api GET /prompts --query limit=5   # raw escape hatch
```

Run `astria --help`, or see the **astria-api** skill for the full reference.

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
