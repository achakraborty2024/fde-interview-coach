"""FastAPI app for the FDE Interview Prep Assistant.

Run it:
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs  -- the interactive API page is our "UI".
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from . import data, scoring
from .models import Question, ScoreRequest, ScoreResponse

app = FastAPI(title="FDE Interview Prep Assistant")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.get("/rounds")
def get_rounds() -> list[str]:
    """List the available interview round types."""
    return data.load_rounds()


@app.get("/questions")
def get_questions(round: str) -> list[Question]:
    """Return the questions for one round, e.g. /questions?round=decomposition."""
    questions = data.load_questions(round=round)
    if not questions:
        raise HTTPException(status_code=404, detail=f"No questions for round '{round}'")
    return questions


@app.post("/score")
def post_score(request: ScoreRequest) -> ScoreResponse:
    """Score a candidate's answer against the rubric, and record the attempt."""
    result = scoring.score_answer(request.answer)
    data.save_result(
        {
            "round": request.round,
            "question_id": request.question_id,
            "total": result.total,
            "max": result.max,
            # Per-category scores, so /report can find the weakest category.
            "categories": {c.name: c.score for c in result.categories},
        }
    )
    return result


@app.get("/progress")
def get_progress() -> dict[str, float | int]:
    """Session stats: how many rounds practised, and the average total score."""
    results = data.load_results()
    count = len(results)
    average = round(sum(r["total"] for r in results) / count, 1) if count else 0
    return {"rounds_practised": count, "average_total": average}
