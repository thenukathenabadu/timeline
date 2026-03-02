from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawArticle:
    """Normalised article data returned by every scraper."""
    source_id: str
    url: str
    title: str
    published_at: datetime
    summary: str | None = None
    # Raw text for AI processing (not stored long-term)
    full_text: str | None = None
    # Extra metadata scrapers may populate
    extra: dict = field(default_factory=dict)


class BaseScraper(ABC):
    """
    Abstract base for all content scrapers.

    Each source = one file that subclasses this.
    """

    #: Must match the `id` column in the `sources` table
    source_id: str
    display_name: str
    home_url: str

    @abstractmethod
    async def fetch_latest(self) -> list[RawArticle]:
        """Fetch articles published since the last scrape.

        Returns a list of RawArticle objects — may be empty if nothing new.
        """
        ...
