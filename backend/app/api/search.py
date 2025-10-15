"""Semantic search API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models.models import Article, Keyword, keyword_article_association
from app.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    min_similarity: float = Query(0.5, ge=0.0, le=1.0, description="Minimum similarity score"),
    db: Session = Depends(get_db)
):
    """
    Perform semantic search using vector similarity.

    This endpoint finds articles that are semantically similar to the query,
    not just exact keyword matches.

    Args:
        q: Search query text
        limit: Maximum number of results
        min_similarity: Minimum similarity score (0.0-1.0)
        db: Database session

    Returns:
        dict: Search results with similarity scores
    """
    try:
        # Initialize embedding service
        embedding_service = EmbeddingService()

        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(q)

        # Get all articles with embeddings
        articles = db.query(Article).filter(Article.embedding.isnot(None)).all()

        if not articles:
            return {
                "query": q,
                "results": [],
                "total": 0
            }

        # Calculate similarities
        article_similarities = []
        for article in articles:
            if article.embedding:
                similarity = embedding_service.compute_similarity(
                    query_embedding,
                    article.embedding
                )
                if similarity >= min_similarity:
                    article_similarities.append((article, similarity))

        # Sort by similarity descending
        article_similarities.sort(key=lambda x: x[1], reverse=True)

        # Limit results
        article_similarities = article_similarities[:limit]

        # Format results
        results = []
        for article, similarity in article_similarities:
            # Get associated keywords
            keywords = db.query(Keyword).join(
                keyword_article_association,
                Keyword.id == keyword_article_association.c.keyword_id
            ).filter(
                keyword_article_association.c.article_id == article.id
            ).all()

            results.append({
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "source": article.source,
                "source_url": article.source_url,
                "published_date": article.published_date.isoformat() if article.published_date else None,
                "similarity_score": round(similarity, 4),
                "sentiment": {
                    "overall": article.sentiment_overall,
                    "classification": article.sentiment_classification
                },
                "keywords": [kw.keyword_en for kw in keywords[:5]]
            })

        return {
            "query": q,
            "results": results,
            "total": len(results),
            "min_similarity": min_similarity
        }

    except Exception as e:
        logger.error(f"Error performing semantic search: {e}")
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


@router.get("/similar/{article_id}")
async def find_similar_articles(
    article_id: int,
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    min_similarity: float = Query(0.6, ge=0.0, le=1.0, description="Minimum similarity score"),
    db: Session = Depends(get_db)
):
    """
    Find articles similar to a given article.

    Uses vector embeddings to find semantically similar content.

    Args:
        article_id: Source article ID
        limit: Maximum number of results
        min_similarity: Minimum similarity score
        db: Database session

    Returns:
        dict: Similar articles with similarity scores
    """
    try:
        # Get source article
        source_article = db.query(Article).filter(Article.id == article_id).first()

        if not source_article:
            raise HTTPException(status_code=404, detail="Article not found")

        if not source_article.embedding:
            raise HTTPException(status_code=400, detail="Article has no embedding")

        # Initialize embedding service
        embedding_service = EmbeddingService()

        # Get all other articles with embeddings
        articles = db.query(Article).filter(
            Article.id != article_id,
            Article.embedding.isnot(None)
        ).all()

        # Calculate similarities
        article_similarities = []
        for article in articles:
            if article.embedding:
                similarity = embedding_service.compute_similarity(
                    source_article.embedding,
                    article.embedding
                )
                if similarity >= min_similarity:
                    article_similarities.append((article, similarity))

        # Sort by similarity descending
        article_similarities.sort(key=lambda x: x[1], reverse=True)

        # Limit results
        article_similarities = article_similarities[:limit]

        # Format results
        results = []
        for article, similarity in article_similarities:
            results.append({
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "source": article.source,
                "source_url": article.source_url,
                "published_date": article.published_date.isoformat() if article.published_date else None,
                "similarity_score": round(similarity, 4),
                "sentiment": {
                    "overall": article.sentiment_overall,
                    "classification": article.sentiment_classification
                }
            })

        return {
            "source_article_id": article_id,
            "source_title": source_article.title,
            "results": results,
            "total": len(results)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar articles: {e}")
        raise HTTPException(status_code=500, detail=f"Error finding similar articles: {str(e)}")
