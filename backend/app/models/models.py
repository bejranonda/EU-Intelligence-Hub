"""SQLAlchemy database models."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.db.types import ArrayType, JSONBType, VectorType


class Keyword(Base):
    """Keyword model with semantic search support."""

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword_en = Column(String(255), unique=True, nullable=False, index=True)
    keyword_th = Column(String(255))
    keyword_de = Column(String(255))
    keyword_da = Column(String(255))  # Danish
    keyword_fr = Column(String(255))
    keyword_es = Column(String(255))
    keyword_it = Column(String(255))
    keyword_pl = Column(String(255))
    keyword_sv = Column(String(255))
    keyword_nl = Column(String(255))
    category = Column(String(100))
    popularity_score = Column(Float, default=0.0)
    search_count = Column(Integer, default=0)
    last_searched = Column(
        DateTime, nullable=True
    )  # Track when keyword was last searched for news
    next_search_after = Column(DateTime, nullable=True)
    search_priority = Column(Integer, default=0)
    embedding = Column(VectorType(384))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    articles = relationship(
        "KeywordArticle", back_populates="keyword", cascade="all, delete-orphan"
    )
    sentiment_trends = relationship(
        "SentimentTrend", back_populates="keyword", cascade="all, delete-orphan"
    )
    evaluations = relationship(
        "KeywordEvaluation", back_populates="keyword", cascade="all, delete-orphan"
    )
    queued_searches = relationship(
        "KeywordSearchQueue", back_populates="keyword", cascade="all, delete-orphan"
    )


class Article(Base):
    """Article model with full sentiment tracking."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    full_text = Column(Text)
    source_url = Column(Text, unique=True, nullable=False, index=True)
    source = Column(String(255), index=True)
    published_date = Column(DateTime, index=True)
    scraped_date = Column(DateTime, default=func.now())
    language = Column(String(10))
    classification = Column(
        String(20), CheckConstraint("classification IN ('fact', 'opinion', 'mixed')")
    )
    sentiment_classification = Column(
        String(20)
    )  # Added field for sentiment classification
    credibility_score = Column(Float, default=0.5)
    embedding = Column(VectorType(384))

    # Sentiment fields
    sentiment_overall = Column(Float)  # -1.0 to 1.0
    sentiment_confidence = Column(Float)  # 0.0 to 1.0
    sentiment_subjectivity = Column(Float)  # 0.0 to 1.0
    emotion_positive = Column(Float)  # 0.0 to 1.0
    emotion_negative = Column(Float)  # 0.0 to 1.0
    emotion_neutral = Column(Float)  # 0.0 to 1.0

    # Relationships
    keywords = relationship(
        "KeywordArticle", back_populates="article", cascade="all, delete-orphan"
    )

    # Indexes defined in __table_args__
    __table_args__ = (
        Index("idx_articles_sentiment", "sentiment_overall"),
        Index(
            "idx_articles_published_date_desc",
            "published_date",
            postgresql_using="btree",
        ),
    )


class KeywordArticle(Base):
    """Junction table for keywords and articles with relevance scoring."""

    __tablename__ = "keyword_articles"

    keyword_id = Column(
        Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True
    )
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    relevance_score = Column(Float)

    # Relationships
    keyword = relationship("Keyword", back_populates="articles")
    article = relationship("Article", back_populates="keywords")


class KeywordRelation(Base):
    """Keyword relationships for mind map visualization."""

    __tablename__ = "keyword_relations"

    keyword1_id = Column(
        Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True
    )
    keyword2_id = Column(
        Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True
    )
    relation_type = Column(String(50))  # 'related', 'parent', 'child', 'causal'
    strength_score = Column(Float)
    evidence_count = Column(Integer, default=0)


class KeywordSuggestion(Base):
    """User-submitted keyword suggestions."""

    __tablename__ = "keyword_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    keyword_en = Column(String(255), nullable=False, index=True)
    keyword_th = Column(String(255))
    keyword_de = Column(String(255))
    keyword_fr = Column(String(255))
    keyword_es = Column(String(255))
    keyword_it = Column(String(255))
    keyword_pl = Column(String(255))
    keyword_sv = Column(String(255))
    keyword_nl = Column(String(255))
    category = Column(String(100), default="general")
    reason = Column(Text)
    contact_email = Column(String(100))
    status = Column(String(20), default="pending")  # 'pending', 'approved', 'rejected'
    votes = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    evaluations = relationship(
        "KeywordEvaluation", back_populates="suggestion", cascade="all, delete-orphan"
    )


class Document(Base):
    """Manually uploaded documents."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    upload_date = Column(DateTime, default=func.now())
    extracted_text = Column(Text)
    source_type = Column(String(50))
    doc_metadata = Column(
        "metadata", JSONBType()
    )  # renamed to avoid SQLAlchemy reserved word


class SentimentTrend(Base):
    """Daily sentiment trends aggregation."""

    __tablename__ = "sentiment_trends"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(
        Integer, ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    avg_sentiment = Column(Float)
    article_count = Column(Integer)
    positive_count = Column(Integer)
    negative_count = Column(Integer)
    neutral_count = Column(Integer)
    top_sources = Column(JSONBType())  # Which sources were most positive/negative

    # Relationships
    keyword = relationship("Keyword", back_populates="sentiment_trends")

    # Unique constraint and indexes
    __table_args__ = (
        UniqueConstraint("keyword_id", "date", name="uq_keyword_date"),
        Index("idx_sentiment_trends_date", "date", postgresql_using="btree"),
        Index(
            "idx_sentiment_trends_keyword_date",
            "keyword_id",
            "date",
            postgresql_using="btree",
        ),
    )


class ComparativeSentiment(Base):
    """Comparative sentiment analysis between keywords."""

    __tablename__ = "comparative_sentiment"

    id = Column(Integer, primary_key=True, index=True)
    primary_keyword = Column(String(255))
    comparison_keyword = Column(String(255))
    date_range_start = Column(Date)
    date_range_end = Column(Date)
    primary_avg_sentiment = Column(Float)
    comparison_avg_sentiment = Column(Float)
    sentiment_gap = Column(Float)  # difference between the two
    article_count_primary = Column(Integer)
    article_count_comparison = Column(Integer)


class KeywordEvaluation(Base):
    """AI evaluation metadata for keyword suggestions and decisions."""

    __tablename__ = "keyword_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    suggestion_id = Column(
        Integer, ForeignKey("keyword_suggestions.id", ondelete="SET NULL"), index=True
    )
    keyword_id = Column(
        Integer, ForeignKey("keywords.id", ondelete="SET NULL"), index=True
    )
    keyword_text = Column(String(255), nullable=False)
    searchability_score = Column(Integer)
    significance_score = Column(Integer)
    specificity = Column(String(50))
    decision = Column(String(20))  # approved, pending, merged, rejected
    reasoning = Column(Text)
    evaluation_metadata = Column(JSONBType(), default=dict)
    created_at = Column(DateTime, default=func.now())

    suggestion = relationship("KeywordSuggestion", back_populates="evaluations")
    keyword = relationship("Keyword", back_populates="evaluations")


class NewsSource(Base):
    """Configurable news source metadata."""

    __tablename__ = "news_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    base_url = Column(String(512), nullable=False)
    enabled = Column(Boolean, default=True)
    language = Column(String(10), default="en")
    country = Column(String(100), nullable=True)
    priority = Column(Integer, default=0)
    parser = Column(String(100), nullable=True)
    tags = Column(ArrayType())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    ingestion_records = relationship(
        "SourceIngestionHistory",
        back_populates="source",
        cascade="all, delete-orphan",
    )


class KeywordSearchQueue(Base):
    """Scheduled keyword search jobs awaiting processing."""

    __tablename__ = "keyword_search_queue"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(
        Integer,
        ForeignKey("keywords.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_at = Column(DateTime, nullable=False, index=True)
    priority = Column(Integer, default=0, index=True)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    status = Column(
        String(20), default="pending"
    )  # pending, running, completed, failed, skipped
    last_attempt_at = Column(DateTime, nullable=True)
    error = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    keyword = relationship("Keyword", back_populates="queued_searches")


class SourceIngestionHistory(Base):
    """Track ingestion activity for each source."""

    __tablename__ = "source_ingestion_history"

    id = Column(Integer, primary_key=True)
    source_id = Column(
        Integer, ForeignKey("news_sources.id", ondelete="CASCADE"), nullable=False
    )
    last_run_at = Column(DateTime, default=func.now())
    articles_ingested = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    notes = Column(Text)

    source = relationship("NewsSource", back_populates="ingestion_records")
