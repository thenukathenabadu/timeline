'use client';

import { useEffect, useRef, useCallback } from 'react';
import type { TimelineEvent } from '../../lib/api';

// vis-timeline types are bundled with the package
declare module 'vis-timeline/standalone' {
  export * from 'vis-timeline';
}

interface Props {
  events: TimelineEvent[];
  onSelect: (event: TimelineEvent) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  politics:  '#7c3aed',
  war:       '#ef4444',
  finance:   '#f59e0b',
  science:   '#06b6d4',
  nature:    '#22c55e',
  sports:    '#ec4899',
  health:    '#10b981',
  crime:     '#f97316',
  other:     '#6b7280',
};

export default function TimelineView({ events, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<any>(null);

  const handleSelect = useCallback(
    (props: { items: string[] }) => {
      if (!props.items.length) return;
      const event = events.find((e) => e.id === props.items[0]);
      if (event) onSelect(event);
    },
    [events, onSelect],
  );

  useEffect(() => {
    if (!containerRef.current || events.length === 0) return;

    import('vis-timeline/standalone').then(({ Timeline, DataSet }) => {
      const items = new DataSet(
        events.map((e) => {
          const color = CATEGORY_COLORS[e.category ?? 'other'] ?? CATEGORY_COLORS.other;
          return {
            id: e.id,
            content: `<span style="font-size:12px;font-weight:600">${escapeHtml(e.title.slice(0, 60))}${e.title.length > 60 ? '…' : ''}</span>`,
            start: e.event_date,
            style: `
              background:${color}22;
              border-color:${color};
              color:#e8e8f0;
              border-radius:6px;
              font-family:system-ui,sans-serif;
            `,
            title: `${e.title}${e.has_conflict ? ' ⚠ sources disagree on time' : ''}`,
          };
        }),
      );

      const options = {
        height: '100%',
        zoomMin: 1000 * 60 * 60,           // 1 hour
        zoomMax: 1000 * 60 * 60 * 24 * 365 * 25, // 25 years
        stack: true,
        showMajorLabels: true,
        showMinorLabels: true,
        orientation: { axis: 'top' },
        selectable: true,
        tooltip: { followMouse: true, overflowMethod: 'cap' },
        start: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30), // 30 days ago
        end: new Date(Date.now() + 1000 * 60 * 60 * 24 * 2),    // 2 days ahead
      };

      if (timelineRef.current) {
        timelineRef.current.destroy();
      }

      const tl = new Timeline(containerRef.current!, items as any, options as any);
      tl.on('select', handleSelect);
      timelineRef.current = tl;
    });

    return () => {
      timelineRef.current?.destroy();
      timelineRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events]);

  if (events.length === 0) {
    return (
      <div style={emptyStyle}>
        <p style={{ color: 'var(--muted)', fontSize: 14 }}>
          No events yet — trigger a scrape to populate the timeline.
        </p>
        <code style={{ color: 'var(--muted)', fontSize: 12, marginTop: 8 }}>
          POST /api/v1/admin/scrape
        </code>
      </div>
    );
  }

  return (
    <>
      {/* vis-timeline CSS loaded via global */}
      <div ref={containerRef} style={{ height: '100%', width: '100%' }} />
    </>
  );
}

function escapeHtml(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const emptyStyle: React.CSSProperties = {
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 8,
};
