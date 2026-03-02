'use client';

import { useMemo, useRef, useEffect } from 'react';
import type { TimelineEvent } from '../../lib/api';

/* ── Category colours ────────────────────────────────────────────────────── */
const CAT_COLOR: Record<string, string> = {
  politics: '#7c3aed',
  war:      '#ef4444',
  finance:  '#f59e0b',
  science:  '#06b6d4',
  nature:   '#22c55e',
  sports:   '#ec4899',
  health:   '#10b981',
  crime:    '#f97316',
  other:    '#6b6b8a',
};

/* ── Layout constants ────────────────────────────────────────────────────── */
const AXIS_Y       = 260;   // px from top where the axis sits
const PX_PER_DAY  = 180;   // horizontal density
const SIDE_PAD    = 100;   // left / right padding
const CONN_BASE   = 55;    // shortest connector (axis → text)
const CONN_STEP   = 50;    // added per stagger level
const MAX_LEVELS  = 4;
const MIN_X_GAP   = 140;   // min px between texts at same level & side
const TEXT_W      = 130;   // text block width

/* ── Types ───────────────────────────────────────────────────────────────── */
interface Pos {
  event:   TimelineEvent;
  x:       number;
  above:   boolean;
  level:   number;
}

/* ── Helpers ─────────────────────────────────────────────────────────────── */
function assignPositions(events: TimelineEvent[], totalWidth: number, minT: number, range: number): Pos[] {
  const sorted = [...events].sort((a, b) =>
    new Date(a.event_date).getTime() - new Date(b.event_date).getTime()
  );

  const raw = sorted.map((e, i) => ({
    event: e,
    x:     ((new Date(e.event_date).getTime() - minT) / range) * (totalWidth - SIDE_PAD * 2) + SIDE_PAD,
    above: i % 2 === 0,
  }));

  const levels: number[] = raw.map(() => 0);
  for (let i = 0; i < raw.length; i++) {
    const used = new Set<number>();
    for (let j = 0; j < i; j++) {
      if (raw[j].above === raw[i].above && Math.abs(raw[j].x - raw[i].x) < MIN_X_GAP) {
        used.add(levels[j]);
      }
    }
    let l = 0;
    while (used.has(l) && l < MAX_LEVELS - 1) l++;
    levels[i] = l;
  }

  return raw.map((r, i) => ({ ...r, level: levels[i] }));
}

function buildTicks(minT: number, maxT: number, totalWidth: number, range: number) {
  const rangeDays = range / 86400000;
  const mode = rangeDays <= 7 ? 'day' : rangeDays <= 90 ? 'week' : rangeDays <= 730 ? 'month' : 'year';

  const ticks: { x: number; label: string; major: boolean }[] = [];
  const toX = (t: number) => ((t - minT) / range) * (totalWidth - SIDE_PAD * 2) + SIDE_PAD;

  const step = (date: Date): Date => {
    const d = new Date(date);
    if (mode === 'day')   d.setDate(d.getDate() + 1);
    if (mode === 'week')  d.setDate(d.getDate() + 7);
    if (mode === 'month') d.setMonth(d.getMonth() + 1);
    if (mode === 'year')  d.setFullYear(d.getFullYear() + 1);
    return d;
  };

  const start = (): Date => {
    const d = new Date(minT);
    if (mode === 'day')   { d.setHours(0, 0, 0, 0); return d; }
    if (mode === 'week')  { d.setHours(0, 0, 0, 0); return d; }
    if (mode === 'month') return new Date(d.getFullYear(), d.getMonth(), 1);
    return new Date(d.getFullYear(), 0, 1);
  };

  let cur = start();
  const end = new Date(maxT);

  while (cur <= end) {
    const major = mode === 'month' ? cur.getMonth() === 0 : true;
    const label =
      mode === 'day'   ? cur.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) :
      mode === 'week'  ? cur.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) :
      mode === 'month' ? (major ? cur.getFullYear().toString() : cur.toLocaleDateString('en-US', { month: 'short' })) :
      cur.getFullYear().toString();

    ticks.push({ x: toX(cur.getTime()), label, major });
    cur = step(cur);
  }
  return ticks;
}

/* ── Main component ──────────────────────────────────────────────────────── */
export default function TimelineView({
  events,
  onSelect,
}: {
  events: TimelineEvent[];
  onSelect: (e: TimelineEvent) => void;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);

  /* drag-to-scroll */
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    let isDown = false, startX = 0, scrollLeft = 0;
    const down  = (e: MouseEvent) => { isDown = true; startX = e.pageX - el.offsetLeft; scrollLeft = el.scrollLeft; el.style.cursor = 'grabbing'; };
    const up    = () => { isDown = false; el.style.cursor = 'grab'; };
    const move  = (e: MouseEvent) => { if (!isDown) return; e.preventDefault(); el.scrollLeft = scrollLeft - (e.pageX - el.offsetLeft - startX); };
    el.addEventListener('mousedown', down);
    el.addEventListener('mouseup', up);
    el.addEventListener('mouseleave', up);
    el.addEventListener('mousemove', move);
    return () => { el.removeEventListener('mousedown', down); el.removeEventListener('mouseup', up); el.removeEventListener('mouseleave', up); el.removeEventListener('mousemove', move); };
  }, []);

  const { positions, totalWidth, ticks, canvasH } = useMemo(() => {
    if (!events.length) return { positions: [], totalWidth: 0, ticks: [], canvasH: 500 };

    const times  = events.map(e => new Date(e.event_date).getTime());
    const minT   = Math.min(...times);
    const maxT   = Math.max(...times);
    const range  = Math.max(maxT - minT, 86400000);
    const totalWidth = Math.max((range / 86400000) * PX_PER_DAY + SIDE_PAD * 2, 1400);

    const positions = assignPositions(events, totalWidth, minT, range);
    const ticks     = buildTicks(minT, maxT, totalWidth, range);
    const maxLvl    = Math.max(...positions.map(p => p.level), 0);
    const canvasH   = AXIS_Y + CONN_BASE + maxLvl * CONN_STEP + 120;

    return { positions, totalWidth, ticks, canvasH };
  }, [events]);

  /* ── Empty state ── */
  if (!events.length) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
        <span style={{ fontSize: 32 }}>📅</span>
        <p style={{ color: 'var(--muted)', fontSize: 14 }}>No events yet — trigger a scrape to populate the timeline.</p>
        <code style={{ color: 'var(--muted)', fontSize: 12 }}>Click ↺ Scrape now above</code>
      </div>
    );
  }

  return (
    <div ref={scrollRef} style={{ overflowX: 'auto', overflowY: 'auto', height: '100%', cursor: 'grab', userSelect: 'none' }}>
      <div style={{ position: 'relative', width: totalWidth, height: Math.max(canvasH, 500) }}>

        {/* ── Axis rail ── */}
        <div style={{
          position: 'absolute', top: AXIS_Y, left: SIDE_PAD / 2, right: SIDE_PAD / 2,
          height: 3, background: '#1e1e2e', borderRadius: 99,
          boxShadow: '0 0 0 1px #2a2a3e',
        }} />

        {/* ── Ticks ── */}
        {ticks.map((t, i) => (
          <div key={i} style={{ position: 'absolute', left: t.x, top: AXIS_Y - 1 }}>
            <div style={{
              width: t.major ? 2 : 1,
              height: t.major ? 16 : 8,
              background: t.major ? '#3a3a5e' : '#2a2a3e',
              marginLeft: -1,
            }} />
            <span style={{
              position: 'absolute',
              top: t.major ? 20 : 13,
              left: '50%',
              transform: 'translateX(-50%)',
              fontSize: t.major ? 13 : 10,
              fontWeight: t.major ? 700 : 400,
              color: t.major ? 'var(--text)' : 'var(--muted)',
              whiteSpace: 'nowrap',
              fontFamily: 'var(--font-mono)',
              letterSpacing: t.major ? -0.5 : 0,
            }}>{t.label}</span>
          </div>
        ))}

        {/* ── Events ── */}
        {positions.map(({ event, x, above, level }) => {
          const color   = CAT_COLOR[event.category ?? 'other'] ?? CAT_COLOR.other;
          const connLen = CONN_BASE + level * CONN_STEP;
          const mSz     = 11;

          /* connector: starts at axis, goes up or down */
          const connTop  = above ? AXIS_Y - connLen : AXIS_Y + 3;

          /* text block: just beyond the connector end */
          const textTop  = above ? AXIS_Y - connLen - 72 : AXIS_Y + connLen + 6;

          const dateStr = new Date(event.event_date).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric',
          });

          return (
            <div key={event.id}>
              {/* Diamond marker */}
              <div
                onClick={() => onSelect(event)}
                title={event.title}
                style={{
                  position: 'absolute',
                  left: x - mSz / 2,
                  top: AXIS_Y - mSz / 2,
                  width: mSz,
                  height: mSz,
                  background: color,
                  transform: 'rotate(45deg)',
                  cursor: 'pointer',
                  zIndex: 4,
                  borderRadius: 2,
                  boxShadow: `0 0 8px ${color}88`,
                  transition: 'transform 0.15s',
                }}
                onMouseEnter={e => (e.currentTarget.style.transform = 'rotate(45deg) scale(1.4)')}
                onMouseLeave={e => (e.currentTarget.style.transform = 'rotate(45deg) scale(1)')}
              />

              {/* Connector line */}
              <div style={{
                position: 'absolute',
                left: x,
                top: connTop,
                width: 1,
                height: connLen,
                background: `linear-gradient(${above ? '180deg' : '0deg'}, transparent 0%, ${color}70 100%)`,
                zIndex: 2,
              }} />

              {/* Small dot at connector/text junction */}
              <div style={{
                position: 'absolute',
                left: x - 3,
                top: above ? connTop - 3 : connTop + connLen - 3,
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: color,
                opacity: 0.6,
                zIndex: 3,
              }} />

              {/* Text label */}
              <div
                onClick={() => onSelect(event)}
                style={{
                  position: 'absolute',
                  left: x - TEXT_W / 2,
                  top: textTop,
                  width: TEXT_W,
                  textAlign: 'center',
                  cursor: 'pointer',
                  zIndex: 5,
                }}
              >
                <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 3, fontFamily: 'var(--font-mono)' }}>
                  {dateStr}
                </div>
                <div style={{
                  fontSize: 11,
                  fontWeight: 600,
                  color: 'var(--text)',
                  lineHeight: 1.35,
                  display: '-webkit-box',
                  WebkitLineClamp: 4,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}>
                  {event.title}
                </div>
                {event.has_conflict && (
                  <div style={{ fontSize: 9, color: '#f59e0b', marginTop: 2 }}>⚠ conflict</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
