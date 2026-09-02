import { useEffect, useState } from 'react';
import DashboardShell from './components/DashboardShell';
import VUIGauge from './components/VUIGauge';
import SignalTimeline from './components/SignalTimeline';
import AdvisorPanel from './components/AdvisorPanel';
import { fetchLatestDecision } from './api';
import './App.css';

function Panel({ title, children, className = '' }) {
  return (
    <section className={`panel ${className}`}>
      <h2 className="panel-title">{title}</h2>
      <div className="panel-body">{children}</div>
    </section>
  );
}

export default function App() {
  const [engineData, setEngineData] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadDecision() {
      try {
        const data = await fetchLatestDecision();
        if (isMounted) {
          setEngineData(data);
        }
      } catch (error) {
        console.error('Failed to load latest decision:', error);
      }
    }

    loadDecision();
    const intervalId = setInterval(loadDecision, 2000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  if (!engineData) {
    return (
      <DashboardShell>
        <div className="placeholder">Loading traffic decision data…</div>
      </DashboardShell>
    );
  }

  const phases = [
    { label: 'North-South', duration: engineData.phase_durations?.north_south_green ?? 0, color: 'var(--accent-cyan)' },
    { label: 'East-West', duration: engineData.phase_durations?.east_west_green ?? 0, color: 'var(--signal-green)' },
    { label: 'Pedestrian', duration: engineData.phase_durations?.pedestrian_crossing_green ?? 0, color: 'var(--accent-amber)' },
  ];

  return (
    <DashboardShell>
      <Panel title="LIVE VIEW" className="panel-live">
        <div className="placeholder">Camera feed will render here</div>
      </Panel>
      <Panel title="VULNERABLE USER INDEX">
        <VUIGauge score={engineData.vui_score} priorityMode={engineData.priority_mode} />
      </Panel>
      <Panel title="SIGNAL PHASE TIMELINE" className="panel-wide">
        <SignalTimeline phases={phases} />
      </Panel>
      <div className="panel-wide">
        <AdvisorPanel engineData={engineData} />
      </div>
    </DashboardShell>
  );
}
