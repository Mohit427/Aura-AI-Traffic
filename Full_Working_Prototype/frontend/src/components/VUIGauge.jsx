import './VUIGauge.css';

const STATUS = {
  normal: { color: 'var(--status-good)', label: 'Normal operation', tone: 'good' },
  vulnerable_user: { color: 'var(--status-warning)', label: 'Vulnerable user priority', tone: 'warning' },
  emergency_vehicle: { color: 'var(--status-critical)', label: 'Emergency preemption', tone: 'critical' },
  transit_priority: { color: '#3FC1C9', label: 'Transit signal priority', tone: 'good' },
};

function calculateFillPercent(score, priorityMode) {
  if (priorityMode === 'emergency_vehicle') return 92;
  if (priorityMode === 'transit_priority') return 60;
  if (priorityMode === 'vulnerable_user') return Math.min(65 + score * 2, 90);
  return Math.min(10 + score * 2, 25);
}

export default function VUIGauge({ score = 0, priorityMode = 'normal' }) {
  const radius = 92;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const fillPercent = calculateFillPercent(clamped, priorityMode);
  const offset = circumference - (fillPercent / 100) * circumference;
  const status = STATUS[priorityMode] ?? STATUS.normal;
  const elevated = priorityMode !== 'normal';
  
  return (
    <div className={`vui-gauge vui-gauge--${status.tone}`}>
      <div className="vui-gauge__halo" aria-hidden="true" />
      <svg viewBox="0 0 200 200" className="vui-gauge-svg">
        <circle cx="100" cy="100" r={radius} className="vui-track" />
        <circle
          cx="100" cy="100" r={radius}
          className="vui-fill"
          style={{ stroke: status.color }}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
        {elevated && (
          <circle
            cx="100" cy="100" r={radius}
            className="vui-pulse-ring"
            style={{ stroke: status.color }}
          />
        )}
      </svg>
      {priorityMode === 'emergency_vehicle' && <div className="vui-gauge__sweep" aria-hidden="true" />}
      <div className="vui-readout">
        <span className="vui-score">{Math.round(clamped)}</span>
        <span className="vui-label">Vulnerable User Index</span>
      </div>
      <div className="vui-status-pill">
        <span className="vui-status-dot" style={{ background: status.color }} />
        {status.label}
      </div>
    </div>
  );
}
