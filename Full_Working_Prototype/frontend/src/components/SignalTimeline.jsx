import './SignalTimeline.css';

export default function SignalTimeline({ phases }) {
  const total = phases.reduce((sum, p) => sum + p.duration, 0);

  return (
    <div className="timeline">
      <div className="timeline-bar">
        {phases.map((p, i) => (
          <div
            key={i}
            className="timeline-segment"
            style={{ width: `${(p.duration / total) * 100}%`, background: p.color }}
            title={`${p.label}: ${p.duration}s`}
          />
        ))}
      </div>
      <div className="timeline-legend">
        {phases.map((p, i) => (
          <div key={i} className="legend-item">
            <span className="legend-swatch" style={{ background: p.color }} />
            <span>{p.label} — {p.duration}s</span>
          </div>
        ))}
      </div>
    </div>
  );
}
