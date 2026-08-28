# formbharo-skills

Everything here is writing that someone reads. The README is read by a person
deciding whether to use FormBharo. The skill files are read by a coding agent that
then goes and does what they say. There is no code to hide behind.

## Only write what the reader needs

Never write a sentence about something the reader does not have to do, or does not
have to know. "There is nothing to run." "No setup needed." "You do not have to
configure anything."

Write the thing they do have to do. If nothing is needed from them, the sentence is
not needed either, cut it.

This is the rule broken most often. A section that opens by telling the reader what
they can skip has told them nothing and taken a paragraph to do it.

## Name the thing

Say what the reader is actually asking for, not a stand-in word for it. If a phrase
would sound vague said out loud, it is vague.

Two that were in this README and had to be rewritten:

- "ask your tool for FormBharo things". Which things? Write the ask: "build you an
  agent that asks people their name and age, in Hindi".
- "your tool", "other tools". Which tool? Name them: Claude Code, Cursor, Windsurf,
  Codex.

Use the words already in the FormBharo product and the API. Do not invent terms and
do not turn a phrase into a term with capitals or quotes.

## The rest

Plain words. Short lines. One idea per sentence. No em-dashes. Write for someone who
is not an engineer.

Labels name what they act on: "Create the agent", not "Create it".

## Before you change a skill file

Read the whole file first. An agent follows these literally, so a half-updated
instruction is worse than the one it replaced.

After any rename, grep the repo for the old name. The skill files link to each other
and into `references/`, and a dead link leaves the agent without the page it was
told to go and read.

Every command in `references/recipes.md` was run against a real server and shows the
output that came back. Do not add one you have not run.

Every skill opens with a `## Get the latest instructions` section that updates
itself and tells the agent to re-read the file from disk. `main` is served live,
so an installed copy can be months old. A new skill copies that section word for
word and swaps in its own name. `scripts/check_skills.py` fails if it is missing.
