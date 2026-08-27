# FormBharo skills

Agent Skills for the [FormBharo](https://formbharo.artpark.ai) public API.
FormBharo runs voice agents that fill in a form by talking to someone on a call.

They teach a coding agent how to build an agent, edit it, pull the answers
people gave, and read the numbers back. They follow the
[Agent Skills](https://agentskills.io) open standard, so it works with Claude Code,
Cursor, Windsurf, Codex, and other compatible tools.

This repository is public. You do not need any credentials to install it.

## Install

Pick your command below. Without `--agent`, the installer picks whichever of these
it finds on your machine first, which may not be the one you want.

```bash
# Claude Code
npx skills add ARTPARK-SAHAI-ORG/formbharo-skills --agent claude-code -g

# Cursor
npx skills add ARTPARK-SAHAI-ORG/formbharo-skills --agent cursor

# Windsurf
npx skills add ARTPARK-SAHAI-ORG/formbharo-skills --agent windsurf

# Codex
npx skills add ARTPARK-SAHAI-ORG/formbharo-skills --agent codex
```

See what is in here before installing:

```bash
npx skills add ARTPARK-SAHAI-ORG/formbharo-skills --list
```

Restart your session after installing so the skills are picked up.

## First time? Type this

```
/formbharo-start
```

It asks what you want to find out on the call, builds the agent, and gives you a
link you can ring up and try. Nothing to set up first. It asks for your API key
along the way and saves it, so you are asked once and never again.

After that first agent, just say what you want in your own words. "Add a question
about age." "Show me last week's calls." "Put the answers in a spreadsheet."

### Install by hand

```bash
git clone https://github.com/ARTPARK-SAHAI-ORG/formbharo-skills.git
cp -r formbharo-skills/skills/formbharo ~/.claude/skills/formbharo
cp -r formbharo-skills/skills/formbharo-start ~/.claude/skills/formbharo-start
```

Those paths are for Claude Code. Cursor reads `.cursor/skills/`, and Windsurf and
Codex each have their own skills folder.

Copy both folders whole, not just the two `SKILL.md` files, because they link to
the files in `references/`. `formbharo-start` leans on `formbharo`, so you need
both.

## What is here

```
skills/formbharo/
  SKILL.md                              the skill
  references/agent-config.md            the shape of an agent: questions, validation, branches
  references/recipes.md                 four jobs, start to finish, with commands that were run
  references/talking-about-results.md   how to report numbers to a person without misleading them

skills/formbharo-start/
  SKILL.md                              the guided first run: key, first agent, link to call
```

## Before you use it

Make an API key. Sign in at https://formbharo.artpark.ai, click your profile
picture in the top right, then **API keys**. The key is shown once and never
again. It starts with `fb_live_`.

Keep the key to hand. Now ask Claude Code, Cursor, or whichever one you installed
this into, to build you an agent: "ask people their name and age, in Hindi". The
first time it needs your key it will ask for it. Paste it in. It saves the key, so
you only do that once.

To check a key yourself, put it in `FORMBHARO_API_KEY` and run:

```bash
curl -s -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  https://api.formbharo.artpark.ai/api/v1/agents
```

A list of your agents, or `[]` if you have none yet, means the key works.

## API reference

The endpoint list is served by the server itself and needs no key:

```bash
curl -s https://api.formbharo.artpark.ai/api/v1/openapi.json
```

There is a browsable version of the same thing at
https://api.formbharo.artpark.ai/api/v1/docs.

## License

MIT
