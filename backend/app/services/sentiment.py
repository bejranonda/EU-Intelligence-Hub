"""
Sentiment analysis service with multi-layered detection.

Implements:
1. VADER baseline sentiment scoring
2. Gemini-based nuanced opinion detection
3. Sentiment classification with confidence thresholds
4. Emotion breakdown calculation
"""
import json
import logging
from typing import Dict, Optional, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from app.services.gemini_client import get_gemini_client, retry_on_failure
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize VADER
vader_analyzer = SentimentIntensityAnalyzer()


class SentimentAnalyzer:
    """Multi-layered sentiment analysis for news articles."""

    def __init__(self):
        self.gemini = get_gemini_client()
        self.vader = vader_analyzer

    def analyze_sentiment_vader(self, text: str) -> Dict[str, float]:
        """
        Get baseline sentiment using VADER.

        Args:
            text: Article text to analyze

        Returns:
            Dictionary with sentiment scores
        """
        try:
            scores = self.vader.polarity_scores(text)
            return {
                "overall": scores["compound"],  # -1 to 1
                "positive": scores["pos"],
                "negative": scores["neg"],
                "neutral": scores["neu"],
                "confidence": abs(
                    scores["compound"]
                ),  # Use compound magnitude as confidence
            }
        except Exception as e:
            logger.error(f"VADER analysis failed: {str(e)}")
            return {
                "overall": 0.0,
                "positive": 0.33,
                "negative": 0.33,
                "neutral": 0.34,
                "confidence": 0.0,
            }

    @retry_on_failure(max_retries=2, delay=2.0)
    def analyze_sentiment_gemini(
        self, title: str, text: str, source_name: str
    ) -> Optional[Dict[str, any]]:
        """
        Get nuanced sentiment analysis using Gemini API.

        Args:
            title: Article title
            text: Article text (truncate if too long)
            source_name: Publication name

        Returns:
            Dictionary with detailed sentiment analysis or None
        """
        # Truncate text if too long (Gemini has token limits)
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        prompt = f"""Analyze the sentiment and opinion in this news article about Thailand.

Article Title: {title}
Article Text: {text}
Publication: {source_name}

Perform a detailed sentiment analysis:

1. **Overall Polarity**: Rate from -1.0 (very negative) to +1.0 (very positive)
   - Consider: word choice, framing, emphasis on problems vs. opportunities
   - Account for implicit bias (what's highlighted vs. omitted)

2. **Confidence**: Rate from 0.0 (uncertain) to 1.0 (very certain)
   - High confidence: Clear positive/negative language, consistent tone
   - Low confidence: Mixed signals, balanced reporting, ambiguous phrasing

3. **Subjectivity**: Rate from 0.0 (pure facts) to 1.0 (pure opinion)
   - Objective: Statistics, quotes, verifiable claims
   - Subjective: Editorial commentary, predictions, value judgments

4. **Emotion Breakdown**: Distribute 1.0 total across:
   - Positive emotions: admiration, optimism, celebration
   - Negative emotions: criticism, concern, alarm
   - Neutral: informative, balanced, matter-of-fact

5. **Key Opinion Indicators**: Extract specific phrases showing bias
   - Positive phrases: [list 2-3 examples if any]
   - Negative phrases: [list 2-3 examples if any]

6. **Contextual Factors**:
   - Is Thailand portrayed as victim, perpetrator, or neutral actor?
   - Are problems blamed on Thailand or external factors?
   - Does the article emphasize progress or decline?

Return as JSON:
{{
  "overall_polarity": float,
  "confidence": float,
  "subjectivity": float,
  "emotion_breakdown": {{
    "positive": float,
    "negative": float,
    "neutral": float
  }},
  "classification": "STRONGLY_POSITIVE|POSITIVE|NEUTRAL|NEGATIVE|STRONGLY_NEGATIVE",
  "key_phrases": {{
    "positive": [strings],
    "negative": [strings]
  }},
  "reasoning": "Brief explanation of the sentiment assessment (2-3 sentences)"
}}

Be nuanced: A factual article about economic challenges can be neutral despite negative content if presented objectively.
Return ONLY the JSON, no additional text."""

        try:
            response = self.gemini.generate_structured_output(prompt, temperature=0.2)

            if not response:
                logger.warning("Empty response from Gemini sentiment analysis")
                return None

            # Parse JSON response
            # Clean response (sometimes Gemini adds markdown formatting)
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()

            sentiment_data = json.loads(clean_response)

            # Validate structure
            required_keys = [
                "overall_polarity",
                "confidence",
                "subjectivity",
                "emotion_breakdown",
            ]
            if not all(key in sentiment_data for key in required_keys):
                logger.error(
                    f"Missing required keys in Gemini response: {sentiment_data.keys()}"
                )
                return None

            return sentiment_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {str(e)}")
            logger.error(f"Response was: {response[:200] if response else 'None'}")
            return None
        except Exception as e:
            logger.error(f"Gemini sentiment analysis failed: {str(e)}")
            return None

    def classify_sentiment(self, overall_polarity: float, confidence: float) -> str:
        """
        Classify sentiment into categories with confidence-adjusted thresholds.

        Args:
            overall_polarity: Sentiment score from -1.0 to 1.0
            confidence: Confidence score from 0.0 to 1.0

        Returns:
            Classification string
        """
        # Adjust thresholds based on confidence
        confidence_multiplier = max(
            confidence, 0.3
        )  # Minimum 0.3 to avoid extreme adjustments

        strong_threshold = 0.5 * confidence_multiplier
        moderate_threshold = 0.2 * confidence_multiplier

        if overall_polarity >= strong_threshold:
            return "STRONGLY_POSITIVE"
        elif overall_polarity >= moderate_threshold:
            return "POSITIVE"
        elif overall_polarity <= -strong_threshold:
            return "STRONGLY_NEGATIVE"
        elif overall_polarity <= -moderate_threshold:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    def analyze_article(
        self, title: str, text: str, source_name: str, use_gemini: bool = True
    ) -> Dict[str, any]:
        """
        Perform complete sentiment analysis on an article.

        Combines VADER baseline with optional Gemini enhancement.

        Args:
            title: Article title
            text: Article full text
            source_name: Publication name
            use_gemini: Whether to use Gemini (slower but more accurate)

        Returns:
            Complete sentiment analysis results
        """
        # Get VADER baseline
        vader_result = self.analyze_sentiment_vader(text)

        # Combine title and text for analysis
        full_text = f"{title}. {text}"

        # Try Gemini if enabled and configured
        gemini_result = None
        if use_gemini and settings.enable_gemini_sentiment:
            gemini_result = self.analyze_sentiment_gemini(title, text, source_name)

        # Use Gemini result if available, otherwise fall back to VADER
        if gemini_result:
            sentiment_overall = gemini_result["overall_polarity"]
            confidence = gemini_result["confidence"]
            subjectivity = gemini_result["subjectivity"]
            emotions = gemini_result["emotion_breakdown"]

            classification = gemini_result.get(
                "classification", self.classify_sentiment(sentiment_overall, confidence)
            )

            return {
                "sentiment_overall": sentiment_overall,
                "sentiment_confidence": confidence,
                "sentiment_subjectivity": subjectivity,
                "emotion_positive": emotions["positive"],
                "emotion_negative": emotions["negative"],
                "emotion_neutral": emotions["neutral"],
                "classification": classification,
                "method": "gemini",
                "vader_baseline": vader_result,
                "reasoning": gemini_result.get("reasoning"),
                "key_phrases": gemini_result.get("key_phrases"),
            }
        else:
            # Fallback to VADER
            logger.info("Using VADER baseline sentiment (Gemini unavailable)")
            sentiment_overall = vader_result["overall"]
            confidence = vader_result["confidence"]

            # Estimate subjectivity (VADER doesn't provide this)
            # If sentiment is strong (far from 0), it's likely more subjective
            subjectivity = abs(sentiment_overall) * 0.7 + 0.3

            classification = self.classify_sentiment(sentiment_overall, confidence)

            return {
                "sentiment_overall": sentiment_overall,
                "sentiment_confidence": confidence,
                "sentiment_subjectivity": subjectivity,
                "emotion_positive": vader_result["positive"],
                "emotion_negative": vader_result["negative"],
                "emotion_neutral": vader_result["neutral"],
                "classification": classification,
                "method": "vader",
                "vader_baseline": vader_result,
            }


# Global analyzer instance
_sentiment_analyzer: Optional[SentimentAnalyzer] = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or create the global sentiment analyzer instance."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
