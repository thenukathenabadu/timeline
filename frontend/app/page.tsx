'use client';

import { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { fetchEvents, triggerScrape, type TimelineEvent } from './lib/api';
import SidePanel from './components/SidePanel/SidePanel';
import Filters from './components/Filters/Filters';

// vis-timeline uses browser APIs — load client-side only
const TimelineView = dynamic(() => import('./components/Timeline/TimelineView'), {
  ssr: false,
  loading: () => <TimelinePlaceholder text="Loading timeline…" />,
});

export default function Home() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null);
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    const data = await fetchEvents({ category: category || undefined });
    setEvents(data);
    setLoading(false);
  }, [category]);

  useEffect(() => { load(); }, [load]);

  async function handleScrape() {
    setScraping(true);
    await triggerScrape();
    // Give the worker a moment then reload
    setTimeout(() => { load(); setScraping(false); }, 3000);
  }

  return (
    <div style={styles.root}>
      {/* Top bar */}
      <header style={styles.header}>
        <div style={styles.wordmark}>Timeline</div>
        <div style={styles.eventCount}>
          {loading ? '…' : `${events.length} event${events.length !== 1 ? 's' : ''}`}
        </div>
      </header>

      {/* Filter bar */}
      <Filters
        category={category}
        onCategoryChange={setCategory}
        onScrape={handleScrape}
        scraping={scraping}
      />

      {/* Main area */}
      <div style={styles.main}>
        {/* Timeline */}
        <div style={styles.timelineWrap}>
          {loading ? (
            <TimelinePlaceholder text="Loading events…" />
          ) : (
            <TimelineView events={events} onSelect={setSelectedEvent} />
          )}
        </div>

        {/* Side panel (slides in when an event is selected) */}
        <SidePanel event={selectedEvent} onClose={() => setSelectedEvent(null)} />
      </div>
    </div>
  );
}

function TimelinePlaceholder({ text }: { text: string }) {
  return (
    <div style={placeholderStyle}>
      <span style={{ color: 'var(--muted)', fontSize: 14 }}>{text}</span>
    </div>
  );
}

const placeholderStyle: React.CSSProperties = {
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const styles: Record<string, React.CSSProperties> = {
  root: {
    height: '100dvh',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    background: 'var(--bg)',
  },
  header: {
    height: 52,
    display: 'flex',
    alignItems: 'center',
    padding: '0 20px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-card)',
    gap: 16,
    flexShrink: 0,
  },
  wordmark: {
    fontSize: 22,
    fontWeight: 900,
    letterSpacing: -1,
    color: 'var(--text)',
    flex: 1,
  },
  eventCount: {
    fontSize: 12,
    color: 'var(--muted)',
    fontFamily: 'var(--font-mono)',
  },
  main: {
    flex: 1,
    display: 'flex',
    overflow: 'hidden',
  },
  timelineWrap: {
    flex: 1,
    overflow: 'hidden',
    position: 'relative',
  },
};
