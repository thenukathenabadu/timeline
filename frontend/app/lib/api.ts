const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export interface TimelineEvent {
  id: string;
  title: string;
  summary: string | null;
  event_date: string;
  category: string | null;
  country_codes: string[] | null;
  has_conflict: boolean;
  article_count?: number;
}

export interface Article {
  id: string;
  source_id: string;
  url: string;
  title: string;
  summary: string | null;
  published_at: string;
  event_date: string | null;
  category: string | null;
}

export interface Source {
  id: string;
  display_name: string;
  url: string | null;
  enabled: boolean;
  last_scraped_at: string | null;
}

export async function fetchEvents(params: {
  from?: string;
  to?: string;
  category?: string;
  country?: string;
}): Promise<TimelineEvent[]> {
  const qs = new URLSearchParams();
  if (params.from) qs.set('from', params.from);
  if (params.to) qs.set('to', params.to);
  if (params.category) qs.set('category', params.category);
  if (params.country) qs.set('country', params.country);
  const res = await fetch(`${BASE}/api/v1/events?${qs}`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchArticles(eventId: string): Promise<Article[]> {
  const res = await fetch(`${BASE}/api/v1/events/${eventId}/articles`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchSources(): Promise<Source[]> {
  const res = await fetch(`${BASE}/api/v1/sources`);
  if (!res.ok) return [];
  return res.json();
}

export async function triggerScrape(sourceId?: string): Promise<void> {
  const url = sourceId
    ? `${BASE}/api/v1/admin/scrape?source=${sourceId}`
    : `${BASE}/api/v1/admin/scrape`;
  await fetch(url, { method: 'POST' });
}
