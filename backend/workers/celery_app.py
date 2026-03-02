from celery import Celery
from celery.schedules import crontab
from config import settings

celery_app = Celery(
    "timeline",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Retry failed tasks once after 60s
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# ── Scheduled scraping jobs ───────────────────────────────────────────────────
celery_app.conf.beat_schedule = {
    "scrape-news-feeds": {
        "task": "workers.tasks.scrape_all",
        "schedule": crontab(minute="*/15"),  # every 15 min
    },
}
