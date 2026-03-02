"""
Event clustering — groups articles into Events using pgvector cosine similarity.

Algorithm:
  1. Fetch un-clustered articles that have embeddings
  2. For each, find existing Events with a similar representative embedding
  3. If similarity > THRESHOLD → link article to that event
  4. Otherwise → create a new singleton Event from the article
  5. Update event metadata (date range, conflict flag)
"""

import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.article import Article
from models.event import Event
from models.event_article import EventArticle

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.82  # cosine similarity — tune as needed


async def get_unclustered_articles(session: AsyncSession) -> list[Article]:
    """Return articles that have an embedding but are not in any event yet."""
    stmt = (
        select(Article)
        .where(Article.embedding.isnot(None))
        .where(
            ~Article.id.in_(
                select(EventArticle.article_id)
            )
        )
        .order_by(Article.published_at)
        .limit(200)  # process in batches
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def find_matching_event(
    session: AsyncSession,
    embedding: list[float],
    published_at: datetime,
) -> Event | None:
    """
    Find an event whose representative embedding is within SIMILARITY_THRESHOLD
    of the given embedding and whose date is within 7 days.
    """
    # pgvector cosine distance: <=> (0=identical, 2=opposite)
    # cosine similarity = 1 - distance
    distance_threshold = 1.0 - SIMILARITY_THRESHOLD
    cutoff_days = 7

    stmt = text("""
        SELECT e.id
        FROM events e
        JOIN event_articles ea ON ea.event_id = e.id
        JOIN articles a ON a.id = ea.article_id
        WHERE a.embedding IS NOT NULL
          AND ABS(EXTRACT(EPOCH FROM (e.event_date - :pub_at)) / 86400) <= :cutoff
          AND (a.embedding <=> CAST(:emb AS vector)) < :dist
        ORDER BY (a.embedding <=> CAST(:emb AS vector))
        LIMIT 1
    """)
    result = await session.execute(stmt, {
        "emb": str(embedding),
        "pub_at": published_at,
        "cutoff": cutoff_days,
        "dist": distance_threshold,
    })
    row = result.first()
    if row is None:
        return None

    event = await session.get(Event, row[0])
    return event


async def create_event_from_article(session: AsyncSession, article: Article) -> Event:
    """Create a new singleton Event seeded from a single article."""
    event = Event(
        id=uuid.uuid4(),
        title=article.title[:500],
        summary=article.summary,
        event_date=article.event_date or article.published_at,
        category=article.category,
        country_codes=article.country_codes,
        has_conflict=False,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
    )
    session.add(event)
    await session.flush()  # get the ID before linking
    return event


async def link_article_to_event(
    session: AsyncSession,
    article: Article,
    event: Event,
) -> None:
    """Insert event_articles join row (idempotent)."""
    stmt = (
        pg_insert(EventArticle)
        .values(event_id=event.id, article_id=article.id)
        .on_conflict_do_nothing()
    )
    await session.execute(stmt)


async def update_event_metadata(session: AsyncSession, event: Event) -> None:
    """Recalculate event metadata from all its linked articles."""
    stmt = (
        select(Article)
        .join(EventArticle, EventArticle.article_id == Article.id)
        .where(EventArticle.event_id == event.id)
    )
    result = await session.execute(stmt)
    articles = list(result.scalars().all())

    if not articles:
        return

    dates = [a.event_date or a.published_at for a in articles]
    date_min = min(dates)
    date_max = max(dates)

    # Flag conflict if articles disagree on the event date by more than 1 day
    has_conflict = (date_max - date_min).total_seconds() > 86400

    event.event_date = date_min
    event.has_conflict = has_conflict
    event.updated_at = datetime.now(tz=timezone.utc)

    # Use the category and country codes from majority vote (simple: first article wins for now)
    if event.category is None:
        event.category = articles[0].category
    if not event.country_codes:
        event.country_codes = articles[0].country_codes


async def run_clustering(session: AsyncSession) -> dict:
    """
    Main clustering loop. Returns a summary dict with counts.
    """
    articles = await get_unclustered_articles(session)
    if not articles:
        return {"processed": 0, "new_events": 0, "merged": 0}

    new_events = 0
    merged = 0

    for article in articles:
        embedding = article.embedding
        if embedding is None:
            continue

        # Convert pgvector type to plain list if needed
        if hasattr(embedding, 'tolist'):
            embedding = embedding.tolist()

        existing = await find_matching_event(session, embedding, article.published_at)

        if existing:
            await link_article_to_event(session, article, existing)
            await update_event_metadata(session, existing)
            merged += 1
        else:
            event = await create_event_from_article(session, article)
            await link_article_to_event(session, article, event)
            new_events += 1

    await session.commit()
    logger.info(
        "Clustering done — processed=%d new_events=%d merged=%d",
        len(articles), new_events, merged,
    )
    return {"processed": len(articles), "new_events": new_events, "merged": merged}
