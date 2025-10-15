"""Keyword suggestion API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import logging
from datetime import datetime

from app.database import get_db
from app.models.models import KeywordSuggestion

logger = logging.getLogger(__name__)

router = APIRouter()


class SuggestionCreate(BaseModel):
    """Schema for creating a keyword suggestion."""
    keyword_en: str = Field(..., min_length=2, max_length=100, description="Keyword in English")
    keyword_th: Optional[str] = Field(None, max_length=100, description="Keyword in Thai")
    category: Optional[str] = Field("general", max_length=50, description="Category")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for suggestion")
    contact_email: Optional[str] = Field(None, max_length=100, description="Contact email")


class SuggestionResponse(BaseModel):
    """Schema for suggestion response."""
    id: int
    keyword_en: str
    keyword_th: Optional[str]
    category: str
    status: str
    votes: int
    created_at: str


@router.post("/", response_model=dict)
async def create_suggestion(
    suggestion: SuggestionCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a keyword suggestion.

    Allows visitors to suggest keywords for future research.

    Args:
        suggestion: Suggestion data
        db: Database session

    Returns:
        dict: Created suggestion details
    """
    try:
        # Check if similar suggestion already exists
        existing = db.query(KeywordSuggestion).filter(
            KeywordSuggestion.keyword_en.ilike(suggestion.keyword_en)
        ).first()

        if existing:
            # Increment vote count for existing suggestion
            existing.votes += 1
            db.commit()
            db.refresh(existing)

            return {
                "success": True,
                "suggestion": {
                    "id": existing.id,
                    "keyword_en": existing.keyword_en,
                    "keyword_th": existing.keyword_th,
                    "category": existing.category,
                    "status": existing.status,
                    "votes": existing.votes,
                    "created_at": existing.created_at.isoformat()
                },
                "message": "Similar suggestion already exists. Vote count increased!"
            }

        # Create new suggestion
        new_suggestion = KeywordSuggestion(
            keyword_en=suggestion.keyword_en,
            keyword_th=suggestion.keyword_th,
            category=suggestion.category or "general",
            reason=suggestion.reason,
            contact_email=suggestion.contact_email,
            status="pending",
            votes=1
        )

        db.add(new_suggestion)
        db.commit()
        db.refresh(new_suggestion)

        return {
            "success": True,
            "suggestion": {
                "id": new_suggestion.id,
                "keyword_en": new_suggestion.keyword_en,
                "keyword_th": new_suggestion.keyword_th,
                "category": new_suggestion.category,
                "status": new_suggestion.status,
                "votes": new_suggestion.votes,
                "created_at": new_suggestion.created_at.isoformat()
            },
            "message": "Thank you for your suggestion! It will be reviewed by our team."
        }

    except Exception as e:
        logger.error(f"Error creating suggestion: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating suggestion: {str(e)}")


@router.get("/")
async def get_suggestions(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get keyword suggestions.

    Args:
        status: Filter by status (pending/approved/rejected)
        limit: Maximum number of results
        db: Database session

    Returns:
        dict: List of suggestions
    """
    try:
        query = db.query(KeywordSuggestion)

        if status:
            query = query.filter(KeywordSuggestion.status == status)

        # Order by votes descending, then by created date
        suggestions = query.order_by(
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
                "status": suggestion.status,
                "votes": suggestion.votes,
                "created_at": suggestion.created_at.isoformat()
            })

        return {
            "suggestions": results,
            "total": len(results),
            "status_filter": status
        }

    except Exception as e:
        logger.error(f"Error retrieving suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving suggestions: {str(e)}")


@router.get("/{suggestion_id}")
async def get_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific suggestion by ID.

    Args:
        suggestion_id: Suggestion ID
        db: Database session

    Returns:
        dict: Suggestion details
    """
    try:
        suggestion = db.query(KeywordSuggestion).filter(
            KeywordSuggestion.id == suggestion_id
        ).first()

        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        return {
            "id": suggestion.id,
            "keyword_en": suggestion.keyword_en,
            "keyword_th": suggestion.keyword_th,
            "category": suggestion.category,
            "reason": suggestion.reason,
            "status": suggestion.status,
            "votes": suggestion.votes,
            "created_at": suggestion.created_at.isoformat(),
            "updated_at": suggestion.updated_at.isoformat() if suggestion.updated_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving suggestion {suggestion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving suggestion: {str(e)}")


@router.post("/{suggestion_id}/vote")
async def vote_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db)
):
    """
    Vote for a keyword suggestion.

    Args:
        suggestion_id: Suggestion ID
        db: Database session

    Returns:
        dict: Updated suggestion
    """
    try:
        suggestion = db.query(KeywordSuggestion).filter(
            KeywordSuggestion.id == suggestion_id
        ).first()

        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        # Increment vote count
        suggestion.votes += 1
        db.commit()
        db.refresh(suggestion)

        return {
            "success": True,
            "suggestion": {
                "id": suggestion.id,
                "keyword_en": suggestion.keyword_en,
                "votes": suggestion.votes
            },
            "message": "Vote recorded successfully!"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voting for suggestion {suggestion_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error recording vote: {str(e)}")
