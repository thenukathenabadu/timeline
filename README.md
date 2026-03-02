# Timeline

A scrollable, zoomable timeline of world events — continuously scraped from news sources,
Wikipedia, and social media. AI groups articles from different sources covering the same event.

---

## Quick start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js 20+](https://nodejs.org/) (for the frontend)

### 1. Clone and configure

```bash
git clone https://github.com/thenukathenabadu/timeline.git
cd timeline
cp .env.example .env   # edit if needed
```

### 2. Start the backend stack

```bash
docker compose up --build
```

This starts: **PostgreSQL** (+ pgvector), **Redis**, **FastAPI** backend, **Celery** worker, and **Celery beat** scheduler.

Verify everything is healthy:
```
GET http://localhost:8000/health
→ { "status": "ok", "database": "ok" }
```

API docs: http://localhost:8000/docs

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## Project structure

```
timeline/
  backend/        FastAPI + Celery (Python 3.11)
  frontend/       Next.js 14 (TypeScript)
  docker-compose.yml          Local dev
  docker-compose.prod.yml     Production (Phase 7)
  PLAN.md         Full phased build plan
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service + DB connectivity |
| GET | `/api/v1/events` | Events in a date range |
| GET | `/api/v1/events/:id/articles` | Articles linked to an event |
| GET | `/api/v1/sources` | Registered news sources |
| PATCH | `/api/v1/sources/:id` | Enable / disable a source |
| POST | `/api/v1/admin/scrape` | Trigger manual scrape |

## Build phases

| Phase | Status | Description |
|---|---|---|
| 0 — Foundation | ✅ Complete | Docker stack, DB schema, FastAPI skeleton, Next.js placeholder |
| 1 — Scraping | Pending | RSS feeds: BBC, Reuters, AP, Guardian, Al Jazeera |
| 2 — AI Pipeline | Pending | Embeddings, clustering, classification (all-MiniLM-L6-v2 + Llama 3.2:1b) |
| 3 — Timeline UI | Pending | vis-timeline, zoom levels, side panel |
| 4 — Filtering | Pending | Category, country, source, date range |
| 5 — Wikipedia | Pending | Historical data back to 2005 |
| 6 — Twitter/X | Pending | Playwright headless scraping |
| 7 — Production | Pending | Oracle Cloud ARM, Nginx, SSL, Vercel |

See [PLAN.md](./PLAN.md) for full details.
