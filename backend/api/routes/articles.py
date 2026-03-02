from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db import get_session
from models.article import Article
from models.event_article import EventArticle

router = APIRouter()


@router.get("/events/{event_id}/articles")
async def list_articles_for_event(
    event_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Return all articles linked to a specific event, for the side panel."""
    q = (
        select(Article)
        .join(EventArticle, EventArticle.article_id == Article.id)
        .where(EventArticle.event_id == event_id)
        .order_by(Article.published_at.asc())
    )
    result = await session.execute(q)
    articles = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "source_id": a.source_id,
            "url": a.url,
            "title": a.title,
            "summary": a.summary,
            "published_at": a.published_at.isoformat(),
            "event_date": a.event_date.isoformat() if a.event_date else None,
            "category": a.category,
            "country_codes": a.country_codes or [],
        }
        for a in articles
    ]
