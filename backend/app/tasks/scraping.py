"""
Celery tasks for news scraping and processing.

Scheduled tasks:
- Hourly: Scrape news from European sources
- Process each article: extract keywords, analyze sentiment, generate embeddings
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.models import (
    Article,
    Keyword,
    KeywordArticle,
    SourceIngestionHistory,
    NewsSource,
)
from app.services.scraper import scrape_news_sync
from app.services.sentiment import get_sentiment_analyzer
from app.services.keyword_extractor import get_keyword_extractor
from app.services.embeddings import get_embedding_generator

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.scraping.scrape_news")
def scrape_news():
    """
    Scrape news from European sources and process articles.

    This task:
    1. Scrapes articles from BBC, Reuters, DW, France24
    2. Extracts keywords and entities
    3. Analyzes sentiment
    4. Classifies as fact/opinion
    5. Generates embeddings
    6. Stores in database
    """
    logger.info("Starting hourly news scraping task...")

    db = SessionLocal()
    try:
        # Initialize services
        sentiment_analyzer = get_sentiment_analyzer()
        keyword_extractor = get_keyword_extractor()
        embedding_generator = get_embedding_generator()

        # Scrape articles
        articles = scrape_news_sync(max_articles=10)  # Limit for testing
        logger.info(f"Scraped {len(articles)} articles")

        processed_count = 0
        skipped_count = 0
        ingestion_records = {}

        for article_data in articles:
            try:
                # Check if article already exists
                existing = (
                    db.query(Article).filter_by(source_url=article_data.url).first()
                )

                if existing:
                    logger.debug(
                        f"Article already exists: {article_data.title[:50]}..."
                    )
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
                    scraped_date=datetime.now(),
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

                # Process keywords
                for keyword_text in extraction["keywords"]:
                    # Find or create keyword
                    keyword = db.query(Keyword).filter_by(keyword_en=keyword_text).first()

                    if not keyword:
                        # Generate embedding for keyword
                        keyword_embedding = embedding_generator.generate_embedding(
                            keyword_text
                        )

                        keyword = Keyword(
                            keyword_en=keyword_text,
                            category="auto",
                            popularity_score=1.0,
                            search_count=0,
                            embedding=keyword_embedding,
                        )
                        db.add(keyword)
                        db.flush()
                    else:
                        # Update popularity
                        keyword.popularity_score += 0.1
                        keyword.last_updated = datetime.now()

                    # Link article to keyword
                    keyword_article = KeywordArticle(
                        keyword_id=keyword.id,
                        article_id=article.id,
                        relevance_score=0.8,  # Could calculate based on frequency
                    )
                    db.add(keyword_article)

                db.commit()
                processed_count += 1
                logger.info(f"Processed: {article_data.title[:50]}...")

                if article_data.source_name:
                    ingestion_records.setdefault(article_data.source_name, 0)
                    ingestion_records[article_data.source_name] += 1

            except Exception as e:
                logger.error(f"Failed to process article: {str(e)}")
                db.rollback()
                continue

        try:
            for source_name, count in ingestion_records.items():
                source_record = db.query(NewsSource).filter_by(name=source_name).first()
                if not source_record:
                    continue
                db.add(
                    SourceIngestionHistory(
                        source_id=source_record.id,
                        last_run_at=datetime.now(),
                        articles_ingested=count,
                        success=True,
                    )
                )
            db.commit()
        except Exception as history_exc:
            logger.warning(f"Failed to record ingestion history: {history_exc}")

        logger.info(
            f"Scraping task completed: {processed_count} processed, "
            f"{skipped_count} skipped"
        )

        return {
            "status": "success",
            "processed": processed_count,
            "skipped": skipped_count,
            "total": len(articles),
        }

    except Exception as e:
        logger.error(f"Scraping task failed: {str(e)}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()


@celery_app.task(name="app.tasks.scraping.process_single_article")
def process_single_article(article_url: str, article_title: str, article_text: str):
    """
    Process a single article (for manual uploads or testing).

    Args:
        article_url: Article URL
        article_title: Article title
        article_text: Article full text

    Returns:
        Processing result dictionary
    """
    db = SessionLocal()
    try:
        # Initialize services
        sentiment_analyzer = get_sentiment_analyzer()
        keyword_extractor = get_keyword_extractor()
        embedding_generator = get_embedding_generator()

        # Extract keywords and classify
        extraction = keyword_extractor.extract_all(
            article_title, article_text, use_gemini=True
        )

        # Analyze sentiment
        sentiment = sentiment_analyzer.analyze_article(
            article_title, article_text, "Manual Upload", use_gemini=True
        )

        # Generate embedding
        article_combined = f"{article_title}. {article_text[:1000]}"
        embedding = embedding_generator.generate_embedding(article_combined)

        # Create article
        article = Article(
            title=article_title,
            full_text=article_text,
            source_url=article_url,
            source="Manual Upload",
            published_date=datetime.now(),
            scraped_date=datetime.now(),
            language="en",
            classification=extraction["classification"],
            credibility_score=extraction["classification_confidence"],
            embedding=embedding,
            sentiment_overall=sentiment["sentiment_overall"],
            sentiment_confidence=sentiment["sentiment_confidence"],
            sentiment_subjectivity=sentiment["sentiment_subjectivity"],
            emotion_positive=sentiment["emotion_positive"],
            emotion_negative=sentiment["emotion_negative"],
            emotion_neutral=sentiment["emotion_neutral"],
        )

        db.add(article)
        db.commit()

        return {
            "status": "success",
            "article_id": article.id,
            "keywords": extraction["keywords"],
            "sentiment": sentiment["classification"],
        }

    except Exception as e:
        logger.error(f"Failed to process single article: {str(e)}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()
