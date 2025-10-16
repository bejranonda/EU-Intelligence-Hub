"""SQLAlchemy database models."""
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Date, Boolean,
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base


class Keyword(Base):
    """Keyword model with semantic search support."""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword_en = Column(String(255), unique=True, nullable=False, index=True)
    keyword_th = Column(String(255))
    category = Column(String(100))
    popularity_score = Column(Float, default=0.0)
    search_count = Column(Integer, default=0)
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    articles = relationship("KeywordArticle", back_populates="keyword", cascade="all, delete-orphan")
    sentiment_trends = relationship("SentimentTrend", back_populates="keyword", cascade="all, delete-orphan")


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
        String(20),
        CheckConstraint("classification IN ('fact', 'opinion', 'mixed')")
    )
    sentiment_classification = Column(String(20))  # Added field for sentiment classification
    credibility_score = Column(Float, default=0.5)
    embedding = Column(Vector(384))

    # Sentiment fields
    sentiment_overall = Column(Float)  # -1.0 to 1.0
    sentiment_confidence = Column(Float)  # 0.0 to 1.0
    sentiment_subjectivity = Column(Float)  # 0.0 to 1.0
    emotion_positive = Column(Float)  # 0.0 to 1.0
    emotion_negative = Column(Float)  # 0.0 to 1.0
    emotion_neutral = Column(Float)  # 0.0 to 1.0

    # Relationships
    keywords = relationship("KeywordArticle", back_populates="article", cascade="all, delete-orphan")

    # Indexes defined in __table_args__
    __table_args__ = (
        Index('idx_articles_sentiment', 'sentiment_overall'),
        Index('idx_articles_published_date_desc', 'published_date', postgresql_using='btree'),
    )


class KeywordArticle(Base):
    """Junction table for keywords and articles with relevance scoring."""
    __tablename__ = "keyword_articles"

    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    relevance_score = Column(Float)

    # Relationships
    keyword = relationship("Keyword", back_populates="articles")
    article = relationship("Article", back_populates="keywords")


class KeywordRelation(Base):
    """Keyword relationships for mind map visualization."""
    __tablename__ = "keyword_relations"

    keyword1_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)
    keyword2_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)
    relation_type = Column(String(50))  # 'related', 'parent', 'child', 'causal'
    strength_score = Column(Float)
    evidence_count = Column(Integer, default=0)


class KeywordSuggestion(Base):
    """User-submitted keyword suggestions."""
    __tablename__ = "keyword_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    keyword_en = Column(String(255), nullable=False, index=True)
    keyword_th = Column(String(255))
    category = Column(String(100), default='general')
    reason = Column(Text)
    contact_email = Column(String(100))
    status = Column(String(20), default='pending')  # 'pending', 'approved', 'rejected'
    votes = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Document(Base):
    """Manually uploaded documents."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    upload_date = Column(DateTime, default=func.now())
    extracted_text = Column(Text)
    source_type = Column(String(50))
    doc_metadata = Column("metadata", JSONB)  # renamed to avoid SQLAlchemy reserved word


class SentimentTrend(Base):
    """Daily sentiment trends aggregation."""
    __tablename__ = "sentiment_trends"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    avg_sentiment = Column(Float)
    article_count = Column(Integer)
    positive_count = Column(Integer)
    negative_count = Column(Integer)
    neutral_count = Column(Integer)
    top_sources = Column(JSONB)  # Which sources were most positive/negative

    # Relationships
    keyword = relationship("Keyword", back_populates="sentiment_trends")

    # Unique constraint and indexes
    __table_args__ = (
        UniqueConstraint('keyword_id', 'date', name='uq_keyword_date'),
        Index('idx_sentiment_trends_date', 'date', postgresql_using='btree'),
        Index('idx_sentiment_trends_keyword_date', 'keyword_id', 'date', postgresql_using='btree'),
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
