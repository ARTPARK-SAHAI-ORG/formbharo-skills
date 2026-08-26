# Recipes

Every command below was run against a real FormBharo server with a real `fb_live_`
key, and the output shown is what came back. The agent id
`ae407c7d-ba18-4c40-b290-b14567e64ca5` and the call ids starting with `2f3a1b40-`
are from that run. They are examples. Swap in your own.

All commands assume:

```bash
export FORMBHARO_API_KEY=fb_live_...
```

---

## 1. Build an agent from a description of a form

Someone says: "I need to collect name, age, and whether they have a fever, in Hindi."

Turn each thing they want to collect into one entry in `questions`. The full shape,
every field and what it does, is in
[`agent-config.md`](agent-config.md). Read that before writing a big one.

Save this as `agent.json`:

```json
{
  "title": "Fever check",
  "language": "Hindi",
  "agent_persona": "community health worker doing a short screening call",
  "user_persona": "patient answering about themselves",
  "description": "A short fever screening call run in Hindi.",
  "ai_instructions": "Ask the questions in the given order. Speak the Script text as written.",
  "agent_speaks_first": true,
  "ask_questions_one_by_one": true,
  "scripts": {
    "intro": "Namaste. Main aapse bukhar ke baare mein teen chhote sawaal poochunga.",
    "outro": "Dhanyavaad. Saare sawaal ho gaye.",
    "outro_incomplete": "Theek hai, hum baad mein baat karenge. Dhanyavaad."
  },
  "questions": [
    {
      "name": "full_name",
      "question": "What is your name?",
      "response_type": "string",
      "required": true,
      "script": "Aapka naam kya hai?"
    },
    {
      "name": "age",
      "question": "How old are you?",
      "response_type": "number",
      "number_format": "integer",
      "required": true,
      "script": "Aapki umar kitni hai?",
      "validation": { "type": "number_range", "rules": { "min": 0, "max": 120 } }
    },
    {
      "name": "has_fever",
      "question": "Do you have a fever?",
      "response_type": "boolean",
      "required": true,
      "script": "Kya aapko is samay bukhar hai?",
      "boolean_labels": { "true": "Haan", "false": "Nahin" }
    },
    {
      "name": "fever_days",
      "question": "How many days have you had the fever?",
      "response_type": "number",
      "number_format": "integer",
      "required": false,
      "branch_id": "fever_details",
      "script": "Kitne din se bukhar hai?",
      "retry_config": {
        "allow_retries": true,
        "max_retries": 2,
        "retry_messages": ["Maaf kijiye, samajh nahin aaya. Kitne din se bukhar hai?"],
        "exhausted_action": "skip"
      }
    }
  ],
  "branches": [
    { "id": "fever_details", "condition": { "field": "has_fever", "equals": true } }
  ]
}
```

Create it:

```bash
curl -s -X POST "https://api.formbharo.artpark.ai/api/v1/agents" \
  -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  -H "Content-Type: application/json" \
  --data @agent.json
```

```json
{"id":"ae407c7d-ba18-4c40-b290-b14567e64ca5","workspace_id":"personal-44664ffc07d103a6"}
```

That agent is a draft, and nobody can start a call from a draft. Send the same body
again to publish it:

```bash
curl -s -X PUT "https://api.formbharo.artpark.ai/api/v1/agents/ae407c7d-ba18-4c40-b290-b14567e64ca5" \
  -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  -H "Content-Type: application/json" \
  --data @agent.json
```

```json
{"id":"ae407c7d-ba18-4c40-b290-b14567e64ca5","status":"updated","version":1}
```

Check what was saved:

```bash
curl -s -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  "https://api.formbharo.artpark.ai/api/v1/agents/ae407c7d-ba18-4c40-b290-b14567e64ca5"
```

Some keys come back under different names than you sent. `question` is saved as
`label` and `response_type` as `type`. The full list is in
[`agent-config.md`](agent-config.md).

Editing later works the same way: read the config, change it, `PUT` the whole thing
back. There is no partial update.

---

## 2. Pull last week's calls and summarise the answers

One request covers every agent the key can see.

```bash
SINCE=$(date -v-7d +%s)             # macOS
# SINCE=$(date -d '7 days ago' +%s) # Linux

curl -s -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  "https://api.formbharo.artpark.ai/api/v1/conversations?since=$SINCE&limit=200" > week.json
```

`since` and `until` are unix seconds. The other filters are `agent_id`,
`workspace_id`, `status` (`complete`, `screened_out`, `failed`, `in_progress`) and
`source` (`web` for a browser call, `twilio`, `exotel`, `websocket`).

The reply is `{"data": [...], "next_cursor": ...}`, newest call first. `limit`
defaults to 50 and must be between 1 and 200. Asking for more is refused with a 422,
it is not quietly cut down to 200. `next_cursor` is how many rows you have been given
so far, or `null` on the last page. Not null means ask again with `&cursor=<that
value>`. Calls that arrive between two page requests shift the rows along, so on a
busy agent a row can repeat or be missed while you page.

Each row carries `agent_id`, `agent_title`, `conversation_id`, `status`, `form_data`,
`form_status`, `filled_fields`, `total_fields`, `created_at`, `duration_secs`,
`source`, `caller_number` and `cost`.

### Reading the answers

`form_data` holds the answers, keyed by the question's `name`. `form_status` holds
what happened to each one: `answered`, `skipped` or `empty`.

A skipped answer is `null` in `form_data`. So is one the call never reached. Read
`form_status` to tell them apart, and never decide "they answered" by testing
whether the value is truthy: that also throws away `0`, `false` and `""`.

Answered, skipped and never-reached, per field:

```bash
jq -r '
  .data as $rows
  | ([$rows[].form_status | keys[]] | unique)[] as $f
  | [$f,
     ([$rows[] | select(.form_status[$f] == "answered")] | length),
     ([$rows[] | select(.form_status[$f] == "skipped")] | length),
     ([$rows[] | select(.form_status[$f] == "empty" or (.form_status[$f] | not))] | length)]
  | @tsv
' week.json
```

```
age	2	0	2
fever_days	0	1	3
full_name	4	0	0
has_fever	3	0	1
```

The columns are the field, then how many people answered it, how many had it skipped,
and how many calls never got that far. So: four calls, all four gave a name, two gave
an age, and on the days-of-fever question nobody answered, one person was skipped
past, and three calls ended before it came up.

Before you write any of that up for a person, read
[`talking-about-results.md`](talking-about-results.md).

For one agent only there is also
`GET /api/v1/agents/{agent_id}/conversations`, which takes the same filters plus
`include_transcript=false`. Use that when the transcripts would be huge and you only
want the answers.

---

## 3. Export the answers to a spreadsheet

One row per call, one column per question, in the order the agent asks them.

```bash
AGENT=ae407c7d-ba18-4c40-b290-b14567e64ca5

curl -s -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  "https://api.formbharo.artpark.ai/api/v1/agents/$AGENT" > agent_config.json

curl -s -H "Authorization: Bearer $FORMBHARO_API_KEY" \
  "https://api.formbharo.artpark.ai/api/v1/conversations?agent_id=$AGENT&limit=200" > calls.json

jq -r --slurpfile cfg agent_config.json '
  [$cfg[0].questions[].name] as $fields
  | (["conversation_id","status","created_at"] + $fields),
    ( .data[]
      | . as $r
      | [$r.conversation_id, $r.status, ($r.created_at | floor | todate)]
        + [ $fields[] as $f
            | $r.form_data[$f]
            | if . == null then "" else tostring end ] )
  | @csv
' calls.json > calls.csv
```

```
"conversation_id","status","created_at","full_name","age","has_fever","fever_days"
"2f3a1b40-0005-4c11-9a01-aaaaaaaa0005","screened_out","2026-08-24T03:01:39Z","Sunil","","",""
"2f3a1b40-0004-4c11-9a01-aaaaaaaa0004","complete","2026-08-23T03:01:39Z","Karan","28","true","1"
"2f3a1b40-0003-4c11-9a01-aaaaaaaa0003","failed","2026-08-20T03:01:39Z","Meena","","true",""
"2f3a1b40-0002-4c11-9a01-aaaaaaaa0002","complete","2026-08-19T03:01:39Z","Ravi","51","false",""
"2f3a1b40-0001-4c11-9a01-aaaaaaaa0001","complete","2026-08-18T03:01:39Z","Asha","34","true","3"
```

Notes on the shape:

- Column order comes from the agent config, so it matches the order the agent asks.
- A `multi-select` answer is already one string with the chosen labels separated by
  commas, for example `Cough, Fever`. It lands in a single cell as it is.
- An empty cell means no answer. It does not say whether the person skipped it or
  the call never reached it. To keep that, add a second set of columns from
  `form_status` beside the answers.
- Drop `| floor | todate` to keep the raw unix number instead of a date.
- Page it: if `next_cursor` in `calls.json` is not null, fetch the next page with
  `&cursor=<next_cursor>` and add the rows on.

Only want the calls where the form was finished? Add `&status=complete` to the
conversations request.

---

## 4. Run a call from your own page

The call itself runs on the FormBharo page for that agent:

```
https://formbharo.artpark.ai/agents/ae407c7d-ba18-4c40-b290-b14567e64ca5
```

That is the address the Share button in the web app copies. It only works once the
agent is published. Link to it from your own page, or open it in a new window.

Two requests need no key at all, so your page can call them straight from a browser
without holding a secret.

Show the questions on your own page before the call starts:

```bash
curl -s "https://api.formbharo.artpark.ai/api/v1/agents/ae407c7d-ba18-4c40-b290-b14567e64ca5/public"
```

```json
{"id":"ae407c7d-ba18-4c40-b290-b14567e64ca5","title":"Fever check","questions":[{"name":"full_name","label":"What is your name?","type":"string","required":true,"script":"Aapka naam kya hai?"}],"agent_speaks_first":true}
```

Read back what one call collected, given the agent id and the call id:

```bash
curl -s "https://api.formbharo.artpark.ai/api/v1/data/ae407c7d-ba18-4c40-b290-b14567e64ca5/2f3a1b40-0003-4c11-9a01-aaaaaaaa0003"
```

```json
{"form_data":{"full_name":"Meena","age":null,"has_fever":true,"fever_days":null},
 "form_status":{"full_name":"answered","age":"empty","has_fever":"answered","fever_days":"empty"}}
```

Correct an answer, for example when the person types a fix into your page afterwards:

```bash
curl -s -X PATCH \
  "https://api.formbharo.artpark.ai/api/v1/agents/ae407c7d-ba18-4c40-b290-b14567e64ca5/conversations/2f3a1b40-0003-4c11-9a01-aaaaaaaa0003/form_data" \
  -H "Content-Type: application/json" \
  -d '{"updates":{"age":44}}'
```

```json
{"form_data":{"full_name":"Meena","age":44,"has_fever":true,"fever_days":null},
 "form_status":{"full_name":"answered","age":"answered","has_fever":"answered","fever_days":"empty"}}
```

Setting a value flips that field's status to `answered`. It also counts as writing
to the call, so the call's `created_at` moves to now and it jumps to the top of the
conversation list.

Anyone who has both ids can do both of these. Treat a call id as private.

To find out which calls have happened, poll the conversation list with `since`, as
described in the skill's gotchas. There is no message when a call ends.
