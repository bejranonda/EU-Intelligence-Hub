"""Celery tasks for keyword search scheduling and execution."""

import logging
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.config import get_settings
from app.database import SessionLocal
from app.models.models import Article, Keyword, KeywordArticle, KeywordSearchQueue
from app.services.scraper import scrape_news_sync
from app.services.sentiment import get_sentiment_analyzer
from app.services.keyword_extractor import get_keyword_extractor
from app.services.embeddings import get_embedding_generator
from app.services.keyword_scheduler import (
    SchedulingCandidate,
    complete_job,
    dequeue_jobs,
    fill_daily_queue,
    mark_keyword_searched,
    queue_keywords,
    reset_stale_jobs,
)


settings = get_settings()

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.keyword_search.search_keyword_immediately")
def search_keyword_immediately(keyword_id: int):
    """
    Search for news articles for a specific keyword immediately.

    This task:
    1. Checks if keyword was searched in last 3 hours
    2. If not, triggers immediate news scraping for this keyword
    3. Updates last_searched timestamp
    4. Processes and stores found articles

    Args:
        keyword_id: ID of the keyword to search for

    Returns:
        dict: Search result with status and article count
    """
    logger.info(f"Starting immediate search for keyword ID: {keyword_id}")

    db = SessionLocal()
    try:
        # Get keyword
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()

        if not keyword:
            logger.error(f"Keyword ID {keyword_id} not found")
            return {"status": "error", "error": "Keyword not found"}

        cooldown = settings.keyword_search_cooldown_minutes
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=cooldown)

        if keyword.last_searched and keyword.last_searched > window_start:
            time_since_search = now - keyword.last_searched
            minutes_since = int(time_since_search.total_seconds() / 60)

            logger.info(
                f"Keyword '{keyword.keyword_en}' was searched {minutes_since} minutes ago. "
                f"Skipping immediate search (cooldown: {cooldown} minutes)"
            )

            return {
                "status": "skipped",
                "keyword": keyword.keyword_en,
                "reason": "searched_recently",
                "last_searched": keyword.last_searched.isoformat(),
                "minutes_since": minutes_since,
                "cooldown_remaining_minutes": max(cooldown - minutes_since, 0),
            }

        # Initialize services
        sentiment_analyzer = get_sentiment_analyzer()
        keyword_extractor = get_keyword_extractor()
        embedding_generator = get_embedding_generator()

        # Scrape articles for this specific keyword
        logger.info(f"Searching for news about '{keyword.keyword_en}'...")
        articles = scrape_news_sync(
            max_articles=20,  # Limit for immediate search
        )

        logger.info(f"Found {len(articles)} articles for '{keyword.keyword_en}'")

        # Update last_searched timestamp
        mark_keyword_searched(db, keyword)
        db.commit()

        if not articles:
            logger.info(f"No articles found for '{keyword.keyword_en}'")
            return {
                "status": "success",
                "keyword": keyword.keyword_en,
                "articles_found": 0,
                "articles_processed": 0,
                "last_searched": now.isoformat(),
            }

        processed_count = 0
        skipped_count = 0

        for article_data in articles:
            try:
                # Check if article already exists
                existing = (
                    db.query(Article).filter_by(source_url=article_data.url).first()
                )

                if existing:
                    # Link to keyword if not already linked
                    existing_link = (
                        db.query(KeywordArticle)
                        .filter_by(keyword_id=keyword.id, article_id=existing.id)
                        .first()
                    )

                    if not existing_link:
                        keyword_article = KeywordArticle(
                            keyword_id=keyword.id,
                            article_id=existing.id,
                            relevance_score=0.9,  # High relevance for targeted search
                        )
                        db.add(keyword_article)
                        db.commit()
                        processed_count += 1
                    else:
                        skipped_count += 1
                    continue

                # Extract keywords and classify
                extraction = keyword_extractor.extract_all(
                    article_data.title, article_data.full_text, use_gemini=True
                )

                # Analyze sentiment
                sentiment = sentiment_analyzer.analyze_article(
                    article_data.title,
                    article_data.full_text,
                    article_data.source_name,
                    use_gemini=True,
                )

                # Generate embedding for full article
                article_text = f"{article_data.title}. {article_data.summary}"
                embedding = embedding_generator.generate_embedding(article_text)

                # Create article record
                article = Article(
                    title=article_data.title,
                    summary=article_data.summary,
                    full_text=article_data.full_text,
                    source_url=article_data.url,
                    source=article_data.source_name,
                    published_date=article_data.publish_date,
                    scraped_date=now,
                    language=article_data.language,
                    classification=extraction["classification"],
                    credibility_score=extraction["classification_confidence"],
                    embedding=embedding,
                    # Sentiment fields
                    sentiment_overall=sentiment["sentiment_overall"],
                    sentiment_confidence=sentiment["sentiment_confidence"],
                    sentiment_subjectivity=sentiment["sentiment_subjectivity"],
                    emotion_positive=sentiment["emotion_positive"],
                    emotion_negative=sentiment["emotion_negative"],
                    emotion_neutral=sentiment["emotion_neutral"],
                )

                db.add(article)
                db.flush()  # Get article ID

                # Link article to the target keyword
                keyword_article = KeywordArticle(
                    keyword_id=keyword.id,
                    article_id=article.id,
                    relevance_score=0.95,  # Very high relevance for targeted search
                )
                db.add(keyword_article)

                db.commit()
                processed_count += 1
                logger.info(f"Processed: {article_data.title[:50]}...")

            except Exception as e:
                logger.error(f"Failed to process article: {str(e)}")
                db.rollback()
                continue

        logger.info(
            f"Immediate search completed for '{keyword.keyword_en}': "
            f"{processed_count} processed, {skipped_count} skipped"
        )

        return {
            "status": "success",
            "keyword": keyword.keyword_en,
            "articles_found": len(articles),
            "articles_processed": processed_count,
            "articles_skipped": skipped_count,
            "last_searched": now.isoformat(),
        }

    except Exception as e:
        logger.error(f"Immediate keyword search failed: {str(e)}")
        db.rollback()
        return {"status": "error", "keyword_id": keyword_id, "error": str(e)}

    finally:
        db.close()


@celery_app.task(name="app.tasks.keyword_search.populate_keyword_queue")
def populate_keyword_queue():
    """Populate the keyword search queue respecting daily capacity."""

    if not settings.keyword_scheduler_enabled:
        logger.info("Keyword scheduler disabled; skipping queue population")
        return {"status": "disabled"}

    db = SessionLocal()
    try:
        result = fill_daily_queue(db)
        return {"status": "ok", **result}
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to populate keyword queue: %s", exc)
        return {"status": "error", "error": str(exc)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.keyword_search.process_keyword_queue")
def process_keyword_queue(batch_size: int = None):
    """Process pending keyword search jobs with throttling."""

    if not settings.keyword_scheduler_enabled:
        logger.info("Keyword scheduler disabled; skipping queue processing")
        return {"status": "disabled"}

    db = SessionLocal()
    processed: List[dict] = []

    try:
        batch = batch_size or settings.keyword_scheduler_batch_size
        jobs = dequeue_jobs(db, limit=batch)

        if not jobs:
            reset_count = reset_stale_jobs(db)
            return {"status": "empty", "reset_jobs": reset_count}

        for job in jobs:
            keyword = db.query(Keyword).filter(Keyword.id == job.keyword_id).first()
            if not keyword:
                complete_job(db, job, success=False, error="keyword_missing")
                processed.append({"job_id": job.id, "status": "missing_keyword"})
                continue

            result = search_keyword_immediately(keyword.id)
            success = result.get("status") == "success"
            complete_job(
                db, job, success=success, error=None if success else result.get("error")
            )
            processed.append(
                {"job_id": job.id, "keyword": keyword.keyword_en, "result": result}
            )

        return {"status": "processed", "jobs": processed}
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to process keyword queue: %s", exc)
        return {"status": "error", "error": str(exc)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.keyword_search.enqueue_keywords")
def enqueue_keywords(keyword_ids: List[int]):
    """Enqueue provided keywords respecting throttling rules."""

    db = SessionLocal()
    try:
        keywords = db.query(Keyword).filter(Keyword.id.in_(keyword_ids)).all()
        candidates = [
            SchedulingCandidate(
                keyword=kw,
                next_scheduled_at=datetime.utcnow(),
                priority=kw.search_priority or 0,
            )
            for kw in keywords
        ]
        queued = queue_keywords(db, candidates)
        return {"status": "ok", "queued": queued}
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to enqueue keywords: %s", exc)
        return {"status": "error", "error": str(exc)}
    finally:
        db.close()
