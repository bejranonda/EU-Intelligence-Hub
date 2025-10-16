"""
Celery task for immediate keyword news search.

This task is triggered when a keyword is approved to search for news immediately
if the keyword hasn't been searched within the last 3 hours.
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.models import Article, Keyword, KeywordArticle
from app.services.scraper import scrape_news_sync
from app.services.sentiment import get_sentiment_analyzer
from app.services.keyword_extractor import get_keyword_extractor
from app.services.embeddings import get_embedding_generator

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
            return {
                'status': 'error',
                'error': 'Keyword not found'
            }

        # Check if keyword was searched in last 3 hours
        now = datetime.now()
        three_hours_ago = now - timedelta(hours=3)

        if keyword.last_searched and keyword.last_searched > three_hours_ago:
            time_since_search = now - keyword.last_searched
            minutes_since = int(time_since_search.total_seconds() / 60)

            logger.info(
                f"Keyword '{keyword.keyword_en}' was searched {minutes_since} minutes ago. "
                f"Skipping immediate search (cooldown: 3 hours)"
            )

            return {
                'status': 'skipped',
                'keyword': keyword.keyword_en,
                'reason': 'searched_recently',
                'last_searched': keyword.last_searched.isoformat(),
                'minutes_since': minutes_since,
                'cooldown_remaining_minutes': 180 - minutes_since
            }

        # Initialize services
        sentiment_analyzer = get_sentiment_analyzer()
        keyword_extractor = get_keyword_extractor()
        embedding_generator = get_embedding_generator()

        # Scrape articles for this specific keyword
        logger.info(f"Searching for news about '{keyword.keyword_en}'...")
        articles = scrape_news_sync(
            keyword_filter=keyword.keyword_en,
            max_articles=20  # Limit for immediate search
        )

        logger.info(f"Found {len(articles)} articles for '{keyword.keyword_en}'")

        # Update last_searched timestamp
        keyword.last_searched = now
        keyword.search_count += 1
        db.commit()

        if not articles:
            logger.info(f"No articles found for '{keyword.keyword_en}'")
            return {
                'status': 'success',
                'keyword': keyword.keyword_en,
                'articles_found': 0,
                'articles_processed': 0,
                'last_searched': now.isoformat()
            }

        processed_count = 0
        skipped_count = 0

        for article_data in articles:
            try:
                # Check if article already exists
                existing = db.query(Article).filter_by(
                    source_url=article_data.url
                ).first()

                if existing:
                    # Link to keyword if not already linked
                    existing_link = db.query(KeywordArticle).filter_by(
                        keyword_id=keyword.id,
                        article_id=existing.id
                    ).first()

                    if not existing_link:
                        keyword_article = KeywordArticle(
                            keyword_id=keyword.id,
                            article_id=existing.id,
                            relevance_score=0.9  # High relevance for targeted search
                        )
                        db.add(keyword_article)
                        db.commit()
                        processed_count += 1
                    else:
                        skipped_count += 1
                    continue

                # Extract keywords and classify
                extraction = keyword_extractor.extract_all(
                    article_data.title,
                    article_data.full_text,
                    use_gemini=True
                )

                # Analyze sentiment
                sentiment = sentiment_analyzer.analyze_article(
                    article_data.title,
                    article_data.full_text,
                    article_data.source_name,
                    use_gemini=True
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
                    classification=extraction['classification'],
                    credibility_score=extraction['classification_confidence'],
                    embedding=embedding,
                    # Sentiment fields
                    sentiment_overall=sentiment['sentiment_overall'],
                    sentiment_confidence=sentiment['sentiment_confidence'],
                    sentiment_subjectivity=sentiment['sentiment_subjectivity'],
                    emotion_positive=sentiment['emotion_positive'],
                    emotion_negative=sentiment['emotion_negative'],
                    emotion_neutral=sentiment['emotion_neutral']
                )

                db.add(article)
                db.flush()  # Get article ID

                # Link article to the target keyword
                keyword_article = KeywordArticle(
                    keyword_id=keyword.id,
                    article_id=article.id,
                    relevance_score=0.95  # Very high relevance for targeted search
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
            'status': 'success',
            'keyword': keyword.keyword_en,
            'articles_found': len(articles),
            'articles_processed': processed_count,
            'articles_skipped': skipped_count,
            'last_searched': now.isoformat()
        }

    except Exception as e:
        logger.error(f"Immediate keyword search failed: {str(e)}")
        db.rollback()
        return {
            'status': 'error',
            'keyword_id': keyword_id,
            'error': str(e)
        }

    finally:
        db.close()
