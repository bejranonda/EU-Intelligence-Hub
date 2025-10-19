

def _build_settings_override():
    from app.config import Settings

    dummy_env = {name.upper(): "placeholder" for name in Settings.model_fields}
    return Settings(**dummy_env)

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.keyword_approval import KeywordApprovalService


def test_process_suggestion_pending_review(monkeypatch):
    """Service should queue suggestion for manual review on low scores."""

    from app.config import get_settings

    monkeypatch.setattr("app.config.get_settings", lambda: _build_settings_override())

    service = KeywordApprovalService()

    suggestion = SimpleNamespace(
        id=1,
        keyword_en="European Defence Fund",
        category="defence",
        reason="Monitor EU defence budget",
        status="pending",
        keyword_th=None,
        keyword_de=None,
        keyword_fr=None,
        keyword_es=None,
        keyword_it=None,
        keyword_pl=None,
        keyword_sv=None,
        keyword_nl=None,
    )

    query = MagicMock()
    query.filter.return_value.first.return_value = suggestion

    session = MagicMock()
    session.execute.return_value.fetchall.return_value = []
    session.query.return_value = query

    async def fake_evaluation(*_args, **_kwargs):
        return {
            "searchability_score": 5,
            "significance_score": 4,
            "specificity": "broad",
            "reasoning": "Insufficient relevance",
            "suggested_alternatives": [],
            "notes": "",
            "raw": {},
        }

    async def fake_attempt_merge(*_args, **_kwargs):
        return None

    recorded = {}

    def fake_record_evaluation(*_args, **kwargs):
        recorded["decision"] = kwargs.get("decision")
        recorded["evaluation"] = kwargs.get("evaluation")

    monkeypatch.setattr(service, "evaluate_keyword_significance", fake_evaluation)
    monkeypatch.setattr(service, "_attempt_merge", fake_attempt_merge)
    monkeypatch.setattr(service, "_record_evaluation", fake_record_evaluation)
    monkeypatch.setattr(service, "_trigger_immediate_search", lambda *_: None)

    result = asyncio.run(service.process_suggestion(suggestion.id, session))

    assert result["action"] == "pending_review"
    assert "queued for manual review" in result["reasoning"][0]
    assert suggestion.status == "pending_review"
    assert recorded["decision"] == "pending_review"
    assert recorded["evaluation"]["significance_score"] == 4
