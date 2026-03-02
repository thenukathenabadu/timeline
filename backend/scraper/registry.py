"""
Scraper registry — maps source_id strings to scraper instances.

Adding a new source:
  1. Create backend/scraper/sources/mysource.py with a class subclassing BaseScraper
  2. Import and register it here
"""

from scraper.base import BaseScraper
from scraper.sources.bbc import BBCScraper
from scraper.sources.reuters import ReutersScraper
from scraper.sources.ap import APScraper
from scraper.sources.guardian import GuardianScraper
from scraper.sources.aljazeera import AlJazeeraScraper

# source_id → scraper instance
_REGISTRY: dict[str, BaseScraper] = {
    s.source_id: s
    for s in [
        BBCScraper(),
        ReutersScraper(),
        APScraper(),
        GuardianScraper(),
        AlJazeeraScraper(),
    ]
}


def get_scraper(source_id: str) -> BaseScraper | None:
    return _REGISTRY.get(source_id)


def all_scrapers() -> list[BaseScraper]:
    return list(_REGISTRY.values())


def all_source_ids() -> list[str]:
    return list(_REGISTRY.keys())
