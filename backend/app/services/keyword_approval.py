"""
AI-powered keyword approval and management system.

This service uses Gemini AI to intelligently:
1. Evaluate if a suggested keyword is significant enough to track
2. Merge similar keywords to avoid duplication
3. Group related keywords for better news discovery
"""
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.services.gemini_client import get_gemini_client
from app.services.embeddings import EmbeddingGenerator
from app.models.models import KeywordSuggestion, Keyword

logger = logging.getLogger(__name__)


class KeywordApprovalService:
    """Service for AI-powered keyword approval and management."""

    def __init__(self):
        self.embedding_service = EmbeddingGenerator()
        self.gemini_client = get_gemini_client()

    async def evaluate_keyword_significance(
        self,
        keyword: str,
        category: str = "general",
        reason: str = None
    ) -> Dict:
        """
        Use AI to evaluate if a keyword is significant enough to track.

        Args:
            keyword: The keyword to evaluate
            category: Category of the keyword
            reason: User's reason for suggesting (if provided)

        Returns:
            dict: {
                "is_significant": bool,
                "confidence": float (0-1),
                "reasoning": str,
                "searchability": str ("easy", "moderate", "difficult"),
                "suggested_alternatives": List[str],
                "news_potential": str ("high", "medium", "low")
            }
        """
        prompt = f"""Evaluate this keyword for a European news monitoring system that tracks media coverage:

Keyword: "{keyword}"
Category: {category}
{f'User Reason: {reason}' if reason else ''}

Analyze and provide:
1. Is this keyword SIGNIFICANT enough to track in European news? (Yes/No)
   - Consider: International relevance, news frequency, geopolitical importance

2. SEARCHABILITY: How easy is it to find news articles about this keyword?
   - "easy": Well-known entities (countries, major organizations, prominent figures)
   - "moderate": Specific topics, emerging trends, regional issues
   - "difficult": Very niche, unclear, too broad or too narrow

3. NEWS POTENTIAL: How frequently does this topic appear in European media?
   - "high": Daily coverage expected (major countries, ongoing issues)
   - "medium": Weekly coverage (specific topics, regional matters)
   - "low": Rare mentions (very niche topics)

4. If searchability is "moderate" or "difficult", suggest 2-3 ALTERNATIVE keywords that would:
   - Be more specific and easier to search
   - Or broader terms that encompass this keyword
   - Related terms that appear more frequently in news

5. REASONING: Brief explanation of your evaluation (2-3 sentences)

Respond in JSON format:
{{
    "is_significant": true/false,
    "confidence": 0.0-1.0,
    "searchability": "easy/moderate/difficult",
    "news_potential": "high/medium/low",
    "suggested_alternatives": ["keyword1", "keyword2", "keyword3"],
    "reasoning": "explanation here"
}}"""

        try:
            response = await self.gemini_client.generate_json(prompt)

            # Validate response
            if not isinstance(response, dict):
                logger.warning(f"Invalid response format for keyword: {keyword}")
                return self._default_evaluation()

            # Ensure all required fields
            result = {
                "is_significant": response.get("is_significant", False),
                "confidence": float(response.get("confidence", 0.5)),
                "searchability": response.get("searchability", "moderate"),
                "news_potential": response.get("news_potential", "medium"),
                "suggested_alternatives": response.get("suggested_alternatives", []),
                "reasoning": response.get("reasoning", "AI evaluation completed")
            }

            logger.info(f"Keyword evaluation for '{keyword}': significant={result['is_significant']}, "
                       f"searchability={result['searchability']}")

            return result

        except Exception as e:
            logger.error(f"Error evaluating keyword '{keyword}': {e}")
            return self._default_evaluation()

    async def find_similar_keywords(
        self,
        keyword: str,
        db: Session,
        similarity_threshold: float = 0.85
    ) -> List[Dict]:
        """
        Find existing keywords that are similar to the suggested one.

        Args:
            keyword: The keyword to compare
            db: Database session
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar keywords with similarity scores
        """
        try:
            # Generate embedding for the new keyword
            keyword_embedding = self.embedding_service.generate_embedding(keyword)

            # Get all existing keywords with embeddings
            existing_keywords = db.query(Keyword).filter(
                Keyword.embedding.isnot(None)
            ).all()

            similar_keywords = []
            for existing in existing_keywords:
                if existing.embedding:
                    similarity = self.embedding_service.compute_similarity(
                        keyword_embedding,
                        existing.embedding
                    )

                    if similarity >= similarity_threshold:
                        similar_keywords.append({
                            "id": existing.id,
                            "keyword_en": existing.keyword_en,
                            "keyword_th": existing.keyword_th,
                            "category": existing.category,
                            "similarity": similarity
                        })

            # Sort by similarity descending
            similar_keywords.sort(key=lambda x: x["similarity"], reverse=True)

            return similar_keywords

        except Exception as e:
            logger.error(f"Error finding similar keywords for '{keyword}': {e}")
            return []

    async def suggest_keyword_merge(
        self,
        keyword: str,
        similar_keywords: List[str]
    ) -> Dict:
        """
        Use AI to determine if keywords should be merged or kept separate.

        Args:
            keyword: The new keyword
            similar_keywords: List of similar existing keywords

        Returns:
            dict: {
                "should_merge": bool,
                "merge_with": str (keyword to merge with),
                "merged_keyword": str (suggested merged name),
                "reasoning": str
            }
        """
        if not similar_keywords:
            return {
                "should_merge": False,
                "merge_with": None,
                "merged_keyword": None,
                "reasoning": "No similar keywords found"
            }

        prompt = f"""Analyze these keywords for a news monitoring system:

New Suggested Keyword: "{keyword}"
Existing Similar Keywords: {', '.join([f'"{k}"' for k in similar_keywords])}

Determine:
1. Should the new keyword be MERGED with an existing one? (Yes/No)
   - Merge if they represent the same entity/concept
   - Keep separate if they are distinct despite similarity

2. If YES to merge:
   - Which existing keyword should it merge with?
   - What should be the final merged keyword name?

3. Brief reasoning (1-2 sentences)

Respond in JSON:
{{
    "should_merge": true/false,
    "merge_with": "existing keyword name or null",
    "merged_keyword": "final name or null",
    "reasoning": "explanation"
}}"""

        try:
            response = await self.gemini_client.generate_json(prompt)

            if not isinstance(response, dict):
                return self._default_merge_result()

            return {
                "should_merge": response.get("should_merge", False),
                "merge_with": response.get("merge_with"),
                "merged_keyword": response.get("merged_keyword"),
                "reasoning": response.get("reasoning", "Merge analysis completed")
            }

        except Exception as e:
            logger.error(f"Error analyzing keyword merge: {e}")
            return self._default_merge_result()

    async def process_suggestion(
        self,
        suggestion_id: int,
        db: Session
    ) -> Dict:
        """
        Complete AI-powered processing of a keyword suggestion.

        This is the main entry point that:
        1. Evaluates significance
        2. Checks for duplicates/similar keywords
        3. Determines if merge is needed
        4. Updates suggestion status

        Args:
            suggestion_id: ID of the KeywordSuggestion
            db: Database session

        Returns:
            dict: Processing result with decision and reasoning
        """
        # Get suggestion
        suggestion = db.query(KeywordSuggestion).filter(
            KeywordSuggestion.id == suggestion_id
        ).first()

        if not suggestion:
            return {"error": "Suggestion not found"}

        logger.info(f"Processing suggestion: {suggestion.keyword_en}")

        # Step 1: Evaluate significance
        evaluation = await self.evaluate_keyword_significance(
            keyword=suggestion.keyword_en,
            category=suggestion.category,
            reason=suggestion.reason
        )

        result = {
            "suggestion_id": suggestion_id,
            "keyword": suggestion.keyword_en,
            "evaluation": evaluation,
            "action": None,
            "reasoning": []
        }

        # Step 2: If not significant, reject
        if not evaluation["is_significant"] or evaluation["confidence"] < 0.6:
            suggestion.status = "rejected"
            db.commit()

            result["action"] = "rejected"
            result["reasoning"].append(f"Not significant enough: {evaluation['reasoning']}")

            if evaluation["suggested_alternatives"]:
                result["reasoning"].append(
                    f"Consider alternatives: {', '.join(evaluation['suggested_alternatives'][:3])}"
                )

            return result

        # Step 3: Check for similar existing keywords
        similar = await self.find_similar_keywords(
            keyword=suggestion.keyword_en,
            db=db,
            similarity_threshold=0.85
        )

        if similar:
            result["similar_keywords"] = similar[:3]  # Top 3

            # Step 4: Determine if merge is needed
            merge_analysis = await self.suggest_keyword_merge(
                keyword=suggestion.keyword_en,
                similar_keywords=[k["keyword_en"] for k in similar[:3]]
            )

            result["merge_analysis"] = merge_analysis

            if merge_analysis["should_merge"]:
                suggestion.status = "merged"
                result["action"] = "merged"
                result["reasoning"].append(
                    f"Merged with '{merge_analysis['merge_with']}': {merge_analysis['reasoning']}"
                )
                db.commit()
                return result

        # Step 5: If difficult to search, suggest alternatives
        if evaluation["searchability"] == "difficult":
            suggestion.status = "pending"
            result["action"] = "pending_alternatives"
            result["reasoning"].append(
                f"Difficult to search. Consider: {', '.join(evaluation['suggested_alternatives'][:3])}"
            )
            db.commit()
            return result

        # Step 6: Approve and create keyword
        suggestion.status = "approved"

        # Create new keyword
        new_keyword = Keyword(
            keyword_en=suggestion.keyword_en,
            keyword_th=suggestion.keyword_th,
            category=suggestion.category or "general",
            embedding=self.embedding_service.generate_embedding(suggestion.keyword_en)
        )
        db.add(new_keyword)
        db.commit()

        result["action"] = "approved"
        result["keyword_id"] = new_keyword.id
        result["reasoning"].append(
            f"Approved: {evaluation['reasoning']}"
        )

        logger.info(f"Keyword '{suggestion.keyword_en}' approved and created (ID: {new_keyword.id})")

        return result

    def _default_evaluation(self) -> Dict:
        """Return default evaluation when AI fails."""
        return {
            "is_significant": False,
            "confidence": 0.5,
            "searchability": "moderate",
            "news_potential": "medium",
            "suggested_alternatives": [],
            "reasoning": "Unable to evaluate automatically"
        }

    def _default_merge_result(self) -> Dict:
        """Return default merge result when AI fails."""
        return {
            "should_merge": False,
            "merge_with": None,
            "merged_keyword": None,
            "reasoning": "Unable to analyze merge automatically"
        }


# Global instance
keyword_approval_service = KeywordApprovalService()
