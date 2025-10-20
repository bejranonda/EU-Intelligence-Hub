"""Tests for database connection and models."""
import pytest
from sqlalchemy.orm import Session

from app.models.models import (
    Keyword, Article, KeywordArticle, KeywordRelation,
    KeywordSuggestion, Document, SentimentTrend, ComparativeSentiment
)


def test_database_connection(db_session: Session):
    """Test that database connection works."""
    result = db_session.execute("SELECT 1")
    assert result.scalar() == 1


def test_create_keyword(db_session: Session):
    """Test creating a keyword in the database."""
    keyword = Keyword(
        keyword_en="Thailand",
        keyword_th="ประเทศไทย",
        category="Country",
        popularity_score=100.0
    )
    db_session.add(keyword)
    db_session.commit()
    db_session.refresh(keyword)

    assert keyword.id is not None
    assert keyword.keyword_en == "Thailand"
    assert keyword.keyword_th == "ประเทศไทย"
    assert keyword.category == "Country"
    assert keyword.popularity_score == 100.0


def test_create_article(db_session: Session):
    """Test creating an article with sentiment fields."""
    article = Article(
        title="Test Article",
        summary="This is a test article",
        full_text="Full text of test article",
        source_url="https://example.com/test",
        source="Test Source",
        classification="fact",
        sentiment_overall=0.75,
        sentiment_confidence=0.85,
        sentiment_subjectivity=0.3,
        emotion_positive=0.8,
        emotion_negative=0.1,
        emotion_neutral=0.1
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)

    assert article.id is not None
    assert article.title == "Test Article"
    assert article.sentiment_overall == 0.75
    assert article.sentiment_confidence == 0.85
    assert article.emotion_positive == 0.8


def test_keyword_article_relationship(db_session: Session):
    """Test many-to-many relationship between keywords and articles."""
    keyword = Keyword(name_en="Test Keyword")
    article = Article(
        title="Test Article",
        source_url="https://example.com/test"
    )
    db_session.add(keyword)
    db_session.add(article)
    db_session.commit()

    keyword_article = KeywordArticle(
        keyword_id=keyword.id,
        article_id=article.id,
        relevance_score=0.9
    )
    db_session.add(keyword_article)
    db_session.commit()

    # Query to verify relationship
    result = db_session.query(KeywordArticle).filter_by(
        keyword_id=keyword.id,
        article_id=article.id
    ).first()

    assert result is not None
    assert result.relevance_score == 0.9


def test_sentiment_trend_creation(db_session: Session):
    """Test creating sentiment trend record."""
    keyword = Keyword(keyword_en="Thailand")
    db_session.add(keyword)
    db_session.commit()

    from datetime import date
    sentiment_trend = SentimentTrend(
        keyword_id=keyword.id,
        date=date.today(),
        avg_sentiment=0.65,
        article_count=25,
        positive_count=18,
        negative_count=3,
        neutral_count=4,
        top_sources={"BBC": 0.8, "Reuters": 0.7}
    )
    db_session.add(sentiment_trend)
    db_session.commit()
    db_session.refresh(sentiment_trend)

    assert sentiment_trend.id is not None
    assert sentiment_trend.avg_sentiment == 0.65
    assert sentiment_trend.article_count == 25
    assert sentiment_trend.top_sources["BBC"] == 0.8


def test_keyword_suggestion_creation(db_session: Session):
    """Test creating keyword suggestion."""
    suggestion = KeywordSuggestion(
        keyword_en="Vietnam",
        reason="Suggested for geopolitical tracking",
        contact_email="user@example.com",
        status="pending"
    )
    db_session.add(suggestion)
    db_session.commit()
    db_session.refresh(suggestion)

    assert suggestion.id is not None
    assert suggestion.keyword_en == "Vietnam"
    assert suggestion.status == "pending"
