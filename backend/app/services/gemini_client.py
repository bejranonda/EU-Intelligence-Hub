"""Google Gemini API client with rate limiting and error handling."""
import time
import logging
from typing import Optional, Dict, Any
from functools import wraps
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls_per_minute: int = 30):
        self.max_calls = max_calls_per_minute
        self.calls = []
        self.lock_until = 0

    def wait_if_needed(self):
        """Wait if rate limit is exceeded."""
        now = time.time()

        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]

        # Check if we've exceeded rate limit
        if len(self.calls) >= self.max_calls:
            wait_time = 60 - (now - self.calls[0])
            if wait_time > 0:
                logger.warning(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                self.calls = []

        self.calls.append(now)


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.rate_limiter = RateLimiter(
            max_calls_per_minute=settings.gemini_rate_limit_per_minute
        )
        logger.info("Gemini API client initialized")

    def _make_request(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Make a request to Gemini API with rate limiting and error handling.

        Args:
            prompt: The prompt to send to Gemini
            **kwargs: Additional arguments for generate_content

        Returns:
            Generated text or None if error
        """
        try:
            # Apply rate limiting
            self.rate_limiter.wait_if_needed()

            # Make API call
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', 0.7),
                    top_p=kwargs.get('top_p', 0.95),
                    top_k=kwargs.get('top_k', 40),
                    max_output_tokens=kwargs.get('max_output_tokens', 2048),
                ),
            )

            if response and response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini API")
                return None

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            return None

    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Optional[str]:
        """
        Generate text using Gemini.

        Args:
            prompt: The prompt text
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text or None
        """
        return self._make_request(
            prompt,
            temperature=temperature,
            max_output_tokens=max_tokens
        )

    def generate_structured_output(
        self,
        prompt: str,
        temperature: float = 0.3
    ) -> Optional[str]:
        """
        Generate structured output (JSON) using Gemini.

        Lower temperature for more consistent formatting.

        Args:
            prompt: The prompt text (should request JSON output)
            temperature: Sampling temperature

        Returns:
            Generated JSON string or None
        """
        return self._make_request(
            prompt,
            temperature=temperature,
            max_output_tokens=2048
        )

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.3
    ) -> Optional[Dict[str, Any]]:
        """
        Generate and parse JSON output using Gemini.

        Args:
            prompt: The prompt text (should request JSON output)
            temperature: Sampling temperature

        Returns:
            Parsed JSON dict or None if error
        """
        import json

        response = self._make_request(
            prompt,
            temperature=temperature,
            max_output_tokens=2048
        )

        if not response:
            return None

        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.debug(f"Response was: {response}")
            return None


# Global client instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create the global Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            raise last_exception
        return wrapper
    return decorator
