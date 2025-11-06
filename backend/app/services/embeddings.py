"""
Vector embedding generation using Sentence Transformers.

Used for semantic search in articles and keywords.
"""
import logging
import numpy as np
from typing import List, Optional

# Lazy import to avoid heavy dependency during lightweight unit tests.
try:  # pragma: no cover - tested via high level behaviour
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover

    class _FallbackSentenceTransformer:  # type: ignore
        def __init__(self, *_, **__):
            pass

        def encode(self, sentences, convert_to_numpy=True):
            import numpy as np

            if isinstance(sentences, str):
                sentences = [sentences]

            return np.zeros((len(sentences), 384), dtype=float)

    SentenceTransformer = _FallbackSentenceTransformer  # type: ignore

logger = logging.getLogger(__name__)

# Model will generate 384-dimensional embeddings (matches our database schema)
MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingGenerator:
    """Generate vector embeddings for semantic search."""

    def __init__(self):
        self.embedding_dim = 384
        try:
            self.model = SentenceTransformer(MODEL_NAME)
            if (
                hasattr(self.model, "encode")
                and self.model.__class__.__name__ != "_FallbackSentenceTransformer"
            ):
                logger.info(f"Loaded embedding model: {MODEL_NAME}")
            else:
                logger.warning(
                    "Using fallback embedding model; embeddings will be zero vectors"
                )
        except Exception as e:  # pragma: no cover - depends on external resource
            logger.error(f"Failed to load embedding model: {str(e)}")
            self.model = None

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats (384-dimensional vector) or None
        """
        if not self.model:
            logger.error("Embedding model not loaded")
            return None

        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for embedding")
            return None

        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            # Convert to list for JSON serialization
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return None

    def generate_embeddings_batch(
        self, texts: List[str]
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts (more efficient).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (same order as input)
        """
        if not self.model:
            logger.error("Embedding model not loaded")
            return [None] * len(texts)

        if not texts:
            return []

        try:
            # Filter out empty texts
            valid_indices = []
            valid_texts = []
            for i, text in enumerate(texts):
                if text and len(text.strip()) > 0:
                    valid_indices.append(i)
                    valid_texts.append(text)

            if not valid_texts:
                return [None] * len(texts)

            # Generate embeddings in batch
            embeddings = self.model.encode(valid_texts, convert_to_numpy=True)

            # Map back to original positions
            results = [None] * len(texts)
            for i, embedding in zip(valid_indices, embeddings):
                results[i] = embedding.tolist()

            return results

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            return [None] * len(texts)

    def compute_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score from -1 to 1 (higher = more similar)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Cosine similarity
            similarity = np.dot(vec1, vec2) / (
                np.linalg.norm(vec1) * np.linalg.norm(vec2)
            )
            return float(similarity)

        except Exception as e:
            logger.error(f"Failed to compute similarity: {str(e)}")
            return 0.0

    def find_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 10,
    ) -> List[tuple]:
        """
        Find most similar embeddings to query.

        Args:
            query_embedding: Query vector
            candidate_embeddings: List of candidate vectors
            top_k: Number of top results to return

        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        try:
            similarities = []
            for i, candidate in enumerate(candidate_embeddings):
                if candidate:  # Skip None embeddings
                    sim = self.compute_similarity(query_embedding, candidate)
                    similarities.append((i, sim))

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Failed to find similar embeddings: {str(e)}")
            return []


# Global generator instance
_embedding_generator: Optional[EmbeddingGenerator] = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create the global embedding generator instance."""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator
