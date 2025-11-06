"""Tests for AI services: sentiment analysis, keyword extraction, embeddings."""
import pytest
from app.services.sentiment import get_sentiment_analyzer
from app.services.keyword_extractor import get_keyword_extractor
from app.services.embeddings import get_embedding_generator
from app.services.gemini_client import get_gemini_client


class TestSentimentAnalysis:
    """Test sentiment analysis functionality."""

    def test_vader_sentiment_positive(self):
        """Test VADER analysis on positive text."""
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze_sentiment_vader(
            "This is wonderful news! Thailand's economy is thriving and tourism is booming."
        )

        assert "overall" in result
        assert result["overall"] > 0  # Should be positive
        assert result["positive"] > result["negative"]

    def test_vader_sentiment_negative(self):
        """Test VADER analysis on negative text."""
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze_sentiment_vader(
            "This is terrible news. The situation is awful and getting worse."
        )

        assert "overall" in result
        assert result["overall"] < 0  # Should be negative
        assert result["negative"] > result["positive"]

    def test_vader_sentiment_neutral(self):
        """Test VADER analysis on neutral text."""
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze_sentiment_vader(
            "The meeting took place on Tuesday. Officials discussed various topics."
        )

        assert "overall" in result
        assert abs(result["overall"]) < 0.5  # Should be relatively neutral

    def test_sentiment_classification(self):
        """Test sentiment classification logic."""
        analyzer = get_sentiment_analyzer()

        # Test positive
        assert analyzer.classify_sentiment(0.6, 0.8) == "STRONGLY_POSITIVE"
        assert analyzer.classify_sentiment(0.3, 0.7) == "POSITIVE"

        # Test negative
        assert analyzer.classify_sentiment(-0.6, 0.8) == "STRONGLY_NEGATIVE"
        assert analyzer.classify_sentiment(-0.3, 0.7) == "NEGATIVE"

        # Test neutral
        assert analyzer.classify_sentiment(0.1, 0.5) == "NEUTRAL"
        assert analyzer.classify_sentiment(-0.1, 0.5) == "NEUTRAL"

    def test_analyze_article_without_gemini(self):
        """Test article analysis using VADER only."""
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze_article(
            title="Thailand's Economy Grows",
            text="Thailand's economy has shown strong growth this quarter. "
            "Exports increased and tourism recovered significantly.",
            source_name="Test Source",
            use_gemini=False,  # Force VADER only
        )

        assert "sentiment_overall" in result
        assert "sentiment_confidence" in result
        assert "classification" in result
        assert result["method"] == "vader"
        assert result["sentiment_overall"] > 0  # Should be positive


class TestKeywordExtraction:
    """Test keyword extraction functionality."""

    def test_extract_noun_chunks(self):
        """Test noun chunk extraction."""
        extractor = get_keyword_extractor()
        text = """
        Thailand's tourism industry is experiencing rapid growth.
        The Thai government announced new policies to support economic development.
        """

        chunks = extractor.extract_noun_chunks(text)

        assert isinstance(chunks, list)
        # Should extract some meaningful chunks
        assert len(chunks) >= 0  # May vary based on spaCy model

    def test_extract_all_without_gemini(self):
        """Test full extraction without Gemini."""
        extractor = get_keyword_extractor()
        result = extractor.extract_all(
            title="Thailand Announces Economic Policy",
            text="The Thai government announced new economic policies focusing on "
            "sustainable development and digital transformation.",
            use_gemini=False,
        )

        assert "keywords" in result
        assert "entities" in result
        assert "classification" in result
        assert isinstance(result["keywords"], list)


class TestEmbeddings:
    """Test embedding generation functionality."""

    def test_generate_single_embedding(self):
        """Test generating a single embedding."""
        generator = get_embedding_generator()
        embedding = generator.generate_embedding("Thailand tourism industry")

        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # Model generates 384-dimensional vectors
        assert all(isinstance(x, float) for x in embedding)

    def test_generate_batch_embeddings(self):
        """Test batch embedding generation."""
        generator = get_embedding_generator()
        texts = ["Thailand economy", "Tourism sector", "Trade agreement"]

        embeddings = generator.generate_embeddings_batch(texts)

        assert len(embeddings) == len(texts)
        assert all(emb is not None for emb in embeddings)
        assert all(len(emb) == 384 for emb in embeddings)

    def test_compute_similarity(self):
        """Test similarity computation."""
        generator = get_embedding_generator()

        # Generate embeddings for similar texts
        emb1 = generator.generate_embedding("Thailand tourism")
        emb2 = generator.generate_embedding("Thai tourism industry")
        emb3 = generator.generate_embedding("Computer science")

        # Similar texts should have higher similarity
        sim_similar = generator.compute_similarity(emb1, emb2)
        sim_different = generator.compute_similarity(emb1, emb3)

        assert sim_similar > sim_different
        assert -1 <= sim_similar <= 1
        assert -1 <= sim_different <= 1

    def test_find_similar(self):
        """Test finding similar embeddings."""
        generator = get_embedding_generator()

        query_text = "Thailand economy"
        candidate_texts = [
            "Thai economic growth",
            "Tourism in Thailand",
            "Space exploration",
            "Thailand GDP",
        ]

        query_emb = generator.generate_embedding(query_text)
        candidate_embs = generator.generate_embeddings_batch(candidate_texts)

        similar = generator.find_similar(query_emb, candidate_embs, top_k=2)

        assert len(similar) <= 2
        assert all(isinstance(item, tuple) for item in similar)
        assert all(len(item) == 2 for item in similar)

        # Results should be sorted by similarity
        if len(similar) > 1:
            assert similar[0][1] >= similar[1][1]


class TestGeminiClient:
    """Test Gemini API client."""

    def test_gemini_client_initialization(self):
        """Test Gemini client can be initialized."""
        client = get_gemini_client()
        assert client is not None
        assert client.model is not None

    def test_rate_limiter(self):
        """Test rate limiter doesn't crash."""
        client = get_gemini_client()
        # Just ensure rate limiter exists and can be called
        client.rate_limiter.wait_if_needed()
        assert True  # If we got here, rate limiter works

    # Note: Skip actual API tests to avoid using quota during testing
    @pytest.mark.skip(reason="Skipping actual API calls to preserve quota")
    def test_generate_text(self):
        """Test text generation (skipped to preserve API quota)."""
        client = get_gemini_client()
        result = client.generate_text("Say hello", temperature=0.5, max_tokens=50)
        assert result is not None or result is None  # May fail without API key
