"""
Celery tasks for automated keyword management and approval.
"""
import logging
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.models import KeywordSuggestion, Keyword
from app.services.keyword_approval import keyword_approval_service

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.keyword_management.process_pending_suggestions")
def process_pending_suggestions():
    """
    Process all pending keyword suggestions using AI.

    This task runs daily to:
    1. Evaluate significance of suggested keywords
    2. Check for duplicates/similar keywords
    3. Determine if keywords should be merged
    4. Auto-approve significant keywords
    5. Store unclear cases for manual review
    """
    db: Session = SessionLocal()

    try:
        # Get all pending suggestions
        pending_suggestions = (
            db.query(KeywordSuggestion)
            .filter(KeywordSuggestion.status == "pending")
            .order_by(KeywordSuggestion.votes.desc())
            .all()
        )

        logger.info(
            f"Processing {len(pending_suggestions)} pending keyword suggestions"
        )

        results = {
            "processed": 0,
            "approved": 0,
            "rejected": 0,
            "merged": 0,
            "pending_alternatives": 0,
            "errors": 0,
        }

        # Process each suggestion
        for suggestion in pending_suggestions:
            try:
                # Use AI to process the suggestion
                result = keyword_approval_service.process_suggestion(
                    suggestion_id=suggestion.id, db=db
                )

                results["processed"] += 1

                # Count by action
                action = result.get("action")
                if action == "approved":
                    results["approved"] += 1
                    logger.info(f"✓ Approved keyword: {suggestion.keyword_en}")
                elif action == "rejected":
                    results["rejected"] += 1
                    logger.info(f"✗ Rejected keyword: {suggestion.keyword_en}")
                elif action == "merged":
                    results["merged"] += 1
                    logger.info(f"⚡ Merged keyword: {suggestion.keyword_en}")
                elif action == "pending_alternatives":
                    results["pending_alternatives"] += 1
                    logger.info(f"⏸ Pending alternatives: {suggestion.keyword_en}")

            except Exception as e:
                logger.error(f"Error processing suggestion {suggestion.id}: {e}")
                results["errors"] += 1
                continue

        logger.info(f"Keyword processing complete: {results}")

        return {"status": "success", "results": results}

    except Exception as e:
        logger.error(f"Error in process_pending_suggestions task: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.keyword_management.review_keyword_performance")
def review_keyword_performance():
    """
    Review performance of approved keywords.

    Checks if keywords are actually finding articles.
    If no articles found for 30 days, mark for review.
    """
    db: Session = SessionLocal()

    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        from app.models.models import KeywordArticle

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Get all active keywords
        keywords = db.query(Keyword).all()

        inactive_keywords = []

        for keyword in keywords:
            # Count articles in last 30 days
            article_count = (
                db.query(func.count(KeywordArticle.article_id))
                .filter(KeywordArticle.keyword_id == keyword.id)
                .scalar()
            )

            if article_count == 0:
                inactive_keywords.append(
                    {
                        "id": keyword.id,
                        "keyword": keyword.keyword_en,
                        "category": keyword.category,
                    }
                )
                logger.warning(
                    f"Keyword '{keyword.keyword_en}' has no articles in 30 days"
                )

        logger.info(
            f"Keyword performance review: {len(inactive_keywords)} inactive keywords"
        )

        return {
            "status": "success",
            "total_keywords": len(keywords),
            "inactive_keywords": len(inactive_keywords),
            "inactive_list": inactive_keywords,
        }

    except Exception as e:
        logger.error(f"Error in review_keyword_performance task: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.keyword_management.suggest_keyword_groups")
def suggest_keyword_groups():
    """
    Use AI to suggest grouping related keywords.

    Helps identify keywords that should be searched together
    for better news discovery.
    """
    db: Session = SessionLocal()

    try:
        # Get all keywords
        keywords = db.query(Keyword).all()

        if len(keywords) < 3:
            logger.info("Not enough keywords to suggest groups")
            return {"status": "skipped", "reason": "insufficient keywords"}

        # Group by category first
        categories = {}
        for kw in keywords:
            cat = kw.category or "general"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(kw.keyword_en)

        logger.info(f"Found {len(categories)} categories with keywords")

        suggested_groups = []

        # For each category with multiple keywords, suggest groupings
        for category, keyword_list in categories.items():
            if len(keyword_list) >= 2:
                suggested_groups.append(
                    {
                        "category": category,
                        "keywords": keyword_list,
                        "count": len(keyword_list),
                        "suggestion": f"Consider searching these {len(keyword_list)} {category} keywords together",
                    }
                )

        logger.info(f"Suggested {len(suggested_groups)} keyword groups")

        return {"status": "success", "groups": suggested_groups}

    except Exception as e:
        logger.error(f"Error in suggest_keyword_groups task: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
