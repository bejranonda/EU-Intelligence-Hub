"""
Keyword extraction and classification service.

Uses:
1. spaCy for Named Entity Recognition (NER)
2. Gemini for fact/opinion classification
3. Gemini for keyword relationship extraction
"""

import json
import logging
from typing import List, Dict, Optional, Set
from collections import Counter

try:  # pragma: no cover - spaCy is optional during tests
    import spacy
except Exception:  # pragma: no cover
    spacy = None  # type: ignore

from app.services.gemini_client import get_gemini_client, retry_on_failure

logger = logging.getLogger(__name__)

# Load spaCy model (will be downloaded in Docker container)
if spacy is not None:
    try:
        nlp = spacy.load("en_core_web_sm")
        logger.info("spaCy model loaded successfully")
    except OSError:
        logger.warning(
            "spaCy model not found. Run: python -m spacy download en_core_web_sm"
        )
        nlp = None
else:  # pragma: no cover - spaCy not installed
    logger.warning("spaCy library unavailable; entity extraction disabled")
    nlp = None


class KeywordExtractor:
    """Extract keywords and classify article type."""

    def __init__(self):
        self.nlp = nlp
        self.gemini = get_gemini_client()

        # Common stopwords to filter out
        self.stopwords = {
            "thailand",
            "country",
            "government",
            "people",
            "years",
            "year",
            "said",
            "says",
            "according",
            "report",
            "reports",
            "news",
        }

    def extract_entities_spacy(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using spaCy NER.

        Args:
            text: Article text

        Returns:
            Dictionary with entity categories
        """
        if not self.nlp:
            logger.error("spaCy model not loaded")
            return {"people": [], "organizations": [], "locations": [], "other": []}

        try:
            doc = self.nlp(text[:100000])  # Limit text length for performance

            entities = {"people": [], "organizations": [], "locations": [], "other": []}

            for ent in doc.ents:
                text_lower = ent.text.lower().strip()

                # Skip stopwords and short entities
                if text_lower in self.stopwords or len(text_lower) < 3:
                    continue

                if ent.label_ == "PERSON":
                    entities["people"].append(ent.text)
                elif ent.label_ in ["ORG", "NORP"]:
                    entities["organizations"].append(ent.text)
                elif ent.label_ in ["GPE", "LOC"]:
                    entities["locations"].append(ent.text)
                else:
                    entities["other"].append(ent.text)

            # Remove duplicates while preserving order
            for key in entities:
                seen = set()
                unique_list = []
                for item in entities[key]:
                    if item not in seen:
                        seen.add(item)
                        unique_list.append(item)
                entities[key] = unique_list[:10]  # Limit to top 10

            return entities

        except Exception as e:
            logger.error(f"spaCy entity extraction failed: {str(e)}")
            return {"people": [], "organizations": [], "locations": [], "other": []}

    def extract_noun_chunks(self, text: str) -> List[str]:
        """
        Extract important noun chunks as potential keywords.

        Args:
            text: Article text

        Returns:
            List of noun chunks
        """
        if not self.nlp:
            return []

        try:
            doc = self.nlp(text[:50000])
            chunks = []

            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()

                # Filter criteria
                if (
                    len(chunk_text.split()) <= 4  # Not too long
                    and len(chunk_text) >= 5  # Not too short
                    and chunk_text not in self.stopwords
                ):
                    chunks.append(chunk.text)

            # Count frequency and return top ones
            chunk_counts = Counter(chunks)
            return [chunk for chunk, count in chunk_counts.most_common(15)]

        except Exception as e:
            logger.error(f"Noun chunk extraction failed: {str(e)}")
            return []

    @retry_on_failure(max_retries=2, delay=2.0)
    def extract_keywords_gemini(self, title: str, text: str) -> Optional[Dict]:
        """
        Use Gemini to extract primary keywords and relationships.

        Args:
            title: Article title
            text: Article text (will be truncated)

        Returns:
            Dictionary with keywords and relationships
        """
        # Truncate text
        max_chars = 6000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        prompt = f"""Analyze this article and extract structured information:

Article Title: {title}
Article Text: {text}

Extract:
1. Primary keywords (3-5 most important terms about Thailand or the main topic)
   - Focus on concrete nouns, not general words
   - Include specific topics, sectors, events

2. Named entities (people, organizations, locations)
   - People: Names of individuals mentioned
   - Organizations: Companies, institutions, government bodies
   - Locations: Cities, regions, countries (besides Thailand)

3. Key relationships: Which keywords are causally or thematically connected?
   - Format: {{keyword1: "...", keyword2: "...", type: "related/causal/parent-child"}}

Return as JSON:
{{
  "keywords": [list of 3-5 primary keyword strings],
  "entities": {{
    "people": [list of names],
    "organizations": [list of organizations],
    "locations": [list of places]
  }},
  "relationships": [
    {{
      "keyword1": "...",
      "keyword2": "...",
      "type": "related|causal|parent-child",
      "description": "brief explanation"
    }}
  ]
}}

Return ONLY the JSON, no additional text."""

        try:
            response = self.gemini.generate_structured_output(prompt, temperature=0.2)

            if not response:
                return None

            # Clean response
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()

            data = json.loads(clean_response)
            return data

        except Exception as e:
            logger.error(f"Gemini keyword extraction failed: {str(e)}")
            return None

    @retry_on_failure(max_retries=2, delay=2.0)
    def classify_fact_opinion(self, title: str, text: str) -> Optional[Dict]:
        """
        Classify article as fact-based or opinion-based using Gemini.

        Args:
            title: Article title
            text: Article text (will be truncated)

        Returns:
            Classification dictionary
        """
        # Truncate text
        max_chars = 5000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        prompt = f"""Classify this article: Is it primarily FACT-BASED or OPINION-BASED?

Article Title: {title}
Article Text: {text}

Classification criteria:

**FACT-BASED**:
- Verifiable claims with evidence
- Neutral language, objective reporting
- Quotes from sources, statistics, data
- No value judgments or predictions

**OPINION-BASED**:
- Subjective analysis, editorial commentary
- Value judgments, prescriptive statements
- Predictions about future, speculation
- Author's perspective or interpretation

**MIXED**: Contains both factual reporting and opinion/analysis

Analyze and classify:
1. Dominant type: fact, opinion, or mixed
2. Confidence: 0.0 (uncertain) to 1.0 (very certain)
3. Reasoning: 2-3 sentence explanation

Return as JSON:
{{
  "classification": "fact|opinion|mixed",
  "confidence": float between 0 and 1,
  "reasoning": "explanation of classification",
  "fact_percentage": int (0-100),
  "opinion_percentage": int (0-100)
}}

Return ONLY the JSON, no additional text."""

        try:
            response = self.gemini.generate_structured_output(prompt, temperature=0.2)

            if not response:
                return None

            # Clean response
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()

            data = json.loads(clean_response)
            return data

        except Exception as e:
            logger.error(f"Gemini classification failed: {str(e)}")
            return None

    def extract_all(self, title: str, text: str, use_gemini: bool = True) -> Dict:
        """
        Extract all information from article.

        Combines spaCy NER with Gemini extraction.

        Args:
            title: Article title
            text: Article text
            use_gemini: Whether to use Gemini (slower but better)

        Returns:
            Complete extraction results
        """
        results = {
            "keywords": [],
            "entities": {"people": [], "organizations": [], "locations": []},
            "relationships": [],
            "classification": "mixed",
            "classification_confidence": 0.5,
            "method": "hybrid",
        }

        # Get spaCy entities
        spacy_entities = self.extract_entities_spacy(text)
        results["entities"] = spacy_entities

        # Get noun chunks as backup keywords
        noun_chunks = self.extract_noun_chunks(text)

        # Try Gemini if enabled
        if use_gemini:
            gemini_keywords = self.extract_keywords_gemini(title, text)
            classification = self.classify_fact_opinion(title, text)

            if gemini_keywords:
                results["keywords"] = gemini_keywords.get("keywords", [])
                results["relationships"] = gemini_keywords.get("relationships", [])

                # Merge entities (Gemini may find additional ones)
                gemini_entities = gemini_keywords.get("entities", {})
                for key in ["people", "organizations", "locations"]:
                    existing = set(results["entities"].get(key, []))
                    additional = gemini_entities.get(key, [])
                    results["entities"][key] = list(existing.union(additional))[:10]

            if classification:
                results["classification"] = classification.get(
                    "classification", "mixed"
                )
                results["classification_confidence"] = classification.get(
                    "confidence", 0.5
                )
                results["classification_reasoning"] = classification.get("reasoning")

        # Fallback to noun chunks if no keywords extracted
        if not results["keywords"]:
            results["keywords"] = noun_chunks[:5]
            results["method"] = "spacy_only"

        return results


# Global extractor instance
_keyword_extractor: Optional[KeywordExtractor] = None


def get_keyword_extractor() -> KeywordExtractor:
    """Get or create the global keyword extractor instance."""
    global _keyword_extractor
    if _keyword_extractor is None:
        _keyword_extractor = KeywordExtractor()
    return _keyword_extractor
