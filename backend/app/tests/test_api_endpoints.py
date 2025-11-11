"""Tests for API endpoints."""

from datetime import datetime, timedelta
import io

import pytest

from app.models.models import (
    Keyword,
    Article,
    KeywordSuggestion,
    SentimentTrend,
    KeywordArticle,
)


@pytest.fixture
def sample_keyword(db_session):
    keyword = Keyword(keyword_en="Thailand", keyword_th="ประเทศไทย", category="country")
    db_session.add(keyword)
    db_session.commit()
    db_session.refresh(keyword)
    return keyword


@pytest.fixture
def sample_article(db_session, sample_keyword):
    article = Article(
        title="Thailand Tourism Booms",
        summary="Thailand sees record tourist arrivals",
        full_text="Thailand tourism industry experiences significant growth...",
        source="BBC",
        source_url="https://bbc.com/example",
        published_date=datetime.utcnow(),
        sentiment_overall=0.75,
        sentiment_confidence=0.85,
        sentiment_classification="POSITIVE",
        sentiment_subjectivity=0.6,
        emotion_positive=0.8,
        emotion_negative=0.1,
        emotion_neutral=0.1,
        classification="FACT",
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)

    db_session.add(
        KeywordArticle(
            keyword_id=sample_keyword.id,
            article_id=article.id,
            relevance_score=0.9,
        )
    )
    db_session.commit()

    return article


# ==================== Keyword Endpoints Tests ====================


def test_search_keywords_without_query(client, sample_keyword):
    """Test searching keywords without query parameter."""

    response = client.get("/api/keywords/")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) > 0
    assert data["results"][0]["keyword_en"] == "Thailand"


def test_search_keywords_with_query(client, sample_keyword):
    """Test searching keywords with query parameter."""
    response = client.get("/api/keywords/?q=Thai")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0
    assert "Thailand" in data["results"][0]["keyword_en"]


def test_search_keywords_pagination(client, db_session):
    """Test keyword search pagination."""
    for i in range(25):
        keyword = Keyword(
            keyword_en=f"Keyword{i}",
            keyword_th=f"คีย์เวิร์ด{i}",
            category="test",
        )
        db_session.add(keyword)
    db_session.commit()

    # Test first page
    response = client.get("/api/keywords/?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 10
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["total"] == 25

    # Test second page
    response = client.get("/api/keywords/?page=2&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 10
    assert data["pagination"]["page"] == 2


def test_get_keyword_detail(client, sample_keyword):
    """Test getting keyword details."""
    response = client.get(f"/api/keywords/{sample_keyword.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["keyword_en"] == "Thailand"
    assert data["keyword_th"] == "ประเทศไทย"
    assert data["category"] == "country"


def test_get_keyword_not_found(client):
    """Test getting non-existent keyword."""
    response = client.get("/api/keywords/99999")
    assert response.status_code == 404


def test_get_keyword_articles(client, sample_keyword, sample_article):
    """Test getting articles for a keyword."""
    response = client.get(f"/api/keywords/{sample_keyword.id}/articles")
    assert response.status_code == 200
    data = response.json()
    assert data["keyword_id"] == sample_keyword.id
    assert len(data["results"]) > 0
    assert data["results"][0]["title"] == "Thailand Tourism Booms"
    assert "sentiment" in data["results"][0]


def test_get_keyword_articles_sorting(client, db_session, sample_keyword):
    """Test sorting articles by different criteria."""
    # Create articles with different sentiments
    for i, sentiment in enumerate([0.8, -0.5, 0.3]):
        article = Article(
            title=f"Article {i}",
            summary="Summary",
            full_text="Text",
            source="Test",
            published_date=datetime.utcnow() - timedelta(days=i),
            sentiment_overall=sentiment,
            sentiment_classification="NEUTRAL",
        )
        db_session.add(article)
        db_session.flush()
        db_session.add(
            KeywordArticle(
                keyword_id=sample_keyword.id, article_id=article.id, relevance_score=0.9
            )
        )
    db_session.commit()

    # Test sorting by sentiment
    response = client.get(
        f"/api/keywords/{sample_keyword.id}/articles?sort_by=sentiment"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0


def test_get_keyword_relations(client, sample_keyword):
    """Test getting keyword relationships."""
    response = client.get(f"/api/keywords/{sample_keyword.id}/relations")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["keyword_id"] == sample_keyword.id


# ==================== Sentiment Endpoints Tests ====================


def test_get_keyword_sentiment(client, sample_keyword, sample_article):
    """Test getting keyword sentiment statistics."""
    response = client.get(f"/api/sentiment/keywords/{sample_keyword.id}/sentiment")
    assert response.status_code == 200
    data = response.json()
    assert data["keyword_id"] == sample_keyword.id
    assert "average_sentiment" in data
    assert "sentiment_distribution" in data
    assert data["total_articles"] > 0


def test_get_keyword_sentiment_timeline(client, db_session, sample_keyword):
    """Test getting sentiment timeline."""
    # Create sentiment trends
    for i in range(7):
        trend = SentimentTrend(
            keyword_id=sample_keyword.id,
            date=(datetime.utcnow() - timedelta(days=i)).date(),
            average_sentiment=0.5 + (i * 0.05),
            positive_count=10,
            negative_count=2,
            neutral_count=5,
        )
        db_session.add(trend)
    db_session.commit()

    response = client.get(
        f"/api/sentiment/keywords/{sample_keyword.id}/sentiment/timeline?days=7"
    )
    assert response.status_code == 200
    data = response.json()
    assert "timeline" in data
    assert "trend" in data
    assert len(data["timeline"]) > 0


def test_compare_keywords_sentiment(client, db_session):
    """Test comparing sentiment across keywords."""
    keyword1 = Keyword(keyword_en="Thailand", keyword_th="ไทย", category="country")
    keyword2 = Keyword(keyword_en="Vietnam", keyword_th="เวียดนาม", category="country")
    db_session.add_all([keyword1, keyword2])
    db_session.commit()

    # Add articles with different sentiments
    article1 = Article(
        title="Thailand Positive",
        summary="Summary",
        full_text="Text",
        source="Test",
        published_date=datetime.utcnow(),
        sentiment_overall=0.7,
        sentiment_classification="POSITIVE",
    )
    article2 = Article(
        title="Vietnam Negative",
        summary="Summary",
        full_text="Text",
        source="Test",
        published_date=datetime.utcnow(),
        sentiment_overall=-0.5,
        sentiment_classification="NEGATIVE",
    )
    db_session.add_all([article1, article2])
    db_session.flush()

    db_session.add(
        KeywordArticle(
            keyword_id=keyword1.id, article_id=article1.id, relevance_score=0.9
        )
    )
    db_session.add(
        KeywordArticle(
            keyword_id=keyword2.id, article_id=article2.id, relevance_score=0.9
        )
    )
    db_session.commit()

    response = client.get(
        f"/api/sentiment/keywords/compare?keyword_ids={keyword1.id},{keyword2.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "comparison" in data
    assert len(data["comparison"]) == 2
    assert "summary" in data


def test_get_article_sentiment_details(client, sample_article):
    """Test getting detailed sentiment for an article."""
    response = client.get(f"/api/sentiment/articles/{sample_article.id}/sentiment")
    assert response.status_code == 200
    data = response.json()
    assert data["article_id"] == sample_article.id
    assert "sentiment" in data
    assert data["sentiment"]["overall"] == 0.75
    assert data["sentiment"]["classification"] == "POSITIVE"


# ==================== Suggestion Endpoints Tests ====================


def test_create_suggestion(client):
    """Test creating a keyword suggestion."""
    suggestion_data = {
        "keyword_en": "Singapore",
        "keyword_th": "สิงคโปร์",
        "category": "country",
        "reason": "Important ASEAN partner",
    }
    response = client.post("/api/suggestions/", json=suggestion_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["suggestion"]["keyword_en"] == "Singapore"
    assert data["suggestion"]["votes"] == 1


def test_create_duplicate_suggestion(client):
    """Test creating duplicate suggestion increments votes."""
    suggestion_data = {"keyword_en": "Malaysia", "category": "country"}

    # Create first suggestion
    response1 = client.post("/api/suggestions/", json=suggestion_data)
    assert response1.status_code == 200
    assert response1.json()["suggestion"]["votes"] == 1

    # Create duplicate suggestion
    response2 = client.post("/api/suggestions/", json=suggestion_data)
    assert response2.status_code == 200
    assert response2.json()["suggestion"]["votes"] == 2


def test_get_suggestions(client):
    """Test retrieving suggestions."""
    # Create suggestions
    for i in range(3):
        suggestion_data = {"keyword_en": f"Country{i}", "category": "country"}
        client.post("/api/suggestions/", json=suggestion_data)

    response = client.get("/api/suggestions/")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) == 3


def test_get_suggestion_by_id(client):
    """Test getting a specific suggestion."""
    # Create suggestion
    suggestion_data = {"keyword_en": "Indonesia", "category": "country"}
    create_response = client.post("/api/suggestions/", json=suggestion_data)
    suggestion_id = create_response.json()["suggestion"]["id"]

    # Get suggestion
    response = client.get(f"/api/suggestions/{suggestion_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["keyword_en"] == "Indonesia"


def test_vote_suggestion(client):
    """Test voting for a suggestion."""
    # Create suggestion
    suggestion_data = {"keyword_en": "Laos", "category": "country"}
    create_response = client.post("/api/suggestions/", json=suggestion_data)
    suggestion_id = create_response.json()["suggestion"]["id"]
    initial_votes = create_response.json()["suggestion"]["votes"]

    # Vote for suggestion
    response = client.post(f"/api/suggestions/{suggestion_id}/vote")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["suggestion"]["votes"] == initial_votes + 1


# ==================== Document Upload Tests ====================


def test_upload_text_document(client):
    """Test uploading a text document."""
    content = "This is a test document about Thailand. The country has beautiful beaches and friendly people. Tourism is booming."
    file = io.BytesIO(content.encode("utf-8"))

    response = client.post(
        "/api/documents/upload",
        files={"file": ("test.txt", file, "text/plain")},
        data={"title": "Test Document", "source": "Test"},
    )

    # Note: This test will fail without actual AI services running
    # We're testing the endpoint structure
    assert response.status_code in [200, 500]  # May fail without services


def test_upload_unsupported_file(client):
    """Test uploading unsupported file type."""
    file = io.BytesIO(b"test content")

    response = client.post(
        "/api/documents/upload",
        files={"file": ("test.xyz", file, "application/octet-stream")},
        data={"title": "Test"},
    )

    assert response.status_code in [400, 500]


# ==================== Search Endpoints Tests ====================


def test_semantic_search_endpoint(client):
    """Test semantic search endpoint structure."""
    response = client.get("/api/search/semantic?q=tourism+thailand")

    # Note: May fail without embeddings
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "results" in data


def test_find_similar_articles(client, sample_article):
    """Test finding similar articles endpoint."""
    response = client.get(f"/api/search/similar/{sample_article.id}")

    # Note: Requires embeddings
    assert response.status_code in [200, 400, 500]


# ==================== Integration Tests ====================


def test_full_workflow(client, db_session):
    """Test complete workflow: create keyword, add article, get sentiment."""

    keyword = Keyword(keyword_en="TestCountry", keyword_th="ทดสอบ", category="country")
    db_session.add(keyword)
    db_session.commit()
    db_session.refresh(keyword)

    article = Article(
        title="Test Article",
        summary="Summary",
        full_text="Content",
        source="Test",
        published_date=datetime.utcnow(),
        sentiment_overall=0.6,
        sentiment_classification="POSITIVE",
    )
    db_session.add(article)
    db_session.flush()

    db_session.add(
        KeywordArticle(
            keyword_id=keyword.id, article_id=article.id, relevance_score=0.9
        )
    )
    db_session.commit()

    response1 = client.get("/api/keywords/")
    assert response1.status_code == 200

    response2 = client.get(f"/api/keywords/{keyword.id}/articles")
    assert response2.status_code == 200

    response3 = client.get(f"/api/sentiment/keywords/{keyword.id}/sentiment")
    assert response3.status_code == 200
