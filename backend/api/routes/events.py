from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db import get_session
from models.event import Event

router = APIRouter()


@router.get("/events")
async def list_events(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    category: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    """
    Return events within a date range, with optional category/country filters.
    Used by the frontend timeline to populate event markers.
    """
    q = select(Event).order_by(Event.event_date.desc())

    if from_date:
        q = q.where(Event.event_date >= from_date)
    if to_date:
        q = q.where(Event.event_date <= to_date)
    if category:
        q = q.where(Event.category == category)
    if country:
        q = q.where(Event.country_codes.contains([country]))

    q = q.limit(limit).offset(offset)
    result = await session.execute(q)
    events = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "title": e.title,
            "summary": e.summary,
            "event_date": e.event_date.isoformat(),
            "category": e.category,
            "country_codes": e.country_codes or [],
            "has_conflict": e.has_conflict,
        }
        for e in events
    ]
