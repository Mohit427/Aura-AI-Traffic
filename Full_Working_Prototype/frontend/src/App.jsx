import { useEffect, useState } from 'react';
import DashboardShell from './components/DashboardShell';
import VUIGauge from './components/VUIGauge';
import SignalTimeline from './components/SignalTimeline';
import EVConflictPanel from './components/EVConflictPanel';
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

function buildEvData(evSchedule) {
  if (!evSchedule) return null;
  const formatAxis = (axis) => (axis ? axis.replace('_', '-') : '—');
  return {
    ev1: {
      lane: formatAxis(evSchedule.ev_1_axis),
      distance_m: '—',
      speed_kmh: '—',
      tti_sec: evSchedule.ev_1_green_flush_duration ?? '—',
    },
    ev2: {
      lane: formatAxis(evSchedule.ev_2_axis),
      distance_m: '—',
      speed_kmh: '—',
      tti_sec: '—',
    },
  };
}

function clipForMode(priorityMode) {
  if (priorityMode === 'emergency_vehicle') return '/demo-clips/ambulance_footage.mp4';
  if (priorityMode === 'vulnerable_user') return '/demo-clips/platoon_footage.mp4';
  return '/demo-clips/normal_footage.mp4';
}

export default function App() {
  const [engineData, setEngineData] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadDecision() {
      try {
        const data = await fetchLatestDecision();
        if (!isMounted) return;
        if (data.priority_mode === 'emergency_vehicle' && data.ev_schedule) {
          data.ev_data = buildEvData(data.ev_schedule);
          data.ev_stage = 1;
          data.downstream_green_wave = true;
        }
        setEngineData(data);
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
    { label: 'North-South', duration: engineData.phase_durations?.north_south_green ?? 0, color: 'var(--cat-blue)' },
    { label: 'East-West', duration: engineData.phase_durations?.east_west_green ?? 0, color: 'var(--cat-aqua)' },
    { label: 'Pedestrian', duration: engineData.phase_durations?.pedestrian_crossing_green ?? 0, color: 'var(--cat-violet)' },
  ];

  return (
    <DashboardShell priorityMode={engineData.priority_mode}>
      <div className="panel-hero">
        <Panel title="Live view" className="panel-live">
          <video
            key={engineData.priority_mode}
            autoPlay
            loop
            muted
            playsInline
            className="live-view-video"
          >
            <source src={clipForMode(engineData.priority_mode)} type="video/mp4" />
          </video>
        </Panel>
        <div className="hero-vui">
          <VUIGauge score={engineData.vui_score} priorityMode={engineData.priority_mode} />
        </div>
      </div>
      {engineData.priority_mode !== 'emergency_vehicle' && (
        <Panel title="Signal phase timeline" className="panel-wide">
          <SignalTimeline phases={phases} />
        </Panel>
      )}
      <div className="panel-wide">
        <EVConflictPanel engineData={engineData} />
      </div>
      <div className="panel-wide">
        <AdvisorPanel engineData={engineData} />
      </div>
    </DashboardShell>
  );
}
