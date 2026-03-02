from fastapi import APIRouter, HTTPException
from workers.celery_app import celery_app

router = APIRouter()


@router.post("/admin/scrape")
async def trigger_scrape(source: str | None = None):
    """
    Manually trigger a scrape job.
    Pass ?source=bbc to scrape a single source, or omit to scrape all.
    """
    if source:
        task = celery_app.send_task("workers.tasks.scrape_source", args=[source])
        return {"queued": True, "source": source, "task_id": task.id}

    task = celery_app.send_task("workers.tasks.scrape_all")
    return {"queued": True, "source": "all", "task_id": task.id}
