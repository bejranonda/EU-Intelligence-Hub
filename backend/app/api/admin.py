"""Admin API endpoints for keyword management and source configuration."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models.models import (
    Keyword,
    KeywordEvaluation,
    KeywordSuggestion,
    NewsSource,
    SourceIngestionHistory,
)
from app.services.keyword_approval import keyword_approval_service

logger = logging.getLogger(__name__)

router = APIRouter()


class SourcePayload(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    enabled: Optional[bool] = None
    language: Optional[str] = None
    country: Optional[str] = None
    priority: Optional[int] = None
    parser: Optional[str] = None
    tags: Optional[List[str]] = None


def _serialize_source(source: NewsSource) -> Dict[str, Any]:
    return {
        "id": source.id,
        "name": source.name,
        "base_url": source.base_url,
        "enabled": source.enabled,
        "language": source.language,
        "country": source.country,
        "priority": source.priority,
        "parser": source.parser,
        "tags": source.tags or [],
        "created_at": source.created_at.isoformat() if source.created_at else None,
        "updated_at": source.updated_at.isoformat() if source.updated_at else None,
    }


@router.get("/sources")
async def list_news_sources(
    only_enabled: bool = Query(False, description="Return only enabled sources"),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    query = db.query(NewsSource)
    if only_enabled:
        query = query.filter(NewsSource.enabled.is_(True))

    sources = query.order_by(
        NewsSource.priority.desc(), NewsSource.created_at.asc()
    ).all()
    return {"sources": [_serialize_source(source) for source in sources]}


@router.post("/sources")
async def create_news_source(
    payload: SourcePayload,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    if not payload.name or not payload.base_url:
        raise HTTPException(status_code=400, detail="name and base_url are required")

    existing = (
        db.query(NewsSource)
        .filter(func.lower(NewsSource.name) == payload.name.lower())
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Source with this name already exists"
        )

    source = NewsSource(
        name=payload.name,
        base_url=payload.base_url,
        enabled=payload.enabled if payload.enabled is not None else True,
        language=payload.language or "en",
        country=payload.country,
        priority=payload.priority or 0,
        parser=payload.parser,
        tags=payload.tags or [],
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return {"source": _serialize_source(source)}


@router.patch("/sources/{source_id}")
async def update_news_source(
    source_id: int,
    payload: SourcePayload,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "name" in update_data:
        duplicate = (
            db.query(NewsSource)
            .filter(
                func.lower(NewsSource.name) == update_data["name"].lower(),
                NewsSource.id != source_id,
            )
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=400, detail="Another source already uses this name"
            )

    for field, value in update_data.items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return {"source": _serialize_source(source)}


@router.post("/sources/{source_id}/toggle")
async def toggle_news_source(
    source_id: int,
    enabled: bool = Query(..., description="Desired enabled state"),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    source.enabled = enabled
    db.commit()
    db.refresh(source)
    return {"source": _serialize_source(source)}


@router.get("/sources/{source_id}/ingestion")
async def get_source_ingestion_history(
    source_id: int,
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    history = (
        db.query(SourceIngestionHistory)
        .filter(SourceIngestionHistory.source_id == source_id)
        .order_by(SourceIngestionHistory.last_run_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "source": _serialize_source(source),
        "history": [
            {
                "id": entry.id,
                "last_run_at": (
                    entry.last_run_at.isoformat() if entry.last_run_at else None
                ),
                "articles_ingested": entry.articles_ingested,
                "success": entry.success,
                "notes": entry.notes,
            }
            for entry in history
        ],
    }


@router.post("/keywords/suggestions/{suggestion_id}/process")
async def process_suggestion_manually(
    suggestion_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Manually trigger AI processing of a keyword suggestion."""

    try:
        result = await keyword_approval_service.process_suggestion(
            suggestion_id=suggestion_id, db=db
        )

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return {"success": True, "result": result}

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error processing suggestion %s: %s", suggestion_id, exc)
        raise HTTPException(
            status_code=500, detail=f"Error processing suggestion: {exc}"
        ) from exc


@router.get("/keywords/suggestions/pending")
async def get_pending_suggestions(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Get all pending keyword suggestions ordered by votes."""

    try:
        suggestions = (
            db.query(KeywordSuggestion)
            .filter(KeywordSuggestion.status == "pending")
            .order_by(
                KeywordSuggestion.votes.desc(), KeywordSuggestion.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        if not suggestions:
            return {"pending_suggestions": [], "total": 0}

        suggestion_ids = [suggestion.id for suggestion in suggestions]
        ranked_subquery = (
            db.query(
                KeywordEvaluation.id,
                KeywordEvaluation.suggestion_id,
                KeywordEvaluation.searchability_score,
                KeywordEvaluation.significance_score,
                KeywordEvaluation.specificity,
                KeywordEvaluation.decision,
                KeywordEvaluation.reasoning,
                KeywordEvaluation.evaluation_metadata,
                KeywordEvaluation.created_at,
                func.row_number()
                .over(
                    partition_by=KeywordEvaluation.suggestion_id,
                    order_by=KeywordEvaluation.created_at.desc(),
                )
                .label("rank"),
            )
            .filter(KeywordEvaluation.suggestion_id.in_(suggestion_ids))
            .subquery()
        )

        latest_rows = (
            db.query(ranked_subquery).filter(ranked_subquery.c.rank == 1).all()
        )

        latest_by_suggestion: Dict[int, KeywordEvaluation] = {
            row.suggestion_id: row for row in latest_rows  # type: ignore[attr-defined]
        }

        results = [
            _serialize_suggestion_with_evaluation(
                suggestion,
                latest_by_suggestion.get(suggestion.id),
            )
            for suggestion in suggestions
        ]

        return {"pending_suggestions": results, "total": len(results)}

    except Exception as exc:
        logger.error("Error getting pending suggestions: %s", exc)
        raise HTTPException(
            status_code=500, detail=f"Error retrieving suggestions: {exc}"
        ) from exc


@router.post("/keywords/suggestions/{suggestion_id}/approve")
async def approve_suggestion_manually(
    suggestion_id: int,
    trigger_search: bool = Query(True, description="Trigger immediate news search"),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Manually approve a suggestion and create keyword."""

    try:
        suggestion = (
            db.query(KeywordSuggestion)
            .filter(KeywordSuggestion.id == suggestion_id)
            .first()
        )

        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        translations = await keyword_approval_service.translate_keyword(
            suggestion.keyword_en,
            ["th", "de", "fr", "es", "it", "pl", "sv", "nl"],
        )

        keyword_th = suggestion.keyword_th or translations.get("th")
        keyword_de = suggestion.keyword_de or translations.get("de")
        keyword_fr = suggestion.keyword_fr or translations.get("fr")
        keyword_es = suggestion.keyword_es or translations.get("es")
        keyword_it = suggestion.keyword_it or translations.get("it")
        keyword_pl = suggestion.keyword_pl or translations.get("pl")
        keyword_sv = suggestion.keyword_sv or translations.get("sv")
        keyword_nl = suggestion.keyword_nl or translations.get("nl")

        from app.services.embeddings import EmbeddingGenerator

        embedding_service = EmbeddingGenerator()

        new_keyword = Keyword(
            keyword_en=suggestion.keyword_en,
            keyword_th=keyword_th,
            keyword_de=keyword_de,
            keyword_fr=keyword_fr,
            keyword_es=keyword_es,
            keyword_it=keyword_it,
            keyword_pl=keyword_pl,
            keyword_sv=keyword_sv,
            keyword_nl=keyword_nl,
            category=suggestion.category or "general",
            embedding=embedding_service.generate_embedding(suggestion.keyword_en),
        )
        db.add(new_keyword)

        suggestion.status = "approved"

        db.commit()
        db.refresh(new_keyword)

        logger.info(
            "Manually approved keyword '%s' (ID: %s)",
            suggestion.keyword_en,
            new_keyword.id,
        )

        response: Dict[str, Any] = {
            "success": True,
            "keyword": {
                "id": new_keyword.id,
                "keyword_en": new_keyword.keyword_en,
                "keyword_th": new_keyword.keyword_th,
                "keyword_de": new_keyword.keyword_de,
                "keyword_fr": new_keyword.keyword_fr,
                "keyword_es": new_keyword.keyword_es,
                "keyword_it": new_keyword.keyword_it,
                "keyword_pl": new_keyword.keyword_pl,
                "keyword_sv": new_keyword.keyword_sv,
                "keyword_nl": new_keyword.keyword_nl,
                "category": new_keyword.category,
            },
            "message": f"Keyword '{suggestion.keyword_en}' approved and created",
        }

        if trigger_search:
            try:
                from app.tasks.keyword_search import search_keyword_immediately

                search_task = search_keyword_immediately.delay(new_keyword.id)
                response["search_triggered"] = True
                response["search_task_id"] = search_task.id
                response["message"] += " and immediate search triggered"
                logger.info(
                    "Triggered immediate search for keyword ID: %s", new_keyword.id
                )
            except Exception as exc:
                logger.error("Failed to trigger immediate search: %s", exc)
                response["search_triggered"] = False
                response["search_error"] = str(exc)

        return response

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error approving suggestion %s: %s", suggestion_id, exc)
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error approving suggestion: {exc}"
        ) from exc


@router.post("/keywords/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: int,
    reason: Optional[str] = Query(None, description="Reason for rejection"),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Manually reject a keyword suggestion."""

    try:
        suggestion = (
            db.query(KeywordSuggestion)
            .filter(KeywordSuggestion.id == suggestion_id)
            .first()
        )

        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")

        suggestion.status = "rejected"
        db.commit()

        logger.info(
            "Rejected suggestion '%s': %s",
            suggestion.keyword_en,
            reason or "No reason provided",
        )

        return {
            "success": True,
            "message": f"Suggestion '{suggestion.keyword_en}' rejected",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error rejecting suggestion %s: %s", suggestion_id, exc)
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error rejecting suggestion: {exc}"
        ) from exc


@router.get("/keywords/suggestions/stats")
async def get_suggestion_stats(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Get statistics about keyword suggestions."""

    try:
        total = db.query(func.count(KeywordSuggestion.id)).scalar()
        pending = (
            db.query(func.count(KeywordSuggestion.id))
            .filter(KeywordSuggestion.status == "pending")
            .scalar()
        )
        approved = (
            db.query(func.count(KeywordSuggestion.id))
            .filter(KeywordSuggestion.status == "approved")
            .scalar()
        )
        rejected = (
            db.query(func.count(KeywordSuggestion.id))
            .filter(KeywordSuggestion.status == "rejected")
            .scalar()
        )
        merged = (
            db.query(func.count(KeywordSuggestion.id))
            .filter(KeywordSuggestion.status == "merged")
            .scalar()
        )

        top_suggestions = (
            db.query(KeywordSuggestion)
            .filter(KeywordSuggestion.status == "pending")
            .order_by(KeywordSuggestion.votes.desc())
            .limit(10)
            .all()
        )

        return {
            "total_suggestions": total,
            "by_status": {
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "merged": merged,
            },
            "top_pending": [
                {
                    "id": suggestion.id,
                    "keyword_en": suggestion.keyword_en,
                    "votes": suggestion.votes,
                }
                for suggestion in top_suggestions
            ],
        }

    except Exception as exc:
        logger.error("Error getting suggestion stats: %s", exc)
        raise HTTPException(
            status_code=500, detail=f"Error retrieving stats: {exc}"
        ) from exc


def _serialize_suggestion_with_evaluation(
    suggestion: KeywordSuggestion,
    evaluation: Optional[KeywordEvaluation],
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "id": suggestion.id,
        "keyword_en": suggestion.keyword_en,
        "keyword_th": suggestion.keyword_th,
        "keyword_de": getattr(suggestion, "keyword_de", None),
        "keyword_fr": getattr(suggestion, "keyword_fr", None),
        "keyword_es": getattr(suggestion, "keyword_es", None),
        "keyword_it": getattr(suggestion, "keyword_it", None),
        "keyword_pl": getattr(suggestion, "keyword_pl", None),
        "keyword_sv": getattr(suggestion, "keyword_sv", None),
        "keyword_nl": getattr(suggestion, "keyword_nl", None),
        "category": suggestion.category,
        "reason": suggestion.reason,
        "votes": suggestion.votes,
        "status": suggestion.status,
        "created_at": (
            suggestion.created_at.isoformat() if suggestion.created_at else None
        ),
    }

    if evaluation:
        created_at = getattr(evaluation, "created_at", None)
        metadata = getattr(evaluation, "evaluation_metadata", {}) or {}

        payload["latest_evaluation"] = {
            "searchability_score": getattr(evaluation, "searchability_score", None),
            "significance_score": getattr(evaluation, "significance_score", None),
            "specificity": getattr(evaluation, "specificity", None),
            "decision": getattr(evaluation, "decision", None),
            "reasoning": getattr(evaluation, "reasoning", None),
            "created_at": created_at.isoformat() if created_at else None,
            "metadata": metadata,
        }
    else:
        payload["latest_evaluation"] = None

    return payload
