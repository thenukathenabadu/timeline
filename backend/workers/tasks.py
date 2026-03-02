from workers.celery_app import celery_app


@celery_app.task(name="workers.tasks.scrape_source", bind=True, max_retries=3)
def scrape_source(self, source_id: str):
    """
    Scrape a single source by its ID (e.g. 'bbc', 'reuters').
    Implemented in Phase 1 when BaseScraper and source plugins exist.
    """
    # TODO Phase 1: instantiate the right scraper and run it
    return {"status": "not_implemented", "source": source_id}


@celery_app.task(name="workers.tasks.scrape_all", bind=True)
def scrape_all(self):
    """Trigger scrape_source for every enabled source."""
    # TODO Phase 1: query enabled sources from DB and dispatch per-source tasks
    return {"status": "not_implemented"}


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
