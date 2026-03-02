from abc import ABC, abstractmethod
from datetime import datetime


class EmbeddingProvider(ABC):
    """Converts text → embedding vectors + zero-shot classification."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""
        ...

    @abstractmethod
    def classify(self, text: str, labels: list[str]) -> str:
        """Return the label whose embedding is most similar to `text`."""
        ...


class ReasoningProvider(ABC):
    """Uses an LLM for tasks that need language understanding."""

    @abstractmethod
    async def extract_event_date(
        self,
        title: str,
        summary: str,
        published_at: datetime,
    ) -> datetime | None:
        """
        Try to extract the real-world event date from article content.
        Returns None if extraction fails or the model is unavailable.
        """
        ...
