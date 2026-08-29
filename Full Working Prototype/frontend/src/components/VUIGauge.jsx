import './VUIGauge.css';

export default function VUIGauge({ score = 0, priorityMode = 'normal' }) {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const isActive = priorityMode === 'vulnerable_user';

  return (
    <div className={`vui-gauge ${isActive ? 'vui-gauge--active' : ''}`}>
      <svg viewBox="0 0 180 180" className="vui-gauge-svg">
        <circle cx="90" cy="90" r={radius} className="vui-track" />
        <circle
          cx="90" cy="90" r={radius}
          className="vui-fill"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
        {isActive && <circle cx="90" cy="90" r={radius} className="vui-pulse-ring" />}
      </svg>
      <div className="vui-readout">
        <span className="vui-score">{score}</span>
        <span className="vui-label">VUI</span>
      </div>
    </div>
  );
}
