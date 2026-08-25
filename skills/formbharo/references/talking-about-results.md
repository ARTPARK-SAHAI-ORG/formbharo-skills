# Talking about the results

The person asking is usually not the person who built the agent. Say what happened
on the calls, in the words they would use. Keep the field names out of it unless
they ask.

## Say how many people, not just the average

Every answer has a denominator. Give it.

- Wrong: "The average age is 31."
- Right: "2 of the 4 people who were called gave their age. Those two were 28 and 34."

An average over the people who answered, presented as the answer for everyone who
was called, is misleading. If most people did not answer a question, lead with that
rather than with the average.

## Say what a missing answer means

`form_data` shows `null` for three different things, and they are not the same story.
`form_status` tells them apart:

- `answered`: the person said it.
- `skipped`: the agent asked, could not get a usable answer, and moved on.
- `empty`: the call ended before this question came up.

Say it as: "Three people were asked their age. Two gave it, one could not be
understood after three tries. The other two calls ended before the question."

A lot of `skipped` on one question means the question is not working. A lot of
`empty` on the last few questions means calls are ending early. Those are different
problems, so do not report them as one number.

## The call statuses

- `complete`: the whole form was filled in.
- `screened_out`: the call ended early on purpose, for example the person said no to
  a consent question. Nothing went wrong.
- `failed`: the call ended with the form unfinished.
- `in_progress`: the call is still going, or ended so recently that it cannot be
  told apart from one still going.

Do not call `screened_out` a failure. Say "ended at the consent question, as
designed".

## Reading the numbers from the analytics

`GET /api/v1/agents/{agent_id}/analytics` returns a `stats` block:

```json
{"attempted":5,"completed":4,"screened_out":1,"completion_rate":0.8,
 "avg_duration_secs":59.0,"avg_duration_ci95":0.0,"duration_sample_count":5,
 "cost":{"call_count":0,"total":{"per_call":null}}}
```

`completed` includes `screened_out`, and so does `completion_rate`. In the numbers
above, four calls are counted as completed, and one of those four ended at the
consent question. If someone asks how many people finished the form, the answer is
three, not four. Subtract `screened_out` and say you did.

`since` and `until` narrow the window, in unix seconds.

## No calls is not a score of zero

A window with no calls in it comes back with `attempted` 0, `completion_rate` 0 and
every average `null`. That is not a bad result, it is no result. Say "no calls in
that period", never "0%".

## Small numbers move on their own

Each average comes with a `_ci95` beside it and a `_sample_count`. Read the average
as a range: from the average minus the `_ci95` to the average plus the `_ci95`. The
true average is very likely somewhere in that range.

To compare two periods, write down both ranges. If they overlap at all, you cannot
say they differ. If they do not overlap, the difference is real.

Worked example. Before: average 59 seconds, `ci95` 8, so 51 to 67. After: average 52
seconds, `ci95` 9, so 43 to 61. Those overlap between 51 and 61, so calls did not get
measurably shorter. The ranges shrink as `sample_count` grows.

Two things to watch:

- `ci95` is `null` when `sample_count` is under 2. There is no range then and no
  comparison to make. Say so, do not report the average as if it means something.
- `completion_rate` comes with no `ci95`. Judge it by hand: with `n` calls the wobble
  is roughly 1 divided by the square root of `n`. At 10 calls that is about 30
  points, so 70% against 80% is nothing. At 100 calls it is about 10 points. Under
  roughly 30 calls on each side, treat any change in the completion rate as noise.

## Say what you did not check

If you only pulled 200 calls and there were more, say so. If you filtered to one
agent, say which. If `created_at` mattered to the question, say that it is the time
the answers were last written, not when the call started, so a corrected answer
looks like a recent call.
