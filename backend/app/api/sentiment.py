"""Sentiment analysis API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from app.database import get_db
from app.models.models import (
    Keyword, Article, SentimentTrend, ComparativeSentiment,
    keyword_article_association
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/keywords/{keyword_id}/sentiment")
async def get_keyword_sentiment(
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """
    Get overall sentiment statistics for a keyword.

    Args:
        keyword_id: Keyword ID
        db: Database session

    Returns:
        dict: Overall sentiment statistics
    """
    try:
        # Check if keyword exists
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")

        # Get all articles for this keyword
        articles = db.query(Article).join(
            keyword_article_association,
            Article.id == keyword_article_association.c.article_id
        ).filter(
            keyword_article_association.c.keyword_id == keyword_id,
            Article.sentiment_overall.isnot(None)
        ).all()

        if not articles:
            return {
                "keyword_id": keyword_id,
                "keyword_en": keyword.keyword_en,
                "total_articles": 0,
                "average_sentiment": None,
                "sentiment_distribution": {
                    "strongly_positive": 0,
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0,
                    "strongly_negative": 0
                }
            }

        # Calculate statistics
        sentiments = [a.sentiment_overall for a in articles if a.sentiment_overall is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        # Count by classification
        distribution = {
            "strongly_positive": sum(1 for a in articles if a.sentiment_classification == "STRONGLY_POSITIVE"),
            "positive": sum(1 for a in articles if a.sentiment_classification == "POSITIVE"),
            "neutral": sum(1 for a in articles if a.sentiment_classification == "NEUTRAL"),
            "negative": sum(1 for a in articles if a.sentiment_classification == "NEGATIVE"),
            "strongly_negative": sum(1 for a in articles if a.sentiment_classification == "STRONGLY_NEGATIVE")
        }

        # Find most positive and negative sources
        source_sentiments = {}
        for article in articles:
            if article.source and article.sentiment_overall is not None:
                if article.source not in source_sentiments:
                    source_sentiments[article.source] = []
                source_sentiments[article.source].append(article.sentiment_overall)

        source_averages = {
            source: sum(scores) / len(scores)
            for source, scores in source_sentiments.items()
        }

        most_positive = max(source_averages.items(), key=lambda x: x[1]) if source_averages else None
        most_negative = min(source_averages.items(), key=lambda x: x[1]) if source_averages else None

        return {
            "keyword_id": keyword_id,
            "keyword_en": keyword.keyword_en,
            "total_articles": len(articles),
            "average_sentiment": round(avg_sentiment, 3),
            "sentiment_distribution": distribution,
            "by_source": {
                "most_positive": {
                    "source": most_positive[0],
                    "average_sentiment": round(most_positive[1], 3)
                } if most_positive else None,
                "most_negative": {
                    "source": most_negative[0],
                    "average_sentiment": round(most_negative[1], 3)
                } if most_negative else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sentiment for keyword {keyword_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sentiment: {str(e)}")


@router.get("/keywords/{keyword_id}/sentiment/timeline")
async def get_sentiment_timeline(
    keyword_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get sentiment timeline for a keyword.

    Shows how sentiment has changed over time.

    Args:
        keyword_id: Keyword ID
        days: Number of days to retrieve
        db: Database session

    Returns:
        dict: Time-series sentiment data
    """
    try:
        # Check if keyword exists
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")

        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        # Get sentiment trends
        trends = db.query(SentimentTrend).filter(
            SentimentTrend.keyword_id == keyword_id,
            SentimentTrend.date >= start_date,
            SentimentTrend.date <= end_date
        ).order_by(SentimentTrend.date).all()

        # Format results
        timeline = []
        for trend in trends:
            timeline.append({
                "date": trend.date.isoformat(),
                "average_sentiment": round(trend.average_sentiment, 3) if trend.average_sentiment else None,
                "positive_count": trend.positive_count,
                "negative_count": trend.negative_count,
                "neutral_count": trend.neutral_count,
                "total_articles": (trend.positive_count or 0) + (trend.negative_count or 0) + (trend.neutral_count or 0),
                "top_sources": trend.top_sources
            })

        # Calculate overall trend
        if len(timeline) >= 2:
            first_sentiment = timeline[0]["average_sentiment"]
            last_sentiment = timeline[-1]["average_sentiment"]
            if first_sentiment is not None and last_sentiment is not None:
                trend_direction = "improving" if last_sentiment > first_sentiment else "declining" if last_sentiment < first_sentiment else "stable"
                trend_change = round((last_sentiment - first_sentiment) / abs(first_sentiment) * 100, 1) if first_sentiment != 0 else 0
            else:
                trend_direction = "unknown"
                trend_change = 0
        else:
            trend_direction = "insufficient_data"
            trend_change = 0

        return {
            "keyword_id": keyword_id,
            "keyword_en": keyword.keyword_en,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "timeline": timeline,
            "trend": {
                "direction": trend_direction,
                "change_percent": trend_change
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sentiment timeline for keyword {keyword_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving timeline: {str(e)}")


@router.get("/keywords/compare")
async def compare_keyword_sentiment(
    keyword_ids: str = Query(..., description="Comma-separated keyword IDs (e.g., '1,2,3')"),
    db: Session = Depends(get_db)
):
    """
    Compare sentiment across multiple keywords.

    Useful for comparing media coverage of different countries or topics.

    Args:
        keyword_ids: Comma-separated keyword IDs
        db: Database session

    Returns:
        dict: Comparative sentiment analysis
    """
    try:
        # Parse keyword IDs
        try:
            ids = [int(kid.strip()) for kid in keyword_ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid keyword IDs format")

        if len(ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 keywords required for comparison")

        if len(ids) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 keywords allowed for comparison")

        # Get keywords
        keywords = db.query(Keyword).filter(Keyword.id.in_(ids)).all()

        if len(keywords) != len(ids):
            raise HTTPException(status_code=404, detail="One or more keywords not found")

        # Get sentiment for each keyword
        comparison = []
        for keyword in keywords:
            # Get articles
            articles = db.query(Article).join(
                keyword_article_association,
                Article.id == keyword_article_association.c.article_id
            ).filter(
                keyword_article_association.c.keyword_id == keyword.id,
                Article.sentiment_overall.isnot(None)
            ).all()

            # Calculate statistics
            if articles:
                sentiments = [a.sentiment_overall for a in articles if a.sentiment_overall is not None]
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

                comparison.append({
                    "keyword_id": keyword.id,
                    "keyword_en": keyword.keyword_en,
                    "keyword_th": keyword.keyword_th,
                    "average_sentiment": round(avg_sentiment, 3),
                    "total_articles": len(articles),
                    "positive_count": sum(1 for a in articles if a.sentiment_overall and a.sentiment_overall > 0.2),
                    "negative_count": sum(1 for a in articles if a.sentiment_overall and a.sentiment_overall < -0.2),
                    "neutral_count": sum(1 for a in articles if a.sentiment_overall and -0.2 <= a.sentiment_overall <= 0.2)
                })
            else:
                comparison.append({
                    "keyword_id": keyword.id,
                    "keyword_en": keyword.keyword_en,
                    "keyword_th": keyword.keyword_th,
                    "average_sentiment": None,
                    "total_articles": 0,
                    "positive_count": 0,
                    "negative_count": 0,
                    "neutral_count": 0
                })

        # Sort by average sentiment descending
        comparison.sort(key=lambda x: x["average_sentiment"] if x["average_sentiment"] is not None else -999, reverse=True)

        # Calculate rankings
        most_positive = comparison[0] if comparison else None
        most_negative = comparison[-1] if comparison else None

        return {
            "comparison": comparison,
            "summary": {
                "most_positive": most_positive,
                "most_negative": most_negative,
                "total_keywords": len(comparison)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing keywords: {e}")
        raise HTTPException(status_code=500, detail=f"Error comparing keywords: {str(e)}")


@router.get("/articles/{article_id}/sentiment")
async def get_article_sentiment_details(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed sentiment analysis for a specific article.

    Args:
        article_id: Article ID
        db: Database session

    Returns:
        dict: Detailed sentiment breakdown
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Get associated keywords
        keywords = db.query(Keyword).join(
            keyword_article_association,
            Keyword.id == keyword_article_association.c.keyword_id
        ).filter(
            keyword_article_association.c.article_id == article.id
        ).all()

        return {
            "article_id": article.id,
            "title": article.title,
            "source": article.source,
            "published_date": article.published_date.isoformat() if article.published_date else None,
            "sentiment": {
                "overall": article.sentiment_overall,
                "confidence": article.sentiment_confidence,
                "classification": article.sentiment_classification,
                "subjectivity": article.sentiment_subjectivity,
                "emotions": {
                    "positive": article.emotion_positive,
                    "negative": article.emotion_negative,
                    "neutral": article.emotion_neutral
                }
            },
            "classification": article.classification,
            "keywords": [
                {
                    "id": kw.id,
                    "keyword_en": kw.keyword_en,
                    "category": kw.category
                }
                for kw in keywords
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sentiment details for article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sentiment details: {str(e)}")
