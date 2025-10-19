import datetime as dt

import pytest

from app.config import get_settings
from app.models.models import Keyword, KeywordSuggestion
from app.services.keyword_approval import keyword_approval_service


@pytest.fixture(autouse=True)
def mock_translations(monkeypatch):
    async def _fake_translate(keyword_en: str, target_languages=None):
        base = keyword_en.upper()
        return {
            "th": f"TH-{base}",
            "de": f"DE-{base}",
            "fr": f"FR-{base}",
            "es": f"ES-{base}",
            "it": f"IT-{base}",
            "pl": f"PL-{base}",
            "sv": f"SV-{base}",
            "nl": f"NL-{base}",
        }

    monkeypatch.setattr(keyword_approval_service, "translate_keyword", _fake_translate)

    yield

    monkeypatch.undo()


def test_keyword_creation_populates_translations(db_session):
    suggestion = KeywordSuggestion(
        keyword_en="energy security",
        category="policy",
        status="pending",
    )
    db_session.add(suggestion)
    db_session.commit()
    db_session.refresh(suggestion)

    keyword = Keyword(
        keyword_en=suggestion.keyword_en,
        category=suggestion.category,
    )
    db_session.add(keyword)
    db_session.commit()
    db_session.refresh(keyword)

    assert keyword.keyword_de is None

    translations = asyncio_run(keyword_approval_service.translate_keyword(suggestion.keyword_en))
    for lang_code, expected in translations.items():
        assert expected.startswith(lang_code.upper())


def asyncio_run(coro):
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        return asyncio.ensure_future(coro)
    return loop.run_until_complete(coro)
