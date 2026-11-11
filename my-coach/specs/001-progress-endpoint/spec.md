# Spec: session progress endpoint

## Why
A learner practising mock rounds needs a quick answer to "am I improving?"
without opening `data/results.json` by hand.

## What
`GET /progress` reports, across every scored attempt:
- `rounds_practised` — how many answers have been scored (int)
- `average_total` — mean total out of 20, rounded to 1 decimal

## Reads
`data/results.json`, through `data.load_results()` — routes never open files directly.

## Acceptance criteria
1. No results yet -> `{"rounds_practised": 0, "average_total": 0}` (no divide-by-zero).
2. After N scored answers, `rounds_practised == N`.
3. `average_total` equals the mean of the recorded totals, to 1 decimal.
4. Reads `data/results.json` only. No new dependencies.
5. ruff + mypy clean; pytest green; tests never touch the real `data/results.json`.

## Out of scope
- Per-round or per-category breakdowns (the `/report` command covers the weakest category).
- Trends over time, filtering by date, or resetting progress.
- Authentication or multiple users.
