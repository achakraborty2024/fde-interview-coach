# Tasks: session progress endpoint

Each task is small and reviewable on its own. Verify before moving on.

- [x] **T1 — Data access.** Add `data.load_results() -> list[dict[str, Any]]`
  in `app/data.py`; make `save_result()` reuse it.
  *Verify:* mypy clean; existing tests still pass. (Criterion 4)

- [x] **T2 — Test isolation.** Add an autouse fixture in `tests/conftest.py` that
  points `data.DATA_DIR` at a temp folder with an empty `results.json`.
  *Verify:* after `pytest`, `data/results.json` is unchanged. (Criterion 5)

- [x] **T3 — Empty case.** Add `GET /progress` returning zeros when there are no
  results; test `test_progress_is_zero_when_nothing_scored`. (Criterion 1)

- [x] **T4 — Count and average.** Compute `rounds_practised` and a 1-decimal
  `average_total`; test `test_progress_counts_and_averages_scored_attempts`
  scores 2 answers via `/score` and checks both fields. (Criteria 2, 3)

- [x] **T5 — Quality gate.** Run `ruff check app tests`, `mypy app`, `pytest -q`.
  (Criterion 5)
