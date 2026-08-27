# FormBharo skills

An Agent Skill for the [FormBharo](https://formbharo.artpark.ai) public API.
FormBharo runs voice agents that fill in a form by talking to someone on a call.

The skill teaches a coding agent how to build an agent, edit it, pull the answers
people gave, and read the numbers back. It follows the
[Agent Skills](https://agentskills.io) open standard, so it works with Claude Code,
Cursor, Windsurf, Codex, and other compatible tools.

This repository is public. You do not need any credentials to install it.

## Install

Pick the command for your tool. Without `--agent`, the installer picks whichever
tool it finds first, which may not be the one you want.

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

Restart your session after installing so the skill is picked up.

### Install by hand

```bash
git clone https://github.com/ARTPARK-SAHAI-ORG/formbharo-skills.git
cp -r formbharo-skills/skills/formbharo ~/.claude/skills/formbharo
```

Use `.cursor/skills/` for Cursor, and the equivalent directory for other tools.
Copy the whole `formbharo` folder, not just `SKILL.md`, because `SKILL.md` links to
the files in its `references/` folder.

## What is here

```
skills/formbharo/
  SKILL.md                              the skill
  references/agent-config.md            the shape of an agent: questions, validation, branches
  references/recipes.md                 four jobs, start to finish, with commands that were run
  references/talking-about-results.md   how to report numbers to a person without misleading them
```

## Before you use it

You need one thing: an API key. Create one in the web app by clicking your profile
picture in the top right, then **API keys**. The key is shown once and never
again. It starts with `fb_live_`.

There is nothing for you to run. Ask your tool for anything to do with FormBharo,
and the first time it needs the key it will ask you for it. Paste it in. It saves
the key for you and never asks again.

If you would rather set it yourself, it lives in an environment variable named
`FORMBHARO_API_KEY`. Check it works:

```bash
curl -s -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  https://api.formbharo.artpark.ai/api/v1/agents
```

A list of your agents, or `[]` if you have none yet, means you are set up.

## API reference

The endpoint list is served by the server itself and needs no key:

```bash
curl -s https://api.formbharo.artpark.ai/api/v1/openapi.json
```

There is a browsable version of the same thing at
https://api.formbharo.artpark.ai/api/v1/docs.

## License

MIT
