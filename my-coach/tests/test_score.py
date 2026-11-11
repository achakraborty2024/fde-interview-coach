"""Scoring tests — written in Module 3.

The first test is the important one: against the START state's buggy
compute_total() it FAILS (the first category is dropped), which is how the bug
was discovered. Against the fixed version it passes.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app import data, scoring
from app.main import app
from app.models import CategoryScore

client = TestClient(app)


def test_compute_total_sums_every_category() -> None:
    """4 categories x 3 points = 12. The buggy version returns 9."""
    cats = [CategoryScore(name=n, score=3, feedback="") for n in scoring.RUBRIC_CATEGORIES]
    assert scoring.compute_total(cats) == 12


def test_compute_total_includes_the_first_category() -> None:
    """Isolates the cause: only the first category scores, so the total must be 5."""
    cats = [CategoryScore(name=n, score=0, feedback="") for n in scoring.RUBRIC_CATEGORIES]
    cats[0].score = 5
    assert scoring.compute_total(cats) == 5


def test_summary_bands_match_original_behaviour() -> None:
    """Refactor guard: the band boundaries must match the old if/else exactly."""
    expected = {
        0: "Needs significant work", 4: "Needs significant work",
        5: "Needs work", 9: "Needs work",
        10: "Solid, with gaps", 15: "Solid, with gaps",
        16: "Strong answer", 19: "Strong answer",
        20: "Strong answer - full marks",
    }
    for total, summary in expected.items():
        assert scoring.summary_for(total) == summary


def test_score_endpoint_total_equals_sum_of_categories() -> None:
    """The headline invariant: the total must equal the sum of its parts."""
    resp = client.post(
        "/score",
        json={"round": "decomposition", "question_id": "dec-01", "answer": "line\n" * 6},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == sum(c["score"] for c in body["categories"])
    assert body["max"] == 20


def test_scores_stay_within_bounds() -> None:
    """Every category score must sit inside the rubric's 0..5 range."""
    resp = client.post(
        "/score",
        json={"round": "behavioral", "question_id": "beh-01", "answer": "short"},
    )
    for category in resp.json()["categories"]:
        assert 0 <= category["score"] <= 5


def test_progress_is_zero_when_nothing_scored() -> None:
    """Empty results.json must not divide by zero."""
    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {"rounds_practised": 0, "average_total": 0}


def test_progress_counts_and_averages_scored_attempts() -> None:
    """After N scored answers, /progress reports N and the mean total."""
    totals = []
    for answer in ("short", "line\n" * 6):
        resp = client.post(
            "/score", json={"round": "decomposition", "question_id": "dec-01", "answer": answer}
        )
        totals.append(resp.json()["total"])
    body = client.get("/progress").json()
    assert body["rounds_practised"] == 2
    assert body["average_total"] == round(sum(totals) / 2, 1)


def test_score_records_per_category_scores() -> None:
    """Each saved attempt keeps its category scores (used by /report)."""
    client.post("/score", json={"round": "behavioral", "question_id": "beh-01", "answer": "x"})
    record = data.load_results()[-1]
    assert set(record["categories"]) == set(scoring.RUBRIC_CATEGORIES)
