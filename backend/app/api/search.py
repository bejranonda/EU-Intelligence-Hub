"""Search API endpoints for articles and semantic similarity."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Article, Keyword, KeywordArticle
from app.services.embeddings import get_embedding_generator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/articles")
async def search_articles(
    q: Optional[str] = Query(None, description="Full text query"),
    keyword_id: Optional[int] = Query(None, description="Filter by keyword ID"),
    source: Optional[str] = Query(None, description="Filter by article source"),
    language: Optional[str] = Query(None, description="Filter by language code"),
    start_date: Optional[str] = Query(None, description="ISO 8601 start date"),
    end_date: Optional[str] = Query(None, description="ISO 8601 end date"),
    sentiment_min: Optional[float] = Query(None, ge=-1.0, le=1.0, description="Minimum sentiment"),
    sentiment_max: Optional[float] = Query(None, ge=-1.0, le=1.0, description="Maximum sentiment"),
    sort_by: str = Query(
        "date_desc",
        description="Sort order: date_desc, date_asc, sentiment_desc, sentiment_asc, relevance",
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Search stored articles with rich filtering support."""

    try:
        query_builder = db.query(Article)

        if keyword_id:
            query_builder = query_builder.join(KeywordArticle, KeywordArticle.article_id == Article.id)
            query_builder = query_builder.filter(KeywordArticle.keyword_id == keyword_id)

        if q:
            pattern = f"%{q}%"
            query_builder = query_builder.filter(
                or_(
                    Article.title.ilike(pattern),
                    Article.summary.ilike(pattern),
                    Article.full_text.ilike(pattern),
                )
            )

        if source:
            query_builder = query_builder.filter(func.lower(Article.source) == source.lower())

        if language:
            query_builder = query_builder.filter(func.lower(Article.language) == language.lower())

        if start_date:
            start_dt = _parse_iso_date(start_date, "start_date")
            query_builder = query_builder.filter(Article.published_date >= start_dt)

        if end_date:
            end_dt = _parse_iso_date(end_date, "end_date")
            query_builder = query_builder.filter(Article.published_date <= end_dt)

        if sentiment_min is not None:
            query_builder = query_builder.filter(Article.sentiment_overall >= sentiment_min)

        if sentiment_max is not None:
            query_builder = query_builder.filter(Article.sentiment_overall <= sentiment_max)

        total = query_builder.count()

        order_clause = _resolve_article_sort(sort_by, q)
        query_builder = query_builder.order_by(*order_clause)

        offset = (page - 1) * page_size
        articles = query_builder.offset(offset).limit(page_size).all()

        results = [
            _serialize_article_payload(
                article=article,
                keywords=_article_keywords(db, article.id),
                similarity=None,
            )
            for article in articles
        ]

        total_pages = (total + page_size - 1) // page_size if total else 0

        return {
            "results": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
            "filters": {
                "q": q,
                "keyword_id": keyword_id,
                "source": source,
                "language": language,
                "start_date": start_date,
                "end_date": end_date,
                "sentiment_min": sentiment_min,
                "sentiment_max": sentiment_max,
                "sort_by": sort_by,
            },
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error searching articles")
        raise HTTPException(status_code=500, detail="Error searching articles") from exc


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    min_similarity: float = Query(0.5, ge=0.0, le=1.0, description="Minimum similarity score"),
    keyword_id: Optional[int] = Query(None, description="Filter by associated keyword ID"),
    source: Optional[str] = Query(None, description="Filter by source"),
    language: Optional[str] = Query(None, description="Filter by language"),
    start_date: Optional[str] = Query(None, description="ISO 8601 start date"),
    end_date: Optional[str] = Query(None, description="ISO 8601 end date"),
    sort_by: str = Query(
        "relevance",
        description="Sort order: relevance, date_desc, date_asc, sentiment_desc, sentiment_asc",
    ),
    db: Session = Depends(get_db),
):
    """Perform semantic similarity search using embeddings."""

    try:
        embedding_service = get_embedding_generator()
        query_embedding = embedding_service.generate_embedding(q)

        query_builder = db.query(Article).filter(Article.embedding is not None)

        if keyword_id:
            query_builder = query_builder.join(KeywordArticle, KeywordArticle.article_id == Article.id)
            query_builder = query_builder.filter(KeywordArticle.keyword_id == keyword_id)

        if source:
            query_builder = query_builder.filter(func.lower(Article.source) == source.lower())

        if language:
            query_builder = query_builder.filter(func.lower(Article.language) == language.lower())

        if start_date:
            start_dt = _parse_iso_date(start_date, "start_date")
            query_builder = query_builder.filter(Article.published_date >= start_dt)

        if end_date:
            end_dt = _parse_iso_date(end_date, "end_date")
            query_builder = query_builder.filter(Article.published_date <= end_dt)

        articles = query_builder.all()

        if not articles:
            return {
                "query": q,
                "results": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": 0,
                    "total_pages": 0,
                },
                "filters": _build_semantic_filter_payload(
                    keyword_id,
                    source,
                    language,
                    start_date,
                    end_date,
                    sort_by,
                    min_similarity,
                ),
            }

        scored: List[Tuple[Article, float]] = []
        for article in articles:
            similarity = embedding_service.compute_similarity(query_embedding, article.embedding)
            if similarity >= min_similarity:
                scored.append((article, similarity))

        scored = _sort_semantic_results(scored, sort_by)

        total = len(scored)
        total_pages = (total + page_size - 1) // page_size if total else 0
        offset = (page - 1) * page_size
        page_items = scored[offset : offset + page_size]

        results = [
            _serialize_article_payload(
                article=item[0],
                keywords=_article_keywords(db, item[0].id),
                similarity=item[1],
            )
            for item in page_items
        ]

        return {
            "query": q,
            "results": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
            "filters": _build_semantic_filter_payload(
                keyword_id,
                source,
                language,
                start_date,
                end_date,
                sort_by,
                min_similarity,
            ),
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error performing semantic search")
        raise HTTPException(status_code=500, detail="Error performing search") from exc


@router.get("/similar/{article_id}")
async def find_similar_articles(
    article_id: int,
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    min_similarity: float = Query(0.6, ge=0.0, le=1.0, description="Minimum similarity score"),
    db: Session = Depends(get_db),
):
    """Find articles similar to a given article by embedding similarity."""

    try:
        source_article = db.query(Article).filter(Article.id == article_id).first()

        if not source_article:
            raise HTTPException(status_code=404, detail="Article not found")

        if not source_article.embedding:
            raise HTTPException(status_code=400, detail="Article has no embedding")

        embedding_service = get_embedding_generator()

        articles = (
            db.query(Article)
            .filter(Article.id != article_id, Article.embedding is not None)
            .all()
        )

        scored: List[Tuple[Article, float]] = []
        for article in articles:
            similarity = embedding_service.compute_similarity(
                source_article.embedding,
                article.embedding,
            )
            if similarity >= min_similarity:
                scored.append((article, similarity))

        scored.sort(key=lambda pair: pair[1], reverse=True)
        scored = scored[:limit]

        results = [
            _serialize_article_payload(
                article=item[0],
                keywords=_article_keywords(db, item[0].id),
                similarity=item[1],
            )
            for item in scored
        ]

        return {
            "source_article_id": article_id,
            "source_title": source_article.title,
            "results": results,
            "total": len(results),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error finding similar articles")
        raise HTTPException(status_code=500, detail="Error finding similar articles") from exc


def _parse_iso_date(value: str, field: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field}: expected ISO 8601 format") from exc


def _resolve_article_sort(sort_by: str, query_text: Optional[str]) -> Tuple:
    if sort_by == "date_asc":
        return (Article.published_date.asc(), Article.id.asc())
    if sort_by == "sentiment_desc":
        return (Article.sentiment_overall.desc(), Article.published_date.desc())
    if sort_by == "sentiment_asc":
        return (Article.sentiment_overall.asc(), Article.published_date.desc())
    if sort_by == "relevance" and query_text:
        pattern = f"%{query_text}%"
        relevance_case = case(
            (Article.title.ilike(pattern), 3),
            (Article.summary.ilike(pattern), 2),
            else_=1,
        )
        return (relevance_case.desc(), Article.published_date.desc())
    return (Article.published_date.desc(), Article.id.desc())


def _sort_semantic_results(results: List[Tuple[Article, float]], sort_by: str) -> List[Tuple[Article, float]]:
    if sort_by == "date_desc":
        return sorted(results, key=lambda pair: pair[0].published_date or datetime.min, reverse=True)
    if sort_by == "date_asc":
        return sorted(results, key=lambda pair: pair[0].published_date or datetime.min)
    if sort_by == "sentiment_desc":
        return sorted(results, key=lambda pair: pair[0].sentiment_overall or -1.0, reverse=True)
    if sort_by == "sentiment_asc":
        return sorted(results, key=lambda pair: pair[0].sentiment_overall or 1.0)
    return sorted(results, key=lambda pair: pair[1], reverse=True)


def _build_semantic_filter_payload(
    keyword_id: Optional[int],
    source: Optional[str],
    language: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    sort_by: str,
    min_similarity: float,
) -> Dict[str, Optional[str]]:
    return {
        "keyword_id": keyword_id,
        "source": source,
        "language": language,
        "start_date": start_date,
        "end_date": end_date,
        "sort_by": sort_by,
        "min_similarity": min_similarity,
    }


def _article_keywords(db: Session, article_id: int) -> List[str]:
    keywords = (
        db.query(Keyword)
        .join(KeywordArticle, Keyword.id == KeywordArticle.keyword_id)
        .filter(KeywordArticle.article_id == article_id)
        .order_by(Keyword.keyword_en.asc())
        .limit(5)
        .all()
    )
    return [kw.keyword_en for kw in keywords]


def _serialize_article_payload(
    article: Article,
    keywords: List[str],
    similarity: Optional[float],
) -> Dict[str, Optional[str]]:
    return {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "source": article.source,
        "source_url": article.source_url,
        "published_date": article.published_date.isoformat() if article.published_date else None,
        "similarity_score": round(similarity, 4) if similarity is not None else None,
        "sentiment": {
            "overall": article.sentiment_overall,
            "classification": article.sentiment_classification,
        },
        "language": article.language,
        "keywords": keywords,
    }
