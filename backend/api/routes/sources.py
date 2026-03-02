from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db import get_session
from models.source import Source

router = APIRouter()


@router.get("/sources")
async def list_sources(session: AsyncSession = Depends(get_session)):
    """Return all registered news sources with their enabled status."""
    result = await session.execute(select(Source).order_by(Source.display_name))
    sources = result.scalars().all()
    return [
        {
            "id": s.id,
            "display_name": s.display_name,
            "url": s.url,
            "enabled": s.enabled,
            "last_scraped_at": s.last_scraped_at.isoformat() if s.last_scraped_at else None,
        }
        for s in sources
    ]


@router.patch("/sources/{source_id}")
async def toggle_source(
    source_id: str,
    enabled: bool,
    session: AsyncSession = Depends(get_session),
):
    """Enable or disable a source (user preference from the UI)."""
    result = await session.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Source not found")
    source.enabled = enabled
    await session.commit()
    return {"id": source.id, "enabled": source.enabled}
