'use client';

import { useEffect, useState } from 'react';
import { fetchArticles, type Article, type TimelineEvent } from '../../lib/api';

const SOURCE_COLORS: Record<string, string> = {
  bbc:       '#ef4444',
  reuters:   '#f59e0b',
  ap:        '#06b6d4',
  guardian:  '#22c55e',
  aljazeera: '#7c3aed',
};

interface Props {
  event: TimelineEvent | null;
  onClose: () => void;
}

export default function SidePanel({ event, onClose }: Props) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!event) { setArticles([]); return; }
    setLoading(true);
    fetchArticles(event.id)
      .then(setArticles)
      .finally(() => setLoading(false));
  }, [event?.id]);

  if (!event) return null;

  const eventDate = new Date(event.event_date).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });

  return (
    <aside style={styles.panel}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.meta}>
          {event.category && (
            <span style={styles.categoryBadge}>{event.category}</span>
          )}
          {event.has_conflict && (
            <span style={styles.conflictBadge}>⚠ sources disagree on time</span>
          )}
          <span style={styles.date}>{eventDate}</span>
        </div>
        <button style={styles.closeBtn} onClick={onClose} aria-label="Close">✕</button>
      </div>

      <h2 style={styles.title}>{event.title}</h2>

      {event.summary && (
        <p style={styles.summary}>{event.summary}</p>
      )}

      <div style={styles.divider} />

      {/* Article list */}
      <div style={styles.articleList}>
        <p style={styles.sectionLabel}>
          {loading ? 'Loading…' : `${articles.length} source${articles.length !== 1 ? 's' : ''}`}
        </p>

        {articles.map((a) => {
          const sourceColor = SOURCE_COLORS[a.source_id] ?? '#6b7280';
          const pubDate = new Date(a.published_at).toLocaleString('en-US', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
          });
          return (
            <a
              key={a.id}
              href={a.url}
              target="_blank"
              rel="noopener noreferrer"
              style={styles.articleCard}
            >
              <div style={styles.articleHeader}>
                <span style={{ ...styles.sourceBadge, borderColor: sourceColor, color: sourceColor }}>
                  {a.source_id.toUpperCase()}
                </span>
                <span style={styles.pubDate}>{pubDate}</span>
              </div>
              <p style={styles.articleTitle}>{a.title}</p>
              {a.summary && <p style={styles.articleSummary}>{a.summary}</p>}
            </a>
          );
        })}
      </div>
    </aside>
  );
}

const styles: Record<string, React.CSSProperties> = {
  panel: {
    width: 400,
    flexShrink: 0,
    height: '100%',
    overflowY: 'auto',
    background: 'var(--bg-card)',
    borderLeft: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    padding: '20px 20px 40px',
    gap: 16,
  },
  header: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: 8,
  },
  meta: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6,
    alignItems: 'center',
  },
  categoryBadge: {
    fontSize: 11,
    fontWeight: 700,
    padding: '2px 8px',
    borderRadius: 4,
    background: 'var(--brand-dim)',
    color: 'var(--brand)',
    border: '1px solid var(--brand)',
    textTransform: 'capitalize',
    letterSpacing: 0.3,
  },
  conflictBadge: {
    fontSize: 11,
    padding: '2px 8px',
    borderRadius: 4,
    background: 'rgba(245,158,11,0.1)',
    color: '#f59e0b',
    border: '1px solid rgba(245,158,11,0.4)',
  },
  date: {
    fontSize: 12,
    color: 'var(--muted)',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    color: 'var(--muted)',
    cursor: 'pointer',
    fontSize: 16,
    padding: 4,
    flexShrink: 0,
  },
  title: {
    fontSize: 18,
    fontWeight: 700,
    color: 'var(--text)',
    lineHeight: 1.4,
  },
  summary: {
    fontSize: 14,
    color: 'var(--muted)',
    lineHeight: 1.6,
  },
  divider: {
    height: 1,
    background: 'var(--border)',
  },
  articleList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  sectionLabel: {
    fontSize: 11,
    fontWeight: 600,
    color: 'var(--muted)',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  articleCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
    padding: '12px 14px',
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    textDecoration: 'none',
    cursor: 'pointer',
    transition: 'border-color 0.15s',
  },
  articleHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  sourceBadge: {
    fontSize: 10,
    fontWeight: 700,
    padding: '1px 6px',
    borderRadius: 3,
    border: '1px solid',
    fontFamily: 'var(--font-mono)',
  },
  pubDate: {
    fontSize: 11,
    color: 'var(--muted)',
  },
  articleTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--text)',
    lineHeight: 1.4,
  },
  articleSummary: {
    fontSize: 12,
    color: 'var(--muted)',
    lineHeight: 1.5,
    display: '-webkit-box',
    WebkitLineClamp: 3,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
};
