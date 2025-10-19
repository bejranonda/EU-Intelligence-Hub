from types import SimpleNamespace
from datetime import datetime

import pytest

from app.api.search import _resolve_article_sort, _serialize_article_payload


def test_resolve_article_sort_relevance_prefers_title_matches():
    clause = _resolve_article_sort("relevance", "Thailand")
    assert len(clause) == 2


def test_serialize_article_payload_includes_keywords():
    article = SimpleNamespace(
        id=3,
        title="Climate policy",
        summary="Summary",
        source="Reuters",
        source_url="https://reuters.com/article",
        published_date=datetime(2025, 1, 1, 12, 0, 0),
        sentiment_overall=0.4,
        sentiment_classification="positive",
        language="en",
    )

    payload = _serialize_article_payload(article, ["climate"], similarity=0.92)

    assert payload["keywords"] == ["climate"]
    assert payload["similarity_score"] == pytest.approx(0.92, rel=1e-3)

