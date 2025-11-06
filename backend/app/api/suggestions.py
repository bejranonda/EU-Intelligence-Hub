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

    keyword_en: str = Field(
        ..., min_length=2, max_length=100, description="Keyword in English"
    )
    keyword_th: Optional[str] = Field(
        None, max_length=100, description="Keyword in Thai"
    )
    keyword_de: Optional[str] = Field(
        None, max_length=100, description="Keyword in German"
    )
    keyword_fr: Optional[str] = Field(
        None, max_length=100, description="Keyword in French"
    )
    keyword_es: Optional[str] = Field(
        None, max_length=100, description="Keyword in Spanish"
    )
    keyword_it: Optional[str] = Field(
        None, max_length=100, description="Keyword in Italian"
    )
    keyword_pl: Optional[str] = Field(
        None, max_length=100, description="Keyword in Polish"
    )
    keyword_sv: Optional[str] = Field(
        None, max_length=100, description="Keyword in Swedish"
    )
    keyword_nl: Optional[str] = Field(
        None, max_length=100, description="Keyword in Dutch"
    )
    category: Optional[str] = Field("general", max_length=50, description="Category")
    reason: Optional[str] = Field(
        None, max_length=500, description="Reason for suggestion"
    )
    contact_email: Optional[str] = Field(
        None, max_length=100, description="Contact email"
    )


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
    suggestion: SuggestionCreate, db: Session = Depends(get_db)
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
        # Validate required field
        if not suggestion.keyword_en or not suggestion.keyword_en.strip():
            raise HTTPException(status_code=400, detail="Keyword (English) is required")

        # Normalize keyword for comparison
        normalized_keyword = suggestion.keyword_en.strip().lower()

        # Check if similar suggestion already exists
        try:
            existing = (
                db.query(KeywordSuggestion)
                .filter(KeywordSuggestion.keyword_en.ilike(normalized_keyword))
                .first()
            )

            if existing:
                # Increment vote count for existing suggestion
                existing.votes += 1
                db.commit()
                db.refresh(existing)

                logger.info(
                    f"Vote recorded for suggestion: {existing.keyword_en} (now {existing.votes} votes)"
                )

                return {
                    "success": True,
                    "suggestion": {
                        "id": existing.id,
                        "keyword_en": existing.keyword_en,
                        "keyword_th": existing.keyword_th,
                        "category": existing.category,
                        "status": existing.status,
                        "votes": existing.votes,
                        "created_at": existing.created_at.isoformat(),
                    },
                    "message": "Similar suggestion already exists. Vote count increased!",
                }
        except Exception as db_error:
            logger.error(f"Database error checking for existing suggestion: {db_error}")
            db.rollback()
            raise HTTPException(
                status_code=500, detail="Error checking for existing suggestions"
            )

        # Create new suggestion
        try:
            new_suggestion = KeywordSuggestion(
                keyword_en=suggestion.keyword_en.strip(),
                keyword_th=suggestion.keyword_th.strip()
                if suggestion.keyword_th
                else None,
                keyword_de=suggestion.keyword_de.strip()
                if suggestion.keyword_de
                else None,
                keyword_fr=suggestion.keyword_fr.strip()
                if suggestion.keyword_fr
                else None,
                keyword_es=suggestion.keyword_es.strip()
                if suggestion.keyword_es
                else None,
                keyword_it=suggestion.keyword_it.strip()
                if suggestion.keyword_it
                else None,
                keyword_pl=suggestion.keyword_pl.strip()
                if suggestion.keyword_pl
                else None,
                keyword_sv=suggestion.keyword_sv.strip()
                if suggestion.keyword_sv
                else None,
                keyword_nl=suggestion.keyword_nl.strip()
                if suggestion.keyword_nl
                else None,
                category=suggestion.category.strip()
                if suggestion.category
                else "general",
                reason=suggestion.reason.strip() if suggestion.reason else None,
                contact_email=suggestion.contact_email.strip()
                if suggestion.contact_email
                else None,
                status="pending",
                votes=1,
            )

            db.add(new_suggestion)
            db.commit()
            db.refresh(new_suggestion)

            logger.info(
                f"New suggestion created: {new_suggestion.keyword_en} (ID: {new_suggestion.id})"
            )

            return {
                "success": True,
                "suggestion": {
                    "id": new_suggestion.id,
                    "keyword_en": new_suggestion.keyword_en,
                    "keyword_th": new_suggestion.keyword_th,
                    "keyword_de": new_suggestion.keyword_de,
                    "keyword_fr": new_suggestion.keyword_fr,
                    "keyword_es": new_suggestion.keyword_es,
                    "keyword_it": new_suggestion.keyword_it,
                    "keyword_pl": new_suggestion.keyword_pl,
                    "keyword_sv": new_suggestion.keyword_sv,
                    "keyword_nl": new_suggestion.keyword_nl,
                    "category": new_suggestion.category,
                    "status": new_suggestion.status,
                    "votes": new_suggestion.votes,
                    "created_at": new_suggestion.created_at.isoformat(),
                },
                "message": "Thank you for your suggestion! It will be reviewed by our team.",
            }
        except Exception as create_error:
            logger.error(
                f"Error creating new suggestion: {create_error}", exc_info=True
            )
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error creating suggestion. Please try again later.",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_suggestion: {e}", exc_info=True)
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your suggestion",
        )


@router.get("/")
async def get_suggestions(
    status: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)
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
        suggestions = (
            query.order_by(
                KeywordSuggestion.votes.desc(), KeywordSuggestion.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        results = []
        for suggestion in suggestions:
            results.append(
                {
                    "id": suggestion.id,
                    "keyword_en": suggestion.keyword_en,
                    "keyword_th": suggestion.keyword_th,
                    "keyword_de": suggestion.keyword_de,
                    "keyword_fr": suggestion.keyword_fr,
                    "keyword_es": suggestion.keyword_es,
                    "keyword_it": suggestion.keyword_it,
                    "keyword_pl": suggestion.keyword_pl,
                    "keyword_sv": suggestion.keyword_sv,
                    "keyword_nl": suggestion.keyword_nl,
                    "category": suggestion.category,
                    "status": suggestion.status,
                    "votes": suggestion.votes,
                    "created_at": suggestion.created_at.isoformat(),
                }
            )

        return {"suggestions": results, "total": len(results), "status_filter": status}

    except Exception as e:
        logger.error(f"Error retrieving suggestions: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving suggestions: {str(e)}"
        )


@router.get("/{suggestion_id}")
async def get_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    """
    Get a specific suggestion by ID.

    Args:
        suggestion_id: Suggestion ID
        db: Database session

    Returns:
        dict: Suggestion details
    """
    try:
        suggestion = (
            db.query(KeywordSuggestion)
            .filter(KeywordSuggestion.id == suggestion_id)
            .first()
        )

        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        return {
            "id": suggestion.id,
            "keyword_en": suggestion.keyword_en,
            "keyword_th": suggestion.keyword_th,
            "keyword_de": suggestion.keyword_de,
            "keyword_fr": suggestion.keyword_fr,
            "keyword_es": suggestion.keyword_es,
            "keyword_it": suggestion.keyword_it,
            "keyword_pl": suggestion.keyword_pl,
            "keyword_sv": suggestion.keyword_sv,
            "keyword_nl": suggestion.keyword_nl,
            "category": suggestion.category,
            "reason": suggestion.reason,
            "status": suggestion.status,
            "votes": suggestion.votes,
            "created_at": suggestion.created_at.isoformat(),
            "updated_at": suggestion.updated_at.isoformat()
            if suggestion.updated_at
            else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving suggestion {suggestion_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving suggestion: {str(e)}"
        )


@router.post("/{suggestion_id}/vote")
async def vote_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    """
    Vote for a keyword suggestion.

    Args:
        suggestion_id: Suggestion ID
        db: Database session

    Returns:
        dict: Updated suggestion
    """
    try:
        suggestion = (
            db.query(KeywordSuggestion)
            .filter(KeywordSuggestion.id == suggestion_id)
            .first()
        )

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
                "votes": suggestion.votes,
            },
            "message": "Vote recorded successfully!",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voting for suggestion {suggestion_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error recording vote: {str(e)}")
