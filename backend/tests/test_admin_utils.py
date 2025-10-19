from types import SimpleNamespace
from datetime import datetime

import pytest

pytest.importorskip("fastapi")

from app.api.admin import _serialize_suggestion_with_evaluation


def _make_suggestion(**overrides):
    base = {
        "id": 1,
        "keyword_en": "green transition",
        "keyword_th": "",
        "keyword_de": "",
        "keyword_fr": "",
        "keyword_es": "",
        "keyword_it": "",
        "keyword_pl": "",
        "keyword_sv": "",
        "keyword_nl": "",
        "category": "energy",
        "reason": "EU policy focus",
        "votes": 7,
        "status": "pending",
        "created_at": datetime(2025, 1, 1, 12, 0, 0),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _make_evaluation(**overrides):
    base = {
        "searchability_score": 8,
        "significance_score": 7,
        "specificity": "just_right",
        "decision": "approved",
        "reasoning": "High relevance to EU initiatives",
        "created_at": datetime(2025, 1, 1, 13, 0, 0),
        "evaluation_metadata": {"model": "gemini-pro"},
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_serialize_suggestion_with_evaluation_includes_scores():
    suggestion = _make_suggestion()
    evaluation = _make_evaluation()

    payload = _serialize_suggestion_with_evaluation(suggestion, evaluation)

    assert payload["id"] == suggestion.id
    assert payload["latest_evaluation"]["decision"] == "approved"
    assert payload["latest_evaluation"]["metadata"] == {"model": "gemini-pro"}


def test_serialize_suggestion_without_evaluation_sets_none():
    suggestion = _make_suggestion()

    payload = _serialize_suggestion_with_evaluation(suggestion, None)

    assert payload["latest_evaluation"] is None
