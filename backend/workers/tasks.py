import asyncio
import logging

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run(coro):
    """Run an async coroutine from a sync Celery task."""
    return asyncio.run(coro)


# ── Phase 1: Scraping ─────────────────────────────────────────────────────────

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
    """Dispatch scrape_source for every enabled source, then process new articles."""
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

    # Trigger AI processing after scraping finishes
    # (slight delay so scrape tasks can insert rows first)
    process_new_articles.apply_async(countdown=120)

    return {"status": "dispatched", "sources": source_ids}


# ── Phase 2: AI Pipeline ──────────────────────────────────────────────────────

@celery_app.task(name="workers.tasks.process_article", bind=True, max_retries=3)
def process_article(self, article_id: str):
    """Embed an article, extract event date, classify category."""
    from uuid import UUID
    from models.db import SessionLocal
    from models.article import Article
    from sqlalchemy import select, update
    from ai.factory import get_embedding_provider, get_reasoning_provider

    async def _process():
        async with SessionLocal() as session:
            result = await session.execute(
                select(Article).where(Article.id == UUID(article_id))
            )
            article = result.scalar_one_or_none()
            if article is None:
                return {"status": "not_found", "article_id": article_id}

            embedding_provider = get_embedding_provider()
            reasoning_provider = get_reasoning_provider()

            # Build text for embedding (title + summary)
            text = f"{article.title}. {article.summary or ''}".strip()

            # Embed
            vectors = embedding_provider.embed([text])
            embedding = vectors[0]

            # Classify category
            category = embedding_provider.classify(text)

            # Extract event date (fallback to published_at)
            event_date = await reasoning_provider.extract_event_date(
                title=article.title,
                summary=article.summary or "",
                published_at=article.published_at,
            )
            if event_date is None:
                event_date = article.published_at

            # Persist
            await session.execute(
                update(Article)
                .where(Article.id == article.id)
                .values(embedding=embedding, category=category, event_date=event_date)
            )
            await session.commit()

        return {"status": "ok", "article_id": article_id, "category": category}

    try:
        return _run(_process())
    except Exception as exc:
        logger.exception("process_article failed for %s", article_id)
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="workers.tasks.process_new_articles", bind=True)
def process_new_articles(self):
    """Embed and classify all articles that don't have embeddings yet."""
    from models.db import SessionLocal
    from models.article import Article
    from sqlalchemy import select

    async def _get_unprocessed():
        async with SessionLocal() as session:
            result = await session.execute(
                select(Article.id).where(Article.embedding.is_(None)).limit(500)
            )
            return [str(row[0]) for row in result.all()]

    article_ids = _run(_get_unprocessed())
    for aid in article_ids:
        process_article.delay(aid)

    # After processing, cluster into events
    if article_ids:
        cluster_events.apply_async(countdown=60)

    return {"status": "dispatched", "articles": len(article_ids)}


@celery_app.task(name="workers.tasks.cluster_events", bind=True)
def cluster_events(self):
    """Group embedded articles into Events via cosine similarity."""
    from models.db import SessionLocal
    from workers.cluster_utils import run_clustering

    async def _cluster():
        async with SessionLocal() as session:
            return await run_clustering(session)

    result = _run(_cluster())
    logger.info("cluster_events result: %s", result)
    return result
