"""Helpers for persisting scraped data to PostgreSQL."""

import hashlib
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.article import Article
from models.source import Source
from scraper.base import RawArticle


def _content_hash(title: str, published_at: datetime) -> str:
    """SHA-256 of title + ISO date string — stable deduplication key."""
    raw = f"{title.strip().lower()}|{published_at.date().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def save_articles(
    session: AsyncSession,
    raw_articles: list[RawArticle],
) -> tuple[int, int]:
    """
    Upsert a list of RawArticle objects into the articles table.

    Returns (inserted, skipped) counts.
    """
    if not raw_articles:
        return 0, 0

    inserted = 0
    skipped = 0

    for raw in raw_articles:
        content_hash = _content_hash(raw.title, raw.published_at)

        stmt = (
            pg_insert(Article)
            .values(
                source_id=raw.source_id,
                url=raw.url,
                title=raw.title,
                summary=raw.summary,
                content_hash=content_hash,
                published_at=raw.published_at,
            )
            .on_conflict_do_nothing()  # catches url OR content_hash collisions
        )
        result = await session.execute(stmt)
        if result.rowcount:
            inserted += 1
        else:
            skipped += 1

    await session.commit()
    return inserted, skipped


async def mark_source_scraped(session: AsyncSession, source_id: str) -> None:
    """Update `last_scraped_at` timestamp on a source row."""
    await session.execute(
        update(Source)
        .where(Source.id == source_id)
        .values(last_scraped_at=datetime.now(tz=timezone.utc))
    )
    await session.commit()


async def seed_sources(session: AsyncSession) -> None:
    """
    Insert default source rows if they don't exist yet.
    Called once on app startup via init_db.
    """
    from scraper.registry import all_scrapers

    for scraper in all_scrapers():
        stmt = (
            pg_insert(Source)
            .values(
                id=scraper.source_id,
                display_name=scraper.display_name,
                url=scraper.home_url,
                enabled=True,
            )
            .on_conflict_do_nothing(index_elements=["id"])
        )
        await session.execute(stmt)
    await session.commit()
