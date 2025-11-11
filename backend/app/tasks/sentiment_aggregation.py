"""
Celery tasks for sentiment aggregation.

Scheduled tasks:
- Daily: Aggregate sentiment trends for all keywords
"""

import logging
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.models import Keyword, Article, KeywordArticle, SentimentTrend

logger = logging.getLogger(__name__)


def classify_sentiment_category(sentiment_overall: float, confidence: float) -> str:
    """
    Classify sentiment into category.

    Args:
        sentiment_overall: Sentiment score -1 to 1
        confidence: Confidence 0 to 1

    Returns:
        Category string
    """
    confidence_multiplier = max(confidence, 0.3)
    strong_threshold = 0.5 * confidence_multiplier
    moderate_threshold = 0.2 * confidence_multiplier

    if sentiment_overall >= strong_threshold:
        return "STRONGLY_POSITIVE"
    elif sentiment_overall >= moderate_threshold:
        return "POSITIVE"
    elif sentiment_overall <= -strong_threshold:
        return "STRONGLY_NEGATIVE"
    elif sentiment_overall <= -moderate_threshold:
        return "NEGATIVE"
    else:
        return "NEUTRAL"


@celery_app.task(name="app.tasks.sentiment_aggregation.aggregate_daily_sentiment")
def aggregate_daily_sentiment(target_date: str = None):
    """
    Calculate aggregate sentiment metrics for all keywords on a specific date.

    This function weights sentiment by confidence to prioritize reliable scores
    and tracks which sources are most positive/negative.

    Args:
        target_date: Date to aggregate (format: YYYY-MM-DD). Defaults to yesterday.

    Returns:
        Dict with aggregation results
    """
    logger.info("Starting daily sentiment aggregation task...")

    db = SessionLocal()
    try:
        # Parse target date or use yesterday
        if target_date:
            agg_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        else:
            agg_date = date.today() - timedelta(days=1)

        logger.info(f"Aggregating sentiment for date: {agg_date}")

        # Get all keywords
        keywords = db.query(Keyword).all()
        processed_count = 0

        for keyword in keywords:
            try:
                # Get articles for this keyword on this date
                articles = (
                    db.query(Article)
                    .join(KeywordArticle, Article.id == KeywordArticle.article_id)
                    .filter(
                        KeywordArticle.keyword_id == keyword.id,
                        func.date(Article.publish_date) == agg_date,
                        Article.sentiment_overall.isnot(None),
                    )
                    .all()
                )

                if not articles:
                    logger.debug(
                        f"No articles for keyword '{keyword.name_en}' on {agg_date}"
                    )
                    continue

                # Calculate weighted average sentiment
                total_weighted_sentiment = 0.0
                total_weight = 0.0
                positive_count = 0
                negative_count = 0
                neutral_count = 0
                source_sentiments = {}

                for article in articles:
                    # Weight by confidence
                    weight = article.sentiment_confidence or 0.5
                    total_weighted_sentiment += article.sentiment_overall * weight
                    total_weight += weight

                    # Count by category
                    category = classify_sentiment_category(
                        article.sentiment_overall, article.sentiment_confidence
                    )

                    if "POSITIVE" in category:
                        positive_count += 1
                    elif "NEGATIVE" in category:
                        negative_count += 1
                    else:
                        neutral_count += 1

                    # Track by source
                    source = article.source_name
                    if source not in source_sentiments:
                        source_sentiments[source] = []
                    source_sentiments[source].append(article.sentiment_overall)

                # Calculate average
                avg_sentiment = (
                    total_weighted_sentiment / total_weight if total_weight > 0 else 0.0
                )

                # Calculate average sentiment per source
                top_sources = {}
                for source, scores in source_sentiments.items():
                    if scores:
                        top_sources[source] = round(sum(scores) / len(scores), 3)

                # Check if trend already exists for this date
                existing_trend = (
                    db.query(SentimentTrend)
                    .filter_by(keyword_id=keyword.id, date=agg_date)
                    .first()
                )

                if existing_trend:
                    # Update existing
                    existing_trend.avg_sentiment = avg_sentiment
                    existing_trend.article_count = len(articles)
                    existing_trend.positive_count = positive_count
                    existing_trend.negative_count = negative_count
                    existing_trend.neutral_count = neutral_count
                    existing_trend.top_sources = top_sources
                else:
                    # Create new trend
                    trend = SentimentTrend(
                        keyword_id=keyword.id,
                        date=agg_date,
                        avg_sentiment=avg_sentiment,
                        article_count=len(articles),
                        positive_count=positive_count,
                        negative_count=negative_count,
                        neutral_count=neutral_count,
                        top_sources=top_sources,
                    )
                    db.add(trend)

                db.commit()
                processed_count += 1

                logger.info(
                    f"Aggregated sentiment for '{keyword.name_en}': "
                    f"{avg_sentiment:.2f} ({len(articles)} articles)"
                )

            except Exception as e:
                logger.error(
                    f"Failed to aggregate sentiment for keyword {keyword.name_en}: {str(e)}"
                )
                db.rollback()
                continue

        logger.info(
            f"Sentiment aggregation completed: {processed_count} keywords processed"
        )

        return {
            "status": "success",
            "date": str(agg_date),
            "keywords_processed": processed_count,
        }

    except Exception as e:
        logger.error(f"Sentiment aggregation task failed: {str(e)}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()


@celery_app.task(name="app.tasks.sentiment_aggregation.aggregate_keyword_sentiment")
def aggregate_keyword_sentiment(keyword_id: int, start_date: str, end_date: str):
    """
    Aggregate sentiment for a specific keyword over a date range.

    Args:
        keyword_id: Keyword ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Dict with aggregation results
    """
    db = SessionLocal()
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        keyword = db.query(Keyword).filter_by(id=keyword_id).first()
        if not keyword:
            return {"status": "error", "error": "Keyword not found"}

        # Aggregate for each date in range
        current_date = start
        processed_dates = []

        while current_date <= end:
            # Get articles for this date
            articles = (
                db.query(Article)
                .join(KeywordArticle, Article.id == KeywordArticle.article_id)
                .filter(
                    KeywordArticle.keyword_id == keyword_id,
                    func.date(Article.publish_date) == current_date,
                    Article.sentiment_overall.isnot(None),
                )
                .all()
            )

            if articles:
                # Calculate aggregates (similar to daily task)
                total_weighted = sum(
                    a.sentiment_overall * (a.sentiment_confidence or 0.5)
                    for a in articles
                )
                total_weight = sum(a.sentiment_confidence or 0.5 for a in articles)
                avg_sentiment = (
                    total_weighted / total_weight if total_weight > 0 else 0.0
                )

                # Count categories
                positive_count = sum(
                    1
                    for a in articles
                    if classify_sentiment_category(
                        a.sentiment_overall, a.sentiment_confidence or 0.5
                    )
                    in ["POSITIVE", "STRONGLY_POSITIVE"]
                )
                negative_count = sum(
                    1
                    for a in articles
                    if classify_sentiment_category(
                        a.sentiment_overall, a.sentiment_confidence or 0.5
                    )
                    in ["NEGATIVE", "STRONGLY_NEGATIVE"]
                )
                neutral_count = len(articles) - positive_count - negative_count

                # Update or create trend
                trend = (
                    db.query(SentimentTrend)
                    .filter_by(keyword_id=keyword_id, date=current_date)
                    .first()
                )

                if trend:
                    trend.avg_sentiment = avg_sentiment
                    trend.article_count = len(articles)
                    trend.positive_count = positive_count
                    trend.negative_count = negative_count
                    trend.neutral_count = neutral_count
                else:
                    trend = SentimentTrend(
                        keyword_id=keyword_id,
                        date=current_date,
                        avg_sentiment=avg_sentiment,
                        article_count=len(articles),
                        positive_count=positive_count,
                        negative_count=negative_count,
                        neutral_count=neutral_count,
                    )
                    db.add(trend)

                processed_dates.append(str(current_date))

            current_date += timedelta(days=1)

        db.commit()

        return {
            "status": "success",
            "keyword": keyword.name_en,
            "dates_processed": processed_dates,
        }

    except Exception as e:
        logger.error(f"Keyword sentiment aggregation failed: {str(e)}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()
