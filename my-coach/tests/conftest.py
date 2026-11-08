"""Shared pytest fixtures.

Every test gets its own empty results.json in a temp folder, so tests never
write to the real data/results.json and never leak state into each other.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app import data
from app.config import DATA_DIR


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the data layer at a temp copy of data/ with an empty results file."""
    for name in ("questions.json", "rubric.md"):
        shutil.copy(DATA_DIR / name, tmp_path / name)
    (tmp_path / "results.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    return tmp_path
