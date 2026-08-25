# The shape of an agent

What you send to `POST /api/v1/agents` and to `PUT /api/v1/agents/{agent_id}`. The
same body works for both. There is no partial update: read the current config,
change it, and send the whole thing back.

## Whole-agent fields

- `title`: the name of the agent. Required.
- `language`: the language the call is held in, for example `"Hindi"`.
- `questions`: the list of things to collect. Required, and covered below.
- `branches`: groups of questions that are only asked in some calls. Covered below.
- `agent_persona`: who the agent is, for example
  `"community health worker doing a short screening call"`.
- `user_persona`: who it is talking to, for example
  `"patient answering about themselves"`.
- `description`: background about the form that the agent is told.
- `ai_instructions`: how to run the call.
- `agent_speaks_first`: `true` means the agent opens the call. Defaults to `true`.
- `ask_questions_one_by_one`: `true` means one question at a time. Defaults to `true`.
- `scripts`: `intro` is the first thing said, `outro` is said when the form is
  finished, and `outro_incomplete` is said when the call ends early. Sending
  `outro_incomplete` without `outro` is rejected.
- `mute_user_while_agent_speaking`: `true` mutes the person's microphone while the
  agent talks, so the agent does not hear itself. Defaults to `false`.
- `send_hearing_acknowledgements`: whether the agent says a short "got it" before
  its reply. Defaults to `true`.
- `hearing_acknowledgement_mode`: `"fixed"` uses set phrases, `"llm"` lets the agent
  word it. Defaults to `"fixed"`.
- `hearing_acknowledgement_phrases`: the set phrases to use, when the mode is fixed.
- `workspace_id`: which workspace the agent belongs to. Only read when creating.
  Left out, it goes in the creator's own workspace.

## One question

```json
{
  "name": "age",
  "question": "How old are you?",
  "response_type": "number",
  "number_format": "integer",
  "required": true,
  "script": "Aapki umar kitni hai?",
  "validation": { "type": "number_range", "rules": { "min": 0, "max": 120 } }
}
```

- `question`: the field in plain English. This is what shows in the builder.
- `response_type`: one of `string`, `number`, `date`, `boolean`, `single-select`,
  `multi-select`.
- `name`: the key the answer is saved under. Leave it out and the server makes one
  by lower-casing the question and joining the words with underscores. Set it
  yourself. The made-up one changes if the wording changes, and then old calls and
  new calls no longer line up.
- `script`: the exact words the agent speaks. Write it in the call's language.
  Without a script the agent words the question itself, differently each time.
- `required`: `true` means the call cannot finish without it.
- `number_format`: `integer` or `decimal`, for a `number` question.
- `options`: the list of choices, for `single-select` and `multi-select`.
- `boolean_labels`: what yes and no are called out loud, for example
  `{"true": "Haan", "false": "Nahin"}`.
- `skip_message`: what the agent says as it moves past a question it gave up on.
- `advanced_instructions`: a note to the agent about this one question.
- `end_call_values`: answers that end the call early on purpose, for example a
  consent question where "No" stops everything. Those calls are marked
  `screened_out`.
- `branch_id`: the branch this question belongs to. See below.

## Checking the answer

`validation` is `{"type": ..., "rules": {...}}`. The types:

| `type` | `rules` | What it checks |
| --- | --- | --- |
| `number_range` | `min`, `max` | The number is between the two. |
| `phone_number` | `digits` | It is a phone number of that many digits. |
| `min_length` | `min_length` | The answer is at least that long. |
| `exact_num_digits` | `digits` | It has exactly that many digits. |
| `date_today_or_past` | none | It is a DD-MM-YYYY date, today or earlier. |
| `date_future` | none | It is a DD-MM-YYYY date, after today. |
| `regex` | `pattern`, `message` | It matches the pattern. `message` is what the person is told when it does not. |
| `free_text` | `description` | The answer fits the description, judged in words rather than by a rule. |

When the config is read back, whatever you set is also written out as an English
sentence under `validation_rules`. That is generated. Do not send it.

## When the answer does not come through

`retry_config`, per question:

```json
{
  "allow_retries": true,
  "max_retries": 2,
  "retry_messages": ["Maaf kijiye, samajh nahin aaya. Kitne din se bukhar hai?"],
  "exhausted_action": "skip"
}
```

- `allow_retries`: `false` means never ask again. Defaults to `true`.
- `until_answered`: `true` means keep asking forever, and `max_retries` is ignored.
  Defaults to `false`.
- `max_retries`: how many times to ask again after the first ask. Defaults to `2`,
  so the question is asked once and then twice more.
- `retry_messages`: the exact words for each re-ask. The first entry is the first
  re-ask, the second entry the second, and so on. A missing entry means the
  question's `script` is spoken again as it is.
- `exhausted_action`: what happens once the re-asks run out, for an optional
  question. `"skip"` moves on to the next question. `"end_call"` ends the call.
  Defaults to `"skip"`. A required question always ends the call.

## Asking a question only sometimes

Put the follow-up questions in a branch, and the branch only opens when an earlier
answer went a certain way.

```json
{
  "questions": [
    { "name": "has_fever", "question": "Do you have a fever?", "response_type": "boolean", "required": true },
    { "name": "fever_days", "question": "How many days?", "response_type": "number", "branch_id": "fever_details" }
  ],
  "branches": [
    { "id": "fever_details", "condition": { "field": "has_fever", "equals": true } }
  ]
}
```

`field` is the `name` of the question that decides. The controlling question must
come before the questions that depend on it. A condition sets exactly one of these:

- `equals`: `true` or `false`. The controlling question must be a `boolean`. The
  branch opens when the answer matches.
- `present`: works with any question type. `true` opens the branch when the
  controlling question was answered, `false` when it was skipped. It does not look
  at the value.

## The saved config is named differently

Read an agent back with `GET /api/v1/agents/{agent_id}` and some keys have changed
name. This catches people out when they read a config and send it straight back.

| You send | It is saved as |
| --- | --- |
| `question` | `label` |
| `response_type` | `type` |
| `description` | `context` |
| `ai_instructions` | `instructions` |

`name`, `script`, `required`, `validation`, `retry_config`, `branch_id`, `options`,
`boolean_labels` and `number_format` keep their names.

## Draft and published

A newly created agent is a draft. The web app marks it Draft and greys out its share
and play buttons, so nobody can start a call from it. Send the same body again as a
`PUT` and it becomes published. That second save is also the one that saves version
1. Drafts are not versioned.

## When it is rejected

A bad body comes back 400 with a list, one entry per problem:

```json
{"validation_issues":[{"field":"scripts.outro","message":"Outro is required when outro_incomplete is provided."}]}
```

Fix every entry and send it again.
