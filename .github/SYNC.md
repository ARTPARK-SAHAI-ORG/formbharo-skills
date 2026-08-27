# Keeping the skill current

The skill hardcodes the FormBharo API: the address, every endpoint path, the
shape of what you send and what comes back. That moves without anyone here
noticing. [`sync-from-spec.yml`](workflows/sync-from-spec.yml) watches for it.

The skill is prose, not generated, so it cannot be rebuilt from the API
description. Instead Claude reads what changed, reads the skill, and makes the
edits the change calls for. The result opens as a pull request. Nothing is
merged automatically.

## Where the change comes from

`form-fill-agent` deploys to production, then commits the API schema into
`formbharo-docs`. That repo is public, and its history of
`api-reference/openapi.json` is the record of what the API looked like after
every deploy.

```
form-fill-agent ──(deploy)──► formbharo-docs   commits api-reference/openapi.json
                │
                └─(trigger)─► formbharo-skills reads the last two versions,
                                               diffs them, Claude edits → PR
```

So this repo stores no copy of the schema and needs no password to read one. The
difference between the docs repo's last two versions of that file is exactly what
the latest deploy changed.

## What a run does

1. Clones `formbharo-docs` and takes the two most recent commits that touched
   `api-reference/openapi.json`. Both copies are rewritten with sorted keys
   first, so the difference shows real API changes rather than however the schema
   happened to be written that day.
2. If they match, or there is only one, the run stops there and costs nothing.
3. Otherwise Claude gets the difference, reads the skill, and edits what the
   change makes wrong or incomplete. Most API changes touch nothing here.
4. If Claude changed nothing, no pull request opens.
5. If Claude did change something, `check_skills.py` runs, one pull request opens
   on `automated/spec-sync`, and an email goes out with the link if the mail
   secrets below are set.

It also runs weekly and on demand, so a deploy that fails to fire the trigger is
still caught within a week.

## Reruns are safe

The branch is fixed, so a second run over the same API change updates that pull
request instead of opening another one. And once it is merged, a rerun reads the
same difference, finds the skill already correct, and opens nothing.

## What form-fill-agent sends

One step in `deploy_backend.yml`, after the schema is pushed to the docs repo:

```yaml
- name: Tell formbharo-skills the API changed
  run: |
    curl -fsSL -X POST \
      -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      https://api.github.com/repos/ARTPARK-SAHAI-ORG/formbharo-skills/dispatches \
      -d '{"event_type":"sync-api-spec"}'
```

No file travels with it. It only says "go and look".

The token needs write access to this repo, because that is what GitHub requires
to start a workflow in another repository. `form-fill-agent` already has
`DOCS_REPO_TOKEN` for the docs push; widening that one to cover this repo is
enough, or set a separate `SKILLS_REPO_TOKEN` there. If neither is set the deploy
still succeeds and says so in its summary, and the weekly run catches the change.

## Config on this repo

- **Secret `CLAUDE_CODE_OAUTH_TOKEN`** — required. Without it the step that works
  out what the skill needs cannot run.
- **Secrets `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`** —
  optional. Without them the pull request still opens and GitHub still emails
  the assignee; only the extra email is skipped.
- **Secret `SKILLS_SYNC_TOKEN`** — optional. A token so the pull request starts
  `skill-check`; one opened by GitHub's own token does not start further checks.
  Without it the pull request still opens, just without an automatic check.

## When the pull request is wrong

Claude wrote it, so read it as a draft by a colleague rather than a fact. The
body says which files changed and why, and whether the skill is still
installable. Edit the branch and merge it, or close it. Closing loses nothing:
the next deploy that changes the API opens a fresh one.
