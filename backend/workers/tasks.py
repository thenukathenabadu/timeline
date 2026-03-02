import asyncio
import logging

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run(coro):
    """Run an async coroutine from a sync Celery task."""
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(name="workers.tasks.scrape_source", bind=True, max_retries=3)
def scrape_source(self, source_id: str):
    """Scrape a single source by ID and persist new articles to the DB."""
    from scraper.registry import get_scraper
    from models.db import SessionLocal
    from workers.db_utils import save_articles, mark_source_scraped

    scraper = get_scraper(source_id)
    if scraper is None:
        logger.warning("Unknown source_id: %s", source_id)
        return {"status": "unknown_source", "source": source_id}

    async def _scrape():
        try:
            raw_articles = await scraper.fetch_latest()
        except Exception as exc:
            logger.exception("Scrape failed for %s: %s", source_id, exc)
            raise self.retry(exc=exc, countdown=60)

        async with SessionLocal() as session:
            inserted, skipped = await save_articles(session, raw_articles)
            await mark_source_scraped(session, source_id)

        logger.info(
            "Scraped %s — fetched=%d inserted=%d skipped=%d",
            source_id, len(raw_articles), inserted, skipped,
        )
        return {
            "status": "ok",
            "source": source_id,
            "fetched": len(raw_articles),
            "inserted": inserted,
            "skipped": skipped,
        }

    return _run(_scrape())


@celery_app.task(name="workers.tasks.scrape_all", bind=True)
def scrape_all(self):
    """Dispatch scrape_source for every enabled source."""
    from models.db import SessionLocal
    from models.source import Source
    from sqlalchemy import select

    async def _get_enabled():
        async with SessionLocal() as session:
            result = await session.execute(
                select(Source.id).where(Source.enabled.is_(True))
            )
            return [row[0] for row in result.all()]

    source_ids = _run(_get_enabled())
    for sid in source_ids:
        scrape_source.delay(sid)

    return {"status": "dispatched", "sources": source_ids}


@celery_app.task(name="workers.tasks.process_article", bind=True, max_retries=3)
def process_article(self, article_id: str):
    """
    Embed an article, extract event date, classify category and country.
    Implemented in Phase 2 when the AI pipeline exists.
    """
    # TODO Phase 2
    return {"status": "not_implemented", "article_id": article_id}


@celery_app.task(name="workers.tasks.cluster_events", bind=True)
def cluster_events(self):
    """
    Run cosine-similarity clustering over un-grouped articles to form Events.
    Implemented in Phase 2.
    """
    # TODO Phase 2
    return {"status": "not_implemented"}
