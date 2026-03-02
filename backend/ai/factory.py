"""
AI provider factory — returns the right provider based on config.

Switching models = change EMBEDDING_PROVIDER / REASONING_PROVIDER in .env.
No code changes needed.
"""

from __future__ import annotations

from functools import lru_cache

from ai.base import EmbeddingProvider, ReasoningProvider
from config import settings


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()
    if provider == "sentence_transformer":
        from ai.sentence_tf import SentenceTransformerProvider
        return SentenceTransformerProvider()
    raise ValueError(f"Unknown embedding provider: {provider}")


@lru_cache(maxsize=1)
def get_reasoning_provider() -> ReasoningProvider:
    provider = settings.reasoning_provider.lower()
    if provider == "ollama":
        from ai.ollama import OllamaProvider
        return OllamaProvider()
    raise ValueError(f"Unknown reasoning provider: {provider}")
