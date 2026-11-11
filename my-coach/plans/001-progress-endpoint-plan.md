# Plan 001 — GET /progress endpoint

**Goal:** add `GET /progress`, which reads `data/results.json` and returns how many
rounds have been practised and the average total score.

**Response shape:** `{"rounds_practised": <int>, "average_total": <float>}`

## 1. Files to change

| File | Change |
|---|---|
| `app/data.py` | Add `load_results() -> list[dict]` so all disk access stays in the data layer. |
| `app/main.py` | Add the `GET /progress` route: call `data.load_results()`, count the records, average their `total`. |
| `tests/test_score.py` | Add a test for `/progress` (see step 5). |

No new dependencies, no model changes.

## 2. Order

1. Add `data.load_results()`.
2. Add the `/progress` route using it.
3. Handle the empty case: when `results.json` holds `[]`, return
   `{"rounds_practised": 0, "average_total": 0}` — never divide by zero.
4. Round `average_total` to 1 decimal place.
5. Write one test: with no results, `/progress` returns zeros; after scoring N
   answers, `rounds_practised == N` and the average matches the recorded totals.
   The test must use a temporary results file so it never touches the real data.
6. Run `pytest -q`, then try it at `/docs`.

## 3. What could break

- **Division by zero** on an empty results file (handled in step 3).
- **Results only exist once `/score` saves them** — `/score` is still a stub, so
  `/progress` will read an empty list until Module 3 wires scoring up.
- **Tests writing to the real `data/results.json`** and leaking state between runs.
- A malformed record without a `total` key would raise a `KeyError`.

## 4. Riskiest assumption

That every record in `results.json` has a numeric `total` scored out of the same
maximum (20). If the rubric ever changes size, averaging raw totals becomes
misleading.
