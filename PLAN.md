# Timeline — Project Plan

> A website that continuously scrapes news sources and builds a scrollable, zoomable
> global timeline of events. Multiple sources covering the same event are grouped by AI.
> All articles are shown with full source attribution. Conflicts in timing are surfaced,
> never hidden.

---

## Core Concept

Users land on a single giant timeline spanning centuries to seconds. They can:

- **Scroll** left/right through time
- **Zoom** between hour → day → month → year → decade → century
- **Hover** a point to see a date and event count
- **Click** a point to open a side panel of all news about that period
- **Filter** by country, region, category, or source

The timeline shows **Events** (real-world occurrences), not raw articles. Each Event is
linked to one or more Articles from different sources. When sources disagree on timing
or facts, a "Sources disagree" badge appears and all versions are displayed.

---

## Constraints

| Constraint | Detail |
|---|---|
| Budget | Zero — everything must be free / open-source |
| Organisation | Non-profit — storage and compute must stay minimal |
| Dev environment | Local PC (Windows) |
| Production | Oracle Cloud free tier — 4 vCPU / 24 GB RAM ARM VM |
| Migration | Architecture must make local → cloud seamless (Docker Compose) |

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | Next.js 14+ (TypeScript) | SSR for SEO, free on Vercel, great ecosystem |
| Backend API | FastAPI (Python) | Best AI/NLP ecosystem, async, fast |
| Scraping workers | Celery + Redis | Background jobs, scheduling, task queue |
| Database | PostgreSQL + pgvector | Stores articles AND embedding vectors in one DB |
| Timeline UI | vis-timeline | Handles zoom levels natively; can swap to D3 later |
| HTML scraping | Playwright + httpx + BeautifulSoup | Covers JS-heavy and static sites |
| RSS feeds | feedparser | Structured, reliable for major news sources |
| Containers | Docker Compose | Identical local and cloud environments |

---

## AI Model Selection

### Tasks the AI must perform

1. Convert article text to embedding vectors (for similarity-based grouping)
2. Classify articles into categories (finance, war, nature, politics, sports, science…)
3. Extract the **event date** from article body (not just the publish date)
4. Group articles from different sources that cover the same real-world event
5. Generate a brief (~100 word) summary per grouped event

### Model comparison

| Model | Size | CPU viable | Primary use |
|---|---|---|---|
| `all-MiniLM-L6-v2` (sentence-transformers) | **22 MB** | Instant | Embeddings + clustering |
| `facebook/bart-large-mnli` | 1.6 GB | Moderate | Zero-shot classification |
| `Llama 3.2:1b` (Ollama) | 1.3 GB | Moderate (~10 tok/s) | Reasoning, date extraction |
| `Llama 3.2:3b` (Ollama) | 2.0 GB | Slow (~3 tok/s) | Better reasoning |
| `Phi-3.5-mini` (Ollama) | 2.4 GB | Borderline | Excellent quality, heavier |
| `Mistral 7B` (Ollama) | 4.1 GB | Barely | Best quality, too slow for batch |

### Decision: Hybrid two-layer approach

**Layer 1 — Embeddings: `all-MiniLM-L6-v2`**

- 22 MB, CPU, millisecond inference — zero cost at any scale
- Converts every article to a 384-dimensional vector stored in pgvector
- Grouping = cosine similarity query (articles within threshold → same event)
- Zero-shot classification = cosine similarity to category label embeddings
  (embed "war conflict military attack" → find articles nearest to that vector)
- Handles ~90 % of all grouping and classification without touching an LLM

**Layer 2 — Reasoning: `Llama 3.2:1b` via Ollama**

- 1.3 GB, runs on any modern CPU at ~10 tokens/sec
- Called only when embedding similarity is inconclusive
- Tasks: extract event date from article text, disambiguate borderline groupings,
  generate event summaries
- Ollama serves it as a local REST endpoint — easy to swap the model name in config

**Why not Llama 3B / Phi-3.5?**
The Oracle Cloud ARM VM (4 vCPU / 24 GB) must also run PostgreSQL, Redis, and Celery
workers. At 3 tokens/sec the 3B model creates a processing bottleneck for batch jobs.
The 1B model at 10 tokens/sec is sufficient for extraction and short-form reasoning.

**Why not bart-large-mnli?**
The embedding model already performs zero-shot classification via cosine similarity.
Adding a 1.6 GB model for the same task doubles memory footprint for no gain.

### Plug-and-play provider interface

The AI layer is fully modular. Switching models or providers is a one-line config change.

```
backend/ai/
  base.py          Abstract AIProvider
                   - embed(text) → list[float]
                   - classify(text, categories) → str
                   - extract_event_date(text) → datetime | None
                   - summarize(texts) → str

  sentence_tf.py   SentenceTransformerProvider  ← default (Layer 1)
  ollama.py        OllamaProvider               ← default (Layer 2)
  openai.py        OpenAIProvider               ← future drop-in
  claude.py        ClaudeProvider               ← future drop-in
  factory.py       get_provider(config) → AIProvider
```

`config.yaml` controls which provider is active:
```yaml
ai:
  embedding_provider: sentence_transformer
  embedding_model: all-MiniLM-L6-v2
  reasoning_provider: ollama
  reasoning_model: llama3.2:1b
```

---

## Data Sources — v1

| Source | Method | Cadence |
|---|---|---|
| BBC News | RSS feed | Every 15 min |
| Reuters | RSS feed | Every 15 min |
| AP News | RSS feed | Every 15 min |
| The Guardian | RSS feed | Every 30 min |
| Al Jazeera | RSS feed | Every 30 min |
| Wikipedia | MediaWiki REST API | One-time bulk + on-demand |
| Twitter/X | Playwright headless scrape (public search) | Hourly, best-effort |

Users can enable or disable any source from the UI. Each source is a single Python file
implementing `BaseScraper` — adding a new source (CNN, NYT, etc.) = one new file,
register in `config.yaml`.

---

## Data Storage Strategy

Goal: store the minimum needed to render the timeline and detail panel.

| Stored | Not stored |
|---|---|
| title, URL, source_id | Full article HTML |
| published_at, event_date | Raw scraped content |
| content_hash (SHA-256) | Scraped images |
| AI summary (~100 words) | |
| category, country_codes[] | |
| embedding vector (384 floats) | |

**Deduplication**: content_hash (SHA-256 of title + published_at) prevents re-inserting
the same article on repeated scrapes.

**Historical bulk data**: gzipped JSONL files per year — portable, cheap, expandable.

**Estimated footprint at 1 M articles (≈ 20 years of data):**
- Article metadata: ~500 MB
- Embeddings in pgvector: ~1.5 GB
- Total: ~2 GB — comfortably within Oracle free tier (200 GB block storage)

---

## Project Structure

```
timeline/
  PLAN.md                         This document
  docker-compose.yml              Local dev stack
  docker-compose.prod.yml         Production overrides

  frontend/                       Next.js 14+ app (TypeScript)
    app/
      page.tsx                    Main timeline page
      layout.tsx
      globals.css
    components/
      Timeline/                   vis-timeline wrapper + zoom controls
      SidePanel/                  Article list for selected date range
      Filters/                    Country / category / source toggles
      ArticleCard/                Single article display
    lib/
      api.ts                      API client (typed fetch wrappers)
      types.ts                    Shared TypeScript types

  backend/                        FastAPI + Celery (Python)
    main.py                       FastAPI app entry point
    config.yaml                   All runtime settings
    api/
      routes/
        events.py                 GET /events?from=&to=&category=&country=
        articles.py               GET /articles?event_id=
        sources.py                GET /sources
        admin.py                  POST /admin/scrape (manual trigger)
    models/
      db.py                       SQLAlchemy setup + pgvector
      article.py                  Article table
      event.py                    Event table
      event_article.py            Join table
      source.py                   Source registry
    scraper/
      base.py                     BaseScraper abstract class
      rss.py                      Generic RSS scraper (reusable)
      sources/
        bbc.py
        reuters.py
        ap.py
        guardian.py
        aljazeera.py
        wikipedia.py
        twitter.py
    ai/
      base.py
      sentence_tf.py
      ollama.py
      openai.py                   (stub — future)
      claude.py                   (stub — future)
      factory.py
    workers/
      scrape.py                   Celery task: scrape_source(source_id)
      process.py                  Celery task: process_article(article_id)
      cluster.py                  Celery task: cluster_events()
      schedule.py                 Celery beat schedule definitions
```

---

## Build Phases

### Phase 0 — Foundation
**Goal:** Everything runs. Nothing breaks. Stack is wired end-to-end.

- [ ] GitHub repo created, PLAN.md committed
- [ ] `docker-compose.yml` — services: postgres (+ pgvector), redis, fastapi, celery-worker, celery-beat
- [ ] Database schema migrated (articles, events, event_articles, sources tables)
- [ ] FastAPI skeleton — GET /health returns `{ "status": "ok" }`
- [ ] Next.js app — placeholder homepage
- [ ] `docker compose up` → all services green

### Phase 1 — Scraping Infrastructure
**Goal:** Real articles flowing into the database on a schedule.

- [ ] `BaseScraper` abstract class + `RawArticle` dataclass
- [ ] Generic `RSSScaper` that any RSS source can extend
- [ ] Source implementations: BBC, Reuters, AP, The Guardian, Al Jazeera
- [ ] Celery beat schedule (every 15 min for news, every 30 min for slower sources)
- [ ] Deduplication via content_hash on insert
- [ ] Admin endpoint: POST /admin/scrape?source=bbc triggers immediate scrape

### Phase 2 — AI Pipeline
**Goal:** Articles are embedded, grouped into Events, and categorised automatically.

- [ ] `AIProvider` abstract base class
- [ ] `SentenceTransformerProvider` with `all-MiniLM-L6-v2`
- [ ] pgvector column on articles table; embed on ingest
- [ ] Clustering worker: cosine similarity query → group into Events
- [ ] Zero-shot classification via embedding similarity → category tags
- [ ] `OllamaProvider` with `llama3.2:1b` — event date extraction from text
- [ ] Event grouping worker runs after each scrape batch

### Phase 3 — Timeline UI
**Goal:** A working, interactive timeline in the browser.

- [ ] vis-timeline integrated into Next.js
- [ ] Zoom levels: hour → day → month → year → decade → century
- [ ] Hover tooltip: date + event count
- [ ] Click → side panel slides in with articles grouped by Event
- [ ] Article card: source badge, headline, published time, AI summary
- [ ] "Sources disagree" badge on conflicting events

### Phase 4 — Filtering
**Goal:** Users can narrow the timeline to what they care about.

- [ ] Category filter (finance, war, nature, politics, sports, science, other)
- [ ] Country / region filter (country codes extracted by AI on ingest)
- [ ] Source selector (toggle individual sources on/off)
- [ ] Date range picker
- [ ] All filters encoded in URL params (shareable links)

### Phase 5 — Wikipedia historical data
**Goal:** Timeline extends back to 2005 with structured historical events.

- [ ] Wikipedia MediaWiki API integration in `wikipedia.py`
- [ ] Bulk ingestion job: process N articles/hour to respect API rate limits
- [ ] Wikipedia events flow through the same AI pipeline (embed → classify → group)
- [ ] Data range configurable: default 2005–present, expandable in config

### Phase 6 — Twitter/X scraping
**Goal:** Real-time social signals on the timeline.

- [ ] Playwright headless scraper for public Twitter search
- [ ] Rate-limit handling: exponential backoff, randomised delays
- [ ] Extract: tweet text, timestamp, username (public data only)
- [ ] Source badge: clearly labelled as Twitter throughout the UI
- [ ] Graceful degradation: if scraping fails, log and skip — never crash the pipeline

### Phase 7 — Production migration
**Goal:** Live on the internet, running 24/7 for free.

- [ ] `docker-compose.prod.yml` — restart policies, volume mounts, env secrets
- [ ] Nginx reverse proxy config (SSL termination)
- [ ] Let's Encrypt / Certbot for HTTPS
- [ ] Deploy backend to Oracle Cloud ARM VM
- [ ] Deploy frontend to Vercel (free tier)
- [ ] Weekly pg_dump backup to gzipped JSONL

---

## Key Design Decisions

### Event vs Article
- **Article** = one piece of content from one source (a BBC article, a tweet, a Reuters story)
- **Event** = a real-world occurrence, linked to 1..N Articles
- The timeline renders Events. The side panel shows all Articles for that Event.
- This separation means multiple sources can cover the same Event without duplication
  on the timeline itself.

### Conflict handling
- AI groups and tags — it never hides or removes any article
- If two articles for the same Event have different timestamps, both timestamps are shown
- A "Sources disagree on time" badge appears on the Event marker
- Users see the raw evidence; they decide what to trust

### Source plugin system
Every scraper implements one interface:
```python
class BaseScraper(ABC):
    source_id: str          # e.g. "bbc", "reuters"
    display_name: str       # e.g. "BBC News"

    @abstractmethod
    async def fetch_latest(self) -> list[RawArticle]: ...
```
Adding CNN = create `cnn.py`, implement `fetch_latest()`, add one line to `config.yaml`.
No other code changes needed.

---

## Verification checkpoints

| Phase | Test |
|---|---|
| 0 | `docker compose up` → all containers healthy → GET /health → 200 |
| 1 | Trigger BBC scrape → rows appear in `articles` table with correct source/date |
| 2 | Two articles about same event from BBC + Reuters → grouped into one Event record |
| 3 | Timeline renders → zoom from year to day → side panel opens with articles |
| 4 | Enable Finance filter → only finance Events visible on timeline |
| 5 | Wikipedia 2010 events visible alongside modern news articles |
| 6 | Tweet about a news event appears grouped with the same BBC article |
| 7 | Domain resolves → HTTPS → scraping running → new articles appear within 15 min |
