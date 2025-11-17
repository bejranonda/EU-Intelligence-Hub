"""Keywords API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from typing import Optional
import logging

from app.database import get_db
from app.models.models import Keyword, Article, KeywordRelation, KeywordArticle

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def search_keywords(
    q: Optional[str] = Query(None, description="Search query"),
    language: Optional[str] = Query("en", description="Language code (en/th)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Search keywords with pagination.

    Args:
        q: Optional search query to filter keywords
        language: Language code for filtering (en/th)
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)
        db: Database session

    Returns:
        dict: Paginated keyword results with metadata
    """
    try:
        # Base query
        query = db.query(Keyword)

        # Apply search filter if provided
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                or_(
                    Keyword.keyword_en.ilike(search_term),
                    (
                        Keyword.keyword_th.ilike(search_term)
                        if language == "th"
                        else False
                    ),
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        keywords = (
            query.order_by(desc(Keyword.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # Format results
        results = []
        for keyword in keywords:
            # Get article count
            article_count = (
                db.query(func.count(KeywordArticle.article_id))
                .filter(KeywordArticle.keyword_id == keyword.id)
                .scalar()
            )

            results.append(
                {
                    "id": keyword.id,
                    "keyword_en": keyword.keyword_en,
                    "keyword_th": keyword.keyword_th,
                    "category": keyword.category,
                    "article_count": article_count,
                    "created_at": (
                        keyword.created_at.isoformat() if keyword.created_at else None
                    ),
                }
            )

        return {
            "results": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
            },
        }

    except Exception as e:
        logger.error(f"Error searching keywords: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error searching keywords: {str(e)}"
        )


@router.get("/{keyword_id}")
async def get_keyword(
    keyword_id: int,
    language: str = Query("en", description="Language code (en/th)"),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific keyword.

    Args:
        keyword_id: Keyword ID
        language: Language code for response
        db: Database session

    Returns:
        dict: Detailed keyword information
    """
    try:
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()

        if not keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")

        # Get article count
        article_count = (
            db.query(func.count(KeywordArticle.article_id))
            .filter(KeywordArticle.keyword_id == keyword.id)
            .scalar()
        )

        # Get related keywords count
        related_count = (
            db.query(func.count())
            .filter(
                or_(
                    KeywordRelation.keyword1_id == keyword.id,
                    KeywordRelation.keyword2_id == keyword.id,
                )
            )
            .scalar()
        )

        return {
            "id": keyword.id,
            "keyword": keyword.keyword_th if language == "th" else keyword.keyword_en,
            "keyword_en": keyword.keyword_en,
            "keyword_th": keyword.keyword_th,
            "category": keyword.category,
            "article_count": article_count,
            "related_keywords_count": related_count,
            "created_at": (
                keyword.created_at.isoformat() if keyword.created_at else None
            ),
            "updated_at": (
                keyword.updated_at.isoformat() if keyword.updated_at else None
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting keyword {keyword_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving keyword: {str(e)}"
        )


@router.get("/{keyword_id}/articles")
async def get_keyword_articles(
    keyword_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("date", description="Sort by: date, sentiment"),
    db: Session = Depends(get_db),
):
    """
    Get articles associated with a keyword.

    Args:
        keyword_id: Keyword ID
        page: Page number
        page_size: Items per page
        sort_by: Sorting criterion (date or sentiment)
        db: Database session

    Returns:
        dict: Paginated articles with metadata
    """
    try:
        # Check if keyword exists
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")

        # Base query - join articles with keyword association
        query = (
            db.query(Article)
            .join(KeywordArticle, Article.id == KeywordArticle.article_id)
            .filter(KeywordArticle.keyword_id == keyword_id)
        )

        # Apply sorting
        if sort_by == "sentiment":
            query = query.order_by(desc(Article.sentiment_overall))
        else:  # default to date
            query = query.order_by(desc(Article.published_date))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        articles = query.offset(offset).limit(page_size).all()

        # Format results
        results = []
        for article in articles:
            results.append(
                {
                    "id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "source": article.source,
                    "source_url": article.source_url,
                    "published_date": (
                        article.published_date.isoformat()
                        if article.published_date
                        else None
                    ),
                    "sentiment": {
                        "overall": article.sentiment_overall,
                        "confidence": article.sentiment_confidence,
                        "classification": article.sentiment_classification,
                        "subjectivity": article.sentiment_subjectivity,
                    },
                    "classification": article.classification,
                }
            )

        return {
            "keyword_id": keyword_id,
            "keyword_en": keyword.keyword_en,
            "results": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting articles for keyword {keyword_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving articles: {str(e)}"
        )


@router.get("/{keyword_id}/relations")
async def get_keyword_relations(
    keyword_id: int,
    min_strength: float = Query(
        0.3, ge=0.0, le=1.0, description="Minimum relationship strength"
    ),
    db: Session = Depends(get_db),
):
    """
    Get keyword relationships for mind map visualization.

    Args:
        keyword_id: Keyword ID
        min_strength: Minimum relationship strength (0.0-1.0)
        db: Database session

    Returns:
        dict: Nodes and edges for mind map visualization
    """
    try:
        # Check if keyword exists
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            raise HTTPException(status_code=404, detail="Keyword not found")

        # Get all relationships where this keyword is involved
        relations = (
            db.query(KeywordRelation)
            .filter(
                or_(
                    KeywordRelation.keyword1_id == keyword_id,
                    KeywordRelation.keyword2_id == keyword_id,
                ),
                KeywordRelation.strength_score >= min_strength,
            )
            .all()
        )

        # Build nodes and edges
        nodes = {}
        edges = []

        # Add central node
        nodes[keyword.id] = {
            "id": str(keyword.id),
            "label": keyword.keyword_en,
            "type": "central",
            "category": keyword.category,
        }

        # Process relationships
        for relation in relations:
            # Determine the related keyword
            if relation.keyword1_id == keyword_id:
                related_id = relation.keyword2_id
                related_keyword = (
                    db.query(Keyword).filter(Keyword.id == related_id).first()
                )
            else:
                related_id = relation.keyword1_id
                related_keyword = (
                    db.query(Keyword).filter(Keyword.id == related_id).first()
                )

            if not related_keyword:
                continue

            # Add node if not exists
            if related_id not in nodes:
                nodes[related_id] = {
                    "id": str(related_id),
                    "label": related_keyword.keyword_en,
                    "type": "related",
                    "category": related_keyword.category,
                }

            # Add edge
            edges.append(
                {
                    "source": str(keyword_id),
                    "target": str(related_id),
                    "strength": relation.strength_score,
                    "relationship_type": relation.relation_type,
                }
            )

        return {
            "keyword_id": keyword_id,
            "keyword_en": keyword.keyword_en,
            "nodes": list(nodes.values()),
            "edges": edges,
            "total_relations": len(edges),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting relations for keyword {keyword_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving relationships: {str(e)}"
        )
