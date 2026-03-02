"""
Embedding + classification via sentence-transformers (all-MiniLM-L6-v2).

This is Layer 1 of the AI pipeline:
  - Produces 384-dim embedding vectors used for pgvector similarity search
  - Zero-shot category classification via cosine similarity to label embeddings
  - No GPU required — runs on CPU in ~5 ms per article
"""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from ai.base import EmbeddingProvider
from config import settings

# One embedding per category — used for zero-shot classification
_CATEGORY_PHRASES: dict[str, list[str]] = {
    "politics":  ["politics government election president parliament democracy"],
    "war":       ["war military conflict armed forces battle attack bombing"],
    "finance":   ["economy finance stock market business investment GDP inflation"],
    "science":   ["science research discovery space technology innovation"],
    "nature":    ["earthquake flood hurricane wildfire climate disaster environment"],
    "sports":    ["sports football basketball olympics athlete tournament championship"],
    "health":    ["health medicine hospital disease pandemic vaccine treatment"],
    "crime":     ["crime arrest murder court trial conviction police"],
    "other":     ["news events world"],
}


class SentenceTransformerProvider(EmbeddingProvider):
    """Wraps sentence-transformers for embedding and classification."""

    def __init__(self):
        self._model: SentenceTransformer | None = None
        self._category_embeddings: dict[str, np.ndarray] | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    def _get_category_embeddings(self) -> dict[str, np.ndarray]:
        if self._category_embeddings is None:
            model = self._get_model()
            self._category_embeddings = {
                cat: model.encode(phrases, normalize_embeddings=True).mean(axis=0)
                for cat, phrases in _CATEGORY_PHRASES.items()
            }
        return self._category_embeddings

    # ── Public interface ──────────────────────────────────────────────────────

    def embed(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [v.tolist() for v in vectors]

    def classify(self, text: str, labels: list[str] | None = None) -> str:
        """
        If `labels` is None, classify into the built-in category set.
        Otherwise, cosine-similarity against the provided label strings.
        """
        model = self._get_model()
        text_vec = model.encode([text], normalize_embeddings=True)[0]

        if labels is None:
            cat_embs = self._get_category_embeddings()
            best = max(cat_embs, key=lambda c: float(np.dot(text_vec, cat_embs[c])))
            return best
        else:
            label_vecs = model.encode(labels, normalize_embeddings=True)
            scores = [float(np.dot(text_vec, lv)) for lv in label_vecs]
            return labels[int(np.argmax(scores))]
