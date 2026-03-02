from fastapi import APIRouter
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


@router.post("/admin/process")
async def trigger_process():
    """Manually trigger embedding + clustering pipeline."""
    t1 = celery_app.send_task("workers.tasks.process_new_articles")
    t2 = celery_app.send_task("workers.tasks.cluster_events")
    return {"queued": True, "tasks": [t1.id, t2.id]}


@router.post("/admin/scrape-and-process")
async def scrape_and_process():
    """Scrape all sources then immediately kick off the AI pipeline."""
    celery_app.send_task("workers.tasks.scrape_all")
    # Give scraping 30s head start, then process
    celery_app.send_task("workers.tasks.process_new_articles",
                         countdown=30)
    celery_app.send_task("workers.tasks.cluster_events",
                         countdown=90)
    return {"queued": True}
