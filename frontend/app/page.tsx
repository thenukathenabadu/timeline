export default function Home() {
  const phases = [
    { id: 0, label: 'Foundation',           status: 'done'    },
    { id: 1, label: 'Scraping',             status: 'done'    },
    { id: 2, label: 'AI Pipeline',          status: 'pending' },
    { id: 3, label: 'Timeline UI',          status: 'pending' },
    { id: 4, label: 'Filtering',            status: 'pending' },
    { id: 5, label: 'Wikipedia history',    status: 'pending' },
    { id: 6, label: 'Twitter/X',            status: 'pending' },
    { id: 7, label: 'Production',           status: 'pending' },
  ];

  return (
    <main style={styles.root}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.wordmark}>Timeline</div>
        <p style={styles.tagline}>
          A scrollable, zoomable timeline of world events — built from news, Wikipedia, and social media.
        </p>
      </header>

      {/* Timeline strip placeholder */}
      <section style={styles.timelineWrap}>
        <div style={styles.timelineRail}>
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} style={styles.tick}>
              <div style={styles.tickLine} />
              <span style={styles.tickLabel}>{2005 + i}</span>
            </div>
          ))}
        </div>
        <div style={styles.timelineOverlay}>
          <span style={styles.overlayText}>Timeline renders here — Phase 3</span>
        </div>
      </section>

      {/* Build progress */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>Build progress</h2>
        <div style={styles.phases}>
          {phases.map((p) => (
            <div key={p.id} style={styles.phase}>
              <div style={{
                ...styles.phaseDot,
                background: p.status === 'done' ? 'var(--green)' : 'var(--border)',
              }} />
              <span style={styles.phaseNum}>Phase {p.id}</span>
              <span style={styles.phaseLabel}>{p.label}</span>
              <span style={{
                ...styles.phaseBadge,
                color: p.status === 'done' ? 'var(--green)' : 'var(--muted)',
                borderColor: p.status === 'done' ? 'rgba(34,197,94,0.3)' : 'var(--border)',
              }}>
                {p.status === 'done' ? 'complete' : 'pending'}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* API status */}
      <section style={styles.section}>
        <h2 style={styles.sectionTitle}>API endpoints</h2>
        <div style={styles.endpoints}>
          {[
            ['GET', '/health',                  'Service + DB connectivity check'],
            ['GET', '/api/v1/events',           'Events in a date range'],
            ['GET', '/api/v1/events/:id/articles', 'Articles linked to an event'],
            ['GET', '/api/v1/sources',          'Registered news sources'],
            ['PATCH','/api/v1/sources/:id',     'Enable / disable a source'],
            ['POST', '/api/v1/admin/scrape',    'Trigger manual scrape'],
          ].map(([method, path, desc]) => (
            <div key={path} style={styles.endpoint}>
              <span style={{
                ...styles.method,
                color: method === 'GET' ? '#60a5fa'
                     : method === 'POST' ? 'var(--green)'
                     : '#f59e0b',
              }}>{method}</span>
              <code style={styles.path}>{path}</code>
              <span style={styles.desc}>{desc}</span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    maxWidth: 860,
    margin: '0 auto',
    padding: '60px 24px 120px',
    display: 'flex',
    flexDirection: 'column',
    gap: 56,
  },
  header: {
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  wordmark: {
    fontSize: 48,
    fontWeight: 900,
    letterSpacing: -2,
    color: 'var(--text)',
  },
  tagline: {
    fontSize: 16,
    color: 'var(--muted)',
    lineHeight: 1.6,
    maxWidth: 560,
  },

  // Timeline strip
  timelineWrap: {
    position: 'relative',
    height: 100,
    borderRadius: 12,
    border: '1px solid var(--border)',
    overflow: 'hidden',
    background: 'var(--bg-card)',
  },
  timelineRail: {
    display: 'flex',
    alignItems: 'flex-end',
    height: '100%',
    paddingBottom: 12,
    paddingLeft: 16,
    gap: 32,
  },
  tick: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 4,
  },
  tickLine: {
    width: 1,
    height: 20,
    background: 'var(--border)',
  },
  tickLabel: {
    fontSize: 11,
    color: 'var(--muted)',
    fontFamily: 'var(--font-mono)',
  },
  timelineOverlay: {
    position: 'absolute',
    inset: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(9,9,15,0.6)',
  },
  overlayText: {
    fontSize: 13,
    color: 'var(--muted)',
    letterSpacing: 0.3,
  },

  // Section
  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--muted)',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },

  // Phases
  phases: {
    display: 'flex',
    flexDirection: 'column',
    gap: 0,
    border: '1px solid var(--border)',
    borderRadius: 10,
    overflow: 'hidden',
    background: 'var(--bg-card)',
  },
  phase: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '12px 16px',
    borderBottom: '1px solid var(--border)',
  },
  phaseDot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    flexShrink: 0,
  },
  phaseNum: {
    fontSize: 12,
    color: 'var(--muted)',
    fontFamily: 'var(--font-mono)',
    minWidth: 52,
  },
  phaseLabel: {
    fontSize: 14,
    color: 'var(--text)',
    flex: 1,
  },
  phaseBadge: {
    fontSize: 11,
    fontWeight: 600,
    padding: '2px 8px',
    borderRadius: 4,
    border: '1px solid',
    letterSpacing: 0.3,
  },

  // Endpoints
  endpoints: {
    display: 'flex',
    flexDirection: 'column',
    gap: 0,
    border: '1px solid var(--border)',
    borderRadius: 10,
    overflow: 'hidden',
    background: 'var(--bg-card)',
  },
  endpoint: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '10px 16px',
    borderBottom: '1px solid var(--border)',
  },
  method: {
    fontSize: 11,
    fontWeight: 700,
    fontFamily: 'var(--font-mono)',
    minWidth: 44,
  },
  path: {
    fontSize: 13,
    fontFamily: 'var(--font-mono)',
    color: 'var(--text)',
    minWidth: 260,
  },
  desc: {
    fontSize: 13,
    color: 'var(--muted)',
  },
};
