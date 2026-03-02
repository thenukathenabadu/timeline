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

# ── Scheduled jobs ────────────────────────────────────────────────────────────
celery_app.conf.beat_schedule = {
    "scrape-news-feeds": {
        "task": "workers.tasks.scrape_all",
        "schedule": crontab(minute="*/15"),  # every 15 min
    },
    "process-new-articles": {
        "task": "workers.tasks.process_new_articles",
        "schedule": crontab(minute="*/20"),  # every 20 min
    },
    "cluster-events": {
        "task": "workers.tasks.cluster_events",
        "schedule": crontab(minute="*/30"),  # every 30 min
    },
}
