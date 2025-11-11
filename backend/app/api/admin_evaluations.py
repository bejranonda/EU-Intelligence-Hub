"""Admin endpoints for viewing keyword evaluation history."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models.models import KeywordEvaluation, KeywordSuggestion

router = APIRouter()


@router.get("/suggestions/{suggestion_id}/evaluations")
async def list_suggestion_evaluations(
    suggestion_id: int,
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Return evaluation history for a suggestion ordered by newest first."""

    suggestion = (
        db.query(KeywordSuggestion)
        .filter(KeywordSuggestion.id == suggestion_id)
        .first()
    )
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    evaluations = (
        db.query(KeywordEvaluation)
        .filter(KeywordEvaluation.suggestion_id == suggestion_id)
        .order_by(KeywordEvaluation.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "suggestion_id": suggestion_id,
        "evaluations": [
            {
                "searchability_score": evaluation.searchability_score,
                "significance_score": evaluation.significance_score,
                "specificity": evaluation.specificity,
                "decision": evaluation.decision,
                "reasoning": evaluation.reasoning,
                "created_at": (
                    evaluation.created_at.isoformat() if evaluation.created_at else None
                ),
            }
            for evaluation in evaluations
        ],
    }
