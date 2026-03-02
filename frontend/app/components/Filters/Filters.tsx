'use client';

interface Props {
  category: string;
  onCategoryChange: (c: string) => void;
  onScrape: () => void;
  scraping: boolean;
}

const CATEGORIES = ['all', 'politics', 'war', 'finance', 'science', 'nature', 'sports', 'health', 'crime', 'other'];

export default function Filters({ category, onCategoryChange, onScrape, scraping }: Props) {
  return (
    <div style={styles.bar}>
      <div style={styles.group}>
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => onCategoryChange(c === 'all' ? '' : c)}
            style={{
              ...styles.chip,
              ...((!category && c === 'all') || category === c ? styles.chipActive : {}),
            }}
          >
            {c}
          </button>
        ))}
      </div>

      <button
        style={{ ...styles.scrapeBtn, opacity: scraping ? 0.5 : 1 }}
        onClick={onScrape}
        disabled={scraping}
      >
        {scraping ? 'Scraping…' : '↺ Scrape now'}
      </button>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  bar: {
    height: 48,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 20px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-card)',
    gap: 12,
    flexShrink: 0,
  },
  group: {
    display: 'flex',
    gap: 6,
    overflowX: 'auto',
  },
  chip: {
    background: 'none',
    border: '1px solid var(--border)',
    borderRadius: 6,
    color: 'var(--muted)',
    fontSize: 12,
    padding: '3px 10px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    textTransform: 'capitalize',
    transition: 'border-color 0.15s, color 0.15s',
  },
  chipActive: {
    borderColor: 'var(--brand)',
    color: 'var(--brand)',
    background: 'var(--brand-dim)',
  },
  scrapeBtn: {
    background: 'none',
    border: '1px solid var(--border)',
    borderRadius: 6,
    color: 'var(--muted)',
    fontSize: 12,
    padding: '4px 12px',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    flexShrink: 0,
  },
};
