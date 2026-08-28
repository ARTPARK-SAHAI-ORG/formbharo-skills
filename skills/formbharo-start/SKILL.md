---
name: formbharo-start
description: >-
  Take someone from nothing to their first working FormBharo voice agent in one
  sitting: get the key, ask what they want to collect, build the agent, hand them
  a link they can call. Use when the user says "get started with FormBharo",
  "set up FormBharo", "onboard me", "first FormBharo agent", "I just installed
  FormBharo", or types /formbharo-start. For anything after the first agent, use
  the `formbharo` skill instead.
argument-hint: "[what you want to collect on the call]"
---

# Start with FormBharo

FormBharo runs voice agents that fill in a form by talking to someone on a call.
This walks a first-time user from nothing to an agent they can ring up and try.

Every command you need is in the [`formbharo`](../formbharo/SKILL.md) skill. This
one is only the order to do things in, and what to say while you do them.

Build the agent for real. Do not describe what you would build and stop.

## How to talk during this

The person on the other end may have never written a line of code. So:

- Ask, build, hand over a link. No tours of the API.
- Never say endpoint, payload, config, schema, draft state or agent id unless they
  ask. Say "your agent", "the call page", "the questions it asks".
- Three short questions at once beats ten short questions one at a time.
- If they already told you what they want, do not ask again. Build it.

## 1. The key

Run the check in [Setup](../formbharo/SKILL.md#setup). A list back, even an empty
one, means they are set up: say nothing about keys and go to step 2.

Otherwise they have no key yet. Tell them, in your own words:

- FormBharo needs a key so it knows the calls are yours.
- Sign in at https://formbharo.artpark.ai, click the profile picture in the top
  right, then **API keys**, and make one. It is shown once and never again.
- Paste it here.

When they paste it, save it the way [Setup](../formbharo/SKILL.md#setup) says,
before you do anything else. They should never have to hand it over again.

## 2. What the call is for

Ask these three things in one message:

- What do you want to find out on the call? List them the way you would say them
  out loud.
- What language should the call be in?
- Who is making the call, and who is answering? For example a health worker calling
  a patient, or a shop owner calling a customer.

That is enough to build something real. Everything else has a sensible default and
they can change it later.

If their answer is vague, guess a first version and show it to them rather than
asking again. It is faster to correct a real agent than to describe one.

## 3. Build it

Follow [recipe 1](../formbharo/references/recipes.md) exactly. Read
[`agent-config.md`](../formbharo/references/agent-config.md) first if they asked for
anything beyond plain questions, such as a question that only comes up when an
earlier answer went a certain way.

Two things that go wrong here:

- **A new agent is a draft, and nobody can call a draft.** Creating it and
  publishing it are two separate requests with the same body. Recipe 1 shows both.
  Do not stop after the first one.
- **Write the spoken lines in the language they asked for.** The `script` on each
  question is what the agent actually says. English questions with a Hindi
  `language` gives a call in the wrong language.

Then read the agent back and check the questions are all there before you promise
anything.

## 4. Hand it over

Give them the call page:

```
https://formbharo.artpark.ai/agents/<the new agent's id>
```

Tell them to open it and do the call themselves, once, out loud. That is the fastest
way to hear a question that reads fine and sounds wrong. Nothing else finds those.

Then say what they can do next, in one line each:

- Change the wording: tell you what to fix and you will fix it.
- Share that link with the people they want to call it.
- Come back and ask for the answers once calls have happened.

## 5. Only when they ask

Do not run ahead into these. Say they exist, in one line, and stop.

- Reading the answers back and counting them:
  [recipe 2](../formbharo/references/recipes.md).
- Getting the answers into a spreadsheet:
  [recipe 3](../formbharo/references/recipes.md).
- Putting the call on their own web page:
  [recipe 4](../formbharo/references/recipes.md).

Before reporting any numbers to them, read
[`talking-about-results.md`](../formbharo/references/talking-about-results.md).
