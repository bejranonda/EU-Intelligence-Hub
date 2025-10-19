from app.models.models import NewsSource, SourceIngestionHistory


def test_news_source_defaults():
    source = NewsSource(
        name="Test Source",
        base_url="https://example.com",
        parser="generic",
    )

    assert source.enabled is True
    assert source.language == "en"
    assert source.priority == 0


def test_source_ingestion_history_relationship():
    history = SourceIngestionHistory(
        source=NewsSource(name="Another", base_url="https://another.example"),
        articles_ingested=12,
        success=False,
        notes="Timeout",
    )

    assert history.source.name == "Another"
    assert history.articles_ingested == 12
