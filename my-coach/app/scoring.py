"""Scoring logic: turn a candidate's answer into a rubric-based scorecard.

Module 3 changes:
  * score_with_openai() -> implemented against the OpenAI API (mock fallback)
  * compute_total()     -> counts ALL categories (the seeded bug is fixed)
  * format_scorecard()  -> flattened; summary bands now live in SUMMARY_BANDS
"""
from __future__ import annotations

import json

from .config import MODEL_ID, OPENAI_API_KEY, USE_MOCK
from .data import load_rubric
from .models import CategoryScore, ScoreResponse

# The four things every answer is scored on (mirrors data/rubric.md).
RUBRIC_CATEGORIES = [
    "Clarifying questions",
    "Decomposition",
    "Risk identification",
    "Communication",
]

# The scoring prompt lives here as ONE named constant, never inline in the code.
# It must mention JSON because we ask OpenAI for a JSON-only response.
SCORING_PROMPT = """You are a senior Forward Deployed Engineer scoring a candidate's \
interview answer against a rubric. Score each of the four categories from 0 to 5 \
and give one short line of feedback for each.

Reply with JSON only, in exactly this shape:
{{"categories": [{{"name": "...", "score": 0, "feedback": "..."}}]}}

Rubric:
{rubric}

Candidate's answer:
{answer}
"""

# Summary bands, highest threshold first. Replaces the old nested if/else.
SUMMARY_BANDS: list[tuple[int, str]] = [
    (20, "Strong answer - full marks"),
    (16, "Strong answer"),
    (10, "Solid, with gaps"),
    (5, "Needs work"),
    (0, "Needs significant work"),
]


def score_mock(answer: str) -> list[CategoryScore]:
    """A tiny deterministic scorer used when there is no OpenAI key.

    Intentionally simple: longer, more structured answers score a little higher.
    The workshop is about the *workflow*, not about building a clever scorer.
    """
    length_signal = min(len(answer) // 120, 5)  # 0..5 by answer length
    structure_signal = min(answer.count("\n") + 1, 5)  # 0..5 by line breaks
    base = max(1, (length_signal + structure_signal) // 2)
    return [
        CategoryScore(name=name, score=base, feedback=f"Auto-estimate for '{name}'.")
        for name in RUBRIC_CATEGORIES
    ]


def compute_total(categories: list[CategoryScore]) -> int:
    """Sum the per-category scores into a single total (every category counts)."""
    return sum(category.score for category in categories)


def summary_for(total: int) -> str:
    """Map a total score to its one-line summary, using the bands table."""
    for threshold, label in SUMMARY_BANDS:
        if total >= threshold:
            return label
    return SUMMARY_BANDS[-1][1]


def format_scorecard(categories: list[CategoryScore]) -> ScoreResponse:
    """Assemble the final ScoreResponse from the category scores."""
    total = compute_total(categories)
    maximum = sum(category.max for category in categories)
    return ScoreResponse(
        total=total, max=maximum, categories=categories, summary=summary_for(total)
    )


def score_with_openai(answer: str) -> list[CategoryScore]:
    """Score using the real OpenAI API, falling back to the mock on any error."""
    try:
        # Imported lazily so the app still starts if the package isn't installed.
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=MODEL_ID,
            response_format={"type": "json_object"},  # forces valid JSON back
            messages=[
                {
                    "role": "user",
                    "content": SCORING_PROMPT.format(rubric=load_rubric(), answer=answer),
                }
            ],
        )
        payload = json.loads(completion.choices[0].message.content or "{}")
        return [CategoryScore(**item) for item in payload["categories"]]
    except Exception:
        # A scoring hiccup should never take the app down — fall back to the mock.
        return score_mock(answer)


def score_answer(answer: str) -> ScoreResponse:
    """Score one answer end to end (mock offline, OpenAI when a key is set)."""
    categories = score_with_openai(answer) if not USE_MOCK else score_mock(answer)
    return format_scorecard(categories)
