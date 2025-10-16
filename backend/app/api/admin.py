"""Admin API endpoints for keyword management."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.models.models import KeywordSuggestion, Keyword
from app.services.keyword_approval import keyword_approval_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/keywords/suggestions/{suggestion_id}/process")
async def process_suggestion_manually(
    suggestion_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually trigger AI processing of a keyword suggestion.

    This endpoint allows admins to process suggestions on-demand
    rather than waiting for the daily automated task.

    Args:
        suggestion_id: ID of the suggestion to process
        db: Database session

    Returns:
        dict: Processing result with AI decision and reasoning
    """
    try:
        result = await keyword_approval_service.process_suggestion(
            suggestion_id=suggestion_id,
            db=db
        )

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return {
            "success": True,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing suggestion {suggestion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing suggestion: {str(e)}")


@router.get("/keywords/suggestions/pending")
async def get_pending_suggestions(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get all pending keyword suggestions ordered by votes.

    Args:
        limit: Maximum number of suggestions to return
        db: Database session

    Returns:
        dict: List of pending suggestions
    """
    try:
        suggestions = db.query(KeywordSuggestion).filter(
            KeywordSuggestion.status == 'pending'
        ).order_by(
            KeywordSuggestion.votes.desc(),
            KeywordSuggestion.created_at.desc()
        ).limit(limit).all()

        results = []
        for suggestion in suggestions:
            results.append({
                "id": suggestion.id,
                "keyword_en": suggestion.keyword_en,
                "keyword_th": suggestion.keyword_th,
                "category": suggestion.category,
                "reason": suggestion.reason,
                "votes": suggestion.votes,
                "status": suggestion.status,
                "created_at": suggestion.created_at.isoformat()
            })

        return {
            "pending_suggestions": results,
            "total": len(results)
        }

    except Exception as e:
        logger.error(f"Error getting pending suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving suggestions: {str(e)}")


@router.post("/keywords/suggestions/{suggestion_id}/approve")
async def approve_suggestion_manually(
    suggestion_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually approve a suggestion and create keyword.

    Bypasses AI evaluation for admin approval.

    Args:
        suggestion_id: ID of the suggestion
        db: Database session

    Returns:
        dict: Created keyword details
    """
    try:
        suggestion = db.query(KeywordSuggestion).filter(
            KeywordSuggestion.id == suggestion_id
        ).first()

        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        # Create new keyword
        from app.services.embeddings import EmbeddingService
        embedding_service = EmbeddingService()

        new_keyword = Keyword(
            keyword_en=suggestion.keyword_en,
            keyword_th=suggestion.keyword_th,
            category=suggestion.category or "general",
            embedding=embedding_service.generate_embedding(suggestion.keyword_en)
        )
        db.add(new_keyword)

        # Update suggestion status
        suggestion.status = "approved"

        db.commit()
        db.refresh(new_keyword)

        logger.info(f"Manually approved keyword '{suggestion.keyword_en}' (ID: {new_keyword.id})")

        return {
            "success": True,
            "keyword": {
                "id": new_keyword.id,
                "keyword_en": new_keyword.keyword_en,
                "keyword_th": new_keyword.keyword_th,
                "category": new_keyword.category
            },
            "message": f"Keyword '{suggestion.keyword_en}' approved and created"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving suggestion {suggestion_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error approving suggestion: {str(e)}")


@router.post("/keywords/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: int,
    reason: Optional[str] = Query(None, description="Reason for rejection"),
    db: Session = Depends(get_db)
):
    """
    Manually reject a keyword suggestion.

    Args:
        suggestion_id: ID of the suggestion
        reason: Optional reason for rejection
        db: Database session

    Returns:
        dict: Confirmation
    """
    try:
        suggestion = db.query(KeywordSuggestion).filter(
            KeywordSuggestion.id == suggestion_id
        ).first()

        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        suggestion.status = "rejected"
        db.commit()

        logger.info(f"Rejected suggestion '{suggestion.keyword_en}': {reason or 'No reason provided'}")

        return {
            "success": True,
            "message": f"Suggestion '{suggestion.keyword_en}' rejected"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting suggestion {suggestion_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error rejecting suggestion: {str(e)}")


@router.get("/keywords/suggestions/stats")
async def get_suggestion_stats(db: Session = Depends(get_db)):
    """
    Get statistics about keyword suggestions.

    Returns:
        dict: Counts by status and other stats
    """
    try:
        from sqlalchemy import func

        total = db.query(func.count(KeywordSuggestion.id)).scalar()
        pending = db.query(func.count(KeywordSuggestion.id)).filter(
            KeywordSuggestion.status == 'pending'
        ).scalar()
        approved = db.query(func.count(KeywordSuggestion.id)).filter(
            KeywordSuggestion.status == 'approved'
        ).scalar()
        rejected = db.query(func.count(KeywordSuggestion.id)).filter(
            KeywordSuggestion.status == 'rejected'
        ).scalar()
        merged = db.query(func.count(KeywordSuggestion.id)).filter(
            KeywordSuggestion.status == 'merged'
        ).scalar()

        # Top suggestions by votes
        top_suggestions = db.query(KeywordSuggestion).filter(
            KeywordSuggestion.status == 'pending'
        ).order_by(KeywordSuggestion.votes.desc()).limit(10).all()

        return {
            "total_suggestions": total,
            "by_status": {
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "merged": merged
            },
            "top_pending": [
                {
                    "id": s.id,
                    "keyword_en": s.keyword_en,
                    "votes": s.votes
                }
                for s in top_suggestions
            ]
        }

    except Exception as e:
        logger.error(f"Error getting suggestion stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")
