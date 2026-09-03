import { useEffect, useState } from 'react';
import './DashboardShell.css';

const STATUS_COPY = {
  normal: { label: 'Normal operation', color: 'var(--status-good)' },
  vulnerable_user: { label: 'Vulnerable user priority', color: 'var(--status-warning)' },
  emergency_vehicle: { label: 'Emergency preemption', color: 'var(--status-critical)' },
};

function useClock() {
  const [time, setTime] = useState(() => new Date());

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return time;
}

export default function DashboardShell({ children, priorityMode = 'normal' }) {
  const time = useClock();
  const status = STATUS_COPY[priorityMode] ?? STATUS_COPY.normal;

  return (
    <div className="shell">
      <header className="shell-header">
        <div className="shell-brand">
          <span className="shell-brand-mark" style={{ '--dot-color': status.color }} />
          <div>
            <h1>AURA</h1>
            <p className="shell-subtitle">Vadapalani Junction · 13.0505°N, 80.2121°E</p>
          </div>
        </div>
        <div className="shell-status">
          <span className="shell-status-pill" style={{ '--dot-color': status.color }}>
            <span className="status-dot" />
            {status.label}
          </span>
          <time className="shell-clock" dateTime={time.toISOString()}>
            {time.toLocaleTimeString('en-GB')}
          </time>
        </div>
      </header>
      <main className="shell-grid">{children}</main>
    </div>
  );
}
