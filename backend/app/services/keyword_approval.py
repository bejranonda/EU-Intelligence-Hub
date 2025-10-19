"""AI-powered keyword approval and management service (Gemini only)."""

import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.models import Keyword, KeywordEvaluation, KeywordSuggestion
from app.services.embeddings import EmbeddingGenerator
from app.services.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)


class KeywordApprovalService:
    """Gemini-backed keyword evaluation and approval workflow."""

    def __init__(self) -> None:
        self.embedding_service = EmbeddingGenerator()
        self.gemini_client = get_gemini_client()

    async def evaluate_keyword_significance(
        self,
        keyword: str,
        category: str = "general",
        reason: Optional[str] = None,
    ) -> Dict:
        """Score keyword viability for EU intelligence monitoring."""

        prompt = f"""
Evaluate the following keyword for a European Union intelligence news monitoring platform.

Keyword: "{keyword}"
Category: {category}
{f'User context: {reason}' if reason else ''}

Assess the keyword and respond in JSON with:
{{
  "searchability_score": <integer 1-10>,
  "significance_score": <integer 1-10>,
  "specificity": "broad" | "narrow" | "just_right",
  "reasoning": "Two-sentence summary explaining the scores",
  "suggested_alternatives": ["optional better phrasing", ...],
  "notes": "Additional short insight if needed"
}}

Scoring guidance:
- searchability_score reflects how likely European-focused news sources will return relevant, recent results.
- significance_score reflects geopolitical/strategic value to EU monitoring (trade, policy, security, economy, etc.).
- specificity describes whether the keyword is overly broad, overly narrow, or appropriate for targeted monitoring.

Ensure scores are integers within 1-10. If no alternatives, return an empty array.
"""

        try:
            response = await self.gemini_client.generate_json(prompt)

            if not isinstance(response, dict):
                logger.warning("Invalid Gemini evaluation response for '%s'", keyword)
                return self._default_evaluation()

            searchability = self._coerce_score(response.get("searchability_score"))
            significance = self._coerce_score(response.get("significance_score"))
            specificity = response.get("specificity", "unknown") or "unknown"
            reasoning = response.get("reasoning", "AI evaluation completed")
            alternatives = response.get("suggested_alternatives") or []
            notes = response.get("notes", "")

            result = {
                "searchability_score": searchability,
                "significance_score": significance,
                "specificity": specificity,
                "reasoning": reasoning,
                "suggested_alternatives": alternatives,
                "notes": notes,
                "raw": response,
            }

            logger.info(
                "Keyword '%s' evaluated: searchability=%s significance=%s specificity=%s",
                keyword,
                searchability,
                significance,
                specificity,
            )

            return result

        except Exception as exc:  # pragma: no cover
            logger.error("Gemini evaluation failed for '%s': %s", keyword, exc)
            return self._default_evaluation()

    async def find_similar_keywords(
        self,
        keyword: str,
        db: Session,
        similarity_threshold: float = 0.85,
    ) -> List[Dict]:
        """Locate existing keywords with high embedding similarity."""

        try:
            candidate_embedding = self.embedding_service.generate_embedding(keyword)
            existing_keywords = db.query(Keyword).filter(Keyword.embedding.isnot(None)).all()

            similar: List[Dict] = []
            for existing in existing_keywords:
                if not existing.embedding:
                    continue

                similarity = self.embedding_service.compute_similarity(
                    candidate_embedding,
                    existing.embedding,
                )

                if similarity >= similarity_threshold:
                    similar.append(
                        {
                            "id": existing.id,
                            "keyword_en": existing.keyword_en,
                            "keyword_th": existing.keyword_th,
                            "category": existing.category,
                            "similarity": similarity,
                        }
                    )

            similar.sort(key=lambda item: item["similarity"], reverse=True)
            return similar

        except Exception as exc:  # pragma: no cover
            logger.error("Failed to compute similar keywords for '%s': %s", keyword, exc)
            return []

    async def suggest_keyword_merge(
        self,
        keyword: str,
        similar_keywords: List[str],
    ) -> Dict:
        """Ask Gemini whether the keyword should merge with similar ones."""

        if not similar_keywords:
            return self._default_merge_result()

        prompt = f"""
Analyze these keywords for a news monitoring system:

New Suggested Keyword: "{keyword}"
Existing Similar Keywords: {', '.join([f'"{kw}"' for kw in similar_keywords])}

Determine:
1. Should the new keyword be MERGED with an existing one? (Yes/No)
2. If yes, which keyword and what final merged phrasing should be used?
3. Provide a concise reasoning (max 2 sentences).

Respond in JSON:
{{
  "should_merge": true/false,
  "merge_with": "existing keyword" | null,
  "merged_keyword": "final merged phrasing" | null,
  "reasoning": "explanation"
}}
"""

        try:
            response = await self.gemini_client.generate_json(prompt)
            if not isinstance(response, dict):
                return self._default_merge_result()

            return {
                "should_merge": response.get("should_merge", False),
                "merge_with": response.get("merge_with"),
                "merged_keyword": response.get("merged_keyword"),
                "reasoning": response.get("reasoning", "Merge analysis completed"),
            }

        except Exception as exc:  # pragma: no cover
            logger.error("Merge analysis failed for '%s': %s", keyword, exc)
            return self._default_merge_result()

    async def process_suggestion(self, suggestion_id: int, db: Session) -> Dict:
        """Evaluate and act on a keyword suggestion."""

        suggestion = (
            db.query(KeywordSuggestion)
            .filter(KeywordSuggestion.id == suggestion_id)
            .first()
        )

        if not suggestion:
            return {"error": "Suggestion not found"}

        logger.info("Processing suggestion %s (%s)", suggestion_id, suggestion.keyword_en)

        evaluation = await self.evaluate_keyword_significance(
            suggestion.keyword_en,
            category=suggestion.category,
            reason=suggestion.reason,
        )

        result: Dict = {
            "suggestion_id": suggestion_id,
            "keyword": suggestion.keyword_en,
            "evaluation": evaluation,
            "action": None,
            "reasoning": [],
        }

        created_keyword: Optional[Keyword] = None
        decision = "pending"

        if (
            evaluation["searchability_score"] >= 7
            and evaluation["significance_score"] >= 6
        ):
            created_keyword = await self._approve_keyword(db, suggestion)
            decision = "approved"
            result["action"] = "approved"
            result["keyword_id"] = created_keyword.id if created_keyword else None
            result["reasoning"].append(evaluation["reasoning"])
        else:
            merge_info = await self._attempt_merge(db, suggestion)
            if merge_info:
                created_keyword, merge_reason = merge_info
                decision = "merged"
                result["action"] = "merged"
                result["keyword_id"] = created_keyword.id if created_keyword else None
                result["reasoning"].append(merge_reason)
            else:
                suggestion.status = "pending_review"
                db.commit()
                decision = "pending_review"
                result["action"] = "pending_review"
                result["reasoning"].append(
                    evaluation["reasoning"] + " — queued for manual review"
                )

        self._record_evaluation(
            db=db,
            suggestion=suggestion,
            keyword=created_keyword,
            evaluation=evaluation,
            decision=decision,
        )

        if created_keyword:
            self._trigger_immediate_search(created_keyword.id)

        return result

    async def translate_keyword(
        self,
        keyword_en: str,
        target_languages: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Translate keywords via Gemini."""

        if target_languages is None:
            target_languages = [
                "th",
                "de",
                "fr",
                "es",
                "it",
                "pl",
                "sv",
                "nl",
            ]

        language_names = {
            "th": "Thai",
            "de": "German",
            "fr": "French",
            "es": "Spanish",
            "it": "Italian",
            "pl": "Polish",
            "sv": "Swedish",
            "nl": "Dutch",
        }

        languages_str = ", ".join(language_names.get(code, code) for code in target_languages)

        prompt = f"""
Translate this keyword for a multilingual European news monitoring system.

English Keyword: "{keyword_en}"
Target languages: {languages_str}

Respond in JSON with language codes as keys using concise terminology suitable for search queries.
"""

        try:
            response = await self.gemini_client.generate_json(prompt)
            if not isinstance(response, dict):
                logger.warning("Invalid translation response for '%s'", keyword_en)
                return {}

            translations: Dict[str, str] = {}
            for lang_code in target_languages:
                translated = response.get(lang_code)
                if translated:
                    translations[lang_code] = translated
                else:
                    logger.warning("Missing %s translation for '%s'", lang_code, keyword_en)

            return translations

        except Exception as exc:  # pragma: no cover
            logger.error("Translation failed for '%s': %s", keyword_en, exc)
            return {}

    def _coerce_score(self, value: Optional[float], default: int = 5) -> int:
        try:
            score = int(round(float(value)))
            return max(1, min(10, score))
        except (TypeError, ValueError):
            return default

    async def _approve_keyword(
        self,
        db: Session,
        suggestion: KeywordSuggestion,
    ) -> Keyword:
        suggestion.status = "approved"

        keyword_th = suggestion.keyword_th
        if not keyword_th:
            translations = await self.translate_keyword(suggestion.keyword_en, ["th"])
            keyword_th = translations.get("th")

        new_keyword = Keyword(
            keyword_en=suggestion.keyword_en.strip(),
            keyword_th=keyword_th,
            category=suggestion.category or "general",
            embedding=self.embedding_service.generate_embedding(suggestion.keyword_en),
        )

        db.add(new_keyword)
        db.commit()
        db.refresh(new_keyword)

        logger.info("Keyword '%s' approved (ID=%s)", new_keyword.keyword_en, new_keyword.id)
        return new_keyword

    async def _attempt_merge(
        self,
        db: Session,
        suggestion: KeywordSuggestion,
    ) -> Optional[Tuple[Keyword, str]]:
        pending_matches = (
            db.query(KeywordSuggestion)
            .filter(
                KeywordSuggestion.status == "pending",
                KeywordSuggestion.id != suggestion.id,
                and_(
                    KeywordSuggestion.keyword_en.ilike(f"%{suggestion.keyword_en}%"),
                    KeywordSuggestion.category == suggestion.category,
                ),
            )
            .all()
        )

        if not pending_matches:
            return None

        merge_prompt = await self.suggest_keyword_merge(
            suggestion.keyword_en,
            [match.keyword_en for match in pending_matches[:3]],
        )

        if not merge_prompt.get("should_merge"):
            return None

        merged_keyword_text = merge_prompt.get("merged_keyword") or suggestion.keyword_en

        keyword_th = suggestion.keyword_th
        if not keyword_th:
            translations = await self.translate_keyword(merged_keyword_text, ["th"])
            keyword_th = translations.get("th")

        merged_keyword = Keyword(
            keyword_en=merged_keyword_text,
            keyword_th=keyword_th,
            category=suggestion.category or "general",
            embedding=self.embedding_service.generate_embedding(merged_keyword_text),
        )

        db.add(merged_keyword)
        suggestion.status = "merged"

        for match in pending_matches:
            match.status = "merged"

        db.commit()
        db.refresh(merged_keyword)

        merge_reason = merge_prompt.get("reasoning", "Merged based on similarity")
        logger.info("Merged keyword '%s' into '%s'", suggestion.keyword_en, merged_keyword.keyword_en)

        return merged_keyword, merge_reason

    def _record_evaluation(
        self,
        db: Session,
        suggestion: KeywordSuggestion,
        keyword: Optional[Keyword],
        evaluation: Dict,
        decision: str,
    ) -> None:
        record = KeywordEvaluation(
            suggestion_id=suggestion.id,
            keyword_id=keyword.id if keyword else None,
            keyword_text=suggestion.keyword_en,
            searchability_score=evaluation.get("searchability_score"),
            significance_score=evaluation.get("significance_score"),
            specificity=evaluation.get("specificity"),
            decision=decision,
            reasoning=evaluation.get("reasoning"),
            evaluation_metadata=evaluation.get("raw"),
        )

        db.add(record)
        db.commit()

    def _trigger_immediate_search(self, keyword_id: int) -> None:
        try:
            from app.tasks.keyword_search import search_keyword_immediately

            search_task = search_keyword_immediately.delay(keyword_id)
            logger.info(
                "Immediate search queued for keyword %s (task=%s)", keyword_id, search_task.id
            )
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to trigger immediate search for keyword %s: %s", keyword_id, exc)

    def _default_evaluation(self) -> Dict:
        return {
            "searchability_score": 5,
            "significance_score": 5,
            "specificity": "unknown",
            "reasoning": "Unable to evaluate automatically",
            "suggested_alternatives": [],
            "notes": "",
            "raw": {},
        }

    def _default_merge_result(self) -> Dict:
        return {
            "should_merge": False,
            "merge_with": None,
            "merged_keyword": None,
            "reasoning": "Unable to analyze merge automatically",
        }


keyword_approval_service = KeywordApprovalService()
