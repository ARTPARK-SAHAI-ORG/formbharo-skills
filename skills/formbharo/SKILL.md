---
name: formbharo
description: Drive the FormBharo public API. Build or edit a voice form agent, pull
  the answers people gave on calls, and check how an agent is doing. Use when the
  user says "FormBharo", "form bharo", "voice form agent", "form filling agent",
  "build an agent that asks people X", "add a question to my agent", "get last
  week's calls", "export the answers", "how is my agent doing", "completion rate",
  or names an agent id and asks for its calls or its numbers.
argument-hint: "[agent-id-or-what-you-want-to-collect]"
---

# FormBharo

FormBharo runs voice agents that fill in a form by talking to someone. You give an
agent a list of questions, the words to say for each one, and a language. The agent
calls someone or is called, holds the conversation, and saves each answer under the
question's name. Every call is stored with its answers and how far it got, and you
read all of that back over the API.

## Setup

Two values, both from the environment:

- `FORMBHARO_API_KEY`: the key, which starts with `fb_live_`.
- `FORMBHARO_API_URL`: the address of the FormBharo API. It is not the same address
  as the web app.

If either is missing, ask the user for it. Do not guess the address.

The key goes on every request:

```bash
curl -s -H "Authorization: Bearer $FORMBHARO_API_KEY" "$FORMBHARO_API_URL/api/v1/agents"
```

To make a key, the user signs in to FormBharo, opens Settings, then the API keys
tab, and creates one. The token is shown once and never again. A key can do
everything the person who made it can do, except create or revoke other keys.

Two requests need no key at all, so a page you build yourself can use them without
holding a secret: reading one call's answers, and correcting them. Both are in
[`references/recipes.md`](references/recipes.md).

## Find the endpoints in the schema, not here

There is no endpoint list in this file on purpose. Fetch it:

```bash
curl -s "$FORMBHARO_API_URL/api/v1/openapi.json"
```

That needs no key. It is generated from the running server, so it always matches
what is actually there. A list written down in this file would slowly drift out of
date as the API changes, and you would build a request against something that no
longer exists. Read the schema first, then build the request.

## Where to go next

- [`references/agent-config.md`](references/agent-config.md): the shape of an
  agent. Question types, the words the agent speaks, validation, what happens when
  an answer does not come through, and asking a question only when an earlier answer
  went a certain way.
- [`references/recipes.md`](references/recipes.md): four jobs from start to
  finish, with commands that were run against a real server. Build an agent from a
  description of a form. Pull last week's calls and summarise the answers. Export
  the answers to a spreadsheet. Run a call from your own page.
- [`references/talking-about-results.md`](references/talking-about-results.md):
  how to report the numbers to a person without misleading them.

## Gotchas

These cause wrong answers and none of them are visible in the schema.

**A skipped answer is saved as `null`.** Counting answers with a plain "is it
truthy" test throws away every `0`, every `false` and every empty string too. Use
`form_status` instead: each field there is `"answered"`, `"skipped"` or `"empty"`.
Answered means the person said it. Skipped means the agent moved on. Empty means
the call never got that far.

**Screened out counts as complete in the numbers.** A call that ended early on
purpose, for example the person said no to a consent question, has status
`screened_out`. In the analytics it is added to `completed`, so `completion_rate`
includes it. `screened_out` is also reported on its own, so subtract it when you
want only the fully collected forms.

**`created_at` is when the call's answers were last written, not when it started.**
Correcting an answer later moves the call to the top of the list. Filtering with
`since` and `until` is close enough for day-level questions and wrong for anything
finer.

**Nothing tells you when a call ends.** There is no callback and no push. To pick up
new calls, ask again on a timer:

```bash
curl -s -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  "$FORMBHARO_API_URL/api/v1/conversations?since=1787626937&limit=200"
```

`since` is unix seconds, and it is an example number here. Move it forward to the
newest `created_at` you have already seen. It is inclusive, so that newest call
comes back one more time: skip the `conversation_id` values you already have.
