"""Generic RSS / Atom feed scraper.

All RSS-based sources subclass RSSscraper and only need to supply
`source_id`, `display_name`, `home_url`, and `feed_urls`.
"""

from datetime import datetime, timezone

import feedparser
import httpx

from scraper.base import BaseScraper, RawArticle


class RSSScraper(BaseScraper):
    """Fetches articles from one or more RSS / Atom feed URLs."""

    #: Subclasses set this to a list of feed URLs to poll
    feed_urls: list[str] = []

    async def fetch_latest(self) -> list[RawArticle]:
        articles: list[RawArticle] = []
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            for feed_url in self.feed_urls:
                try:
                    resp = await client.get(feed_url)
                    resp.raise_for_status()
                    feed = feedparser.parse(resp.text)
                    for entry in feed.entries:
                        article = self._parse_entry(entry)
                        if article:
                            articles.append(article)
                except Exception:
                    # One feed failing should not abort the others
                    continue
        return articles

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _parse_entry(self, entry) -> RawArticle | None:
        url = entry.get("link", "").strip()
        title = entry.get("title", "").strip()
        if not url or not title:
            return None

        published_at = self._parse_date(entry)
        if published_at is None:
            return None

        summary = self._extract_summary(entry)
        full_text = self._extract_full_text(entry)

        return RawArticle(
            source_id=self.source_id,
            url=url,
            title=title,
            published_at=published_at,
            summary=summary,
            full_text=full_text,
        )

    @staticmethod
    def _parse_date(entry) -> datetime | None:
        """Return a timezone-aware UTC datetime from a feedparser entry."""
        import time as _time
        struct = (
            entry.get("published_parsed")
            or entry.get("updated_parsed")
            or entry.get("created_parsed")
        )
        if struct is None:
            return None
        try:
            ts = _time.mktime(struct)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            return None

    @staticmethod
    def _extract_summary(entry) -> str | None:
        """Pull summary / description text, strip basic HTML tags."""
        raw = (
            entry.get("summary")
            or entry.get("description")
            or ""
        ).strip()
        if not raw:
            return None
        # Strip HTML tags simply (BeautifulSoup not needed for summary)
        from html.parser import HTMLParser

        class _Stripper(HTMLParser):
            def __init__(self):
                super().__init__()
                self._parts: list[str] = []

            def handle_data(self, data: str):
                self._parts.append(data)

            def get_text(self) -> str:
                return " ".join(self._parts).strip()

        stripper = _Stripper()
        stripper.feed(raw)
        text = stripper.get_text()
        return text[:500] if text else None

    @staticmethod
    def _extract_full_text(entry) -> str | None:
        """Best-effort full-text from content fields (not always present)."""
        content_list = entry.get("content", [])
        if content_list:
            raw = content_list[0].get("value", "")
            if raw:
                from bs4 import BeautifulSoup
                return BeautifulSoup(raw, "html.parser").get_text(separator=" ")[:3000]
        return None
