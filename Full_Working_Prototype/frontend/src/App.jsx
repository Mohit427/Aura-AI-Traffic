import DashboardShell from './components/DashboardShell';
import VUIGauge from './components/VUIGauge';
import SignalTimeline from './components/SignalTimeline';
import './App.css';

function Panel({ title, children, className = '' }) {
  return (
    <section className={`panel ${className}`}>
      <h2 className="panel-title">{title}</h2>
      <div className="panel-body">{children}</div>
    </section>
  );
}

// Dummy data — matches Engine Output contract, replace with live data on Day 6
const mockEngineOutput = {
  priority_mode: 'vulnerable_user',
  vui_score: 68,
  phase_durations: {
    north_south_green: 32,
    east_west_green: 28,
    pedestrian_crossing_green: 15,
  },
};

const phases = [
  { label: 'North-South', duration: mockEngineOutput.phase_durations.north_south_green, color: 'var(--accent-cyan)' },
  { label: 'East-West', duration: mockEngineOutput.phase_durations.east_west_green, color: 'var(--signal-green)' },
  { label: 'Pedestrian', duration: mockEngineOutput.phase_durations.pedestrian_crossing_green, color: 'var(--accent-amber)' },
];

export default function App() {
  return (
    <DashboardShell>
      <Panel title="LIVE VIEW" className="panel-live">
        <div className="placeholder">Camera feed will render here</div>
      </Panel>
      <Panel title="VULNERABLE USER INDEX">
        <VUIGauge score={mockEngineOutput.vui_score} priorityMode={mockEngineOutput.priority_mode} />
      </Panel>
      <Panel title="SIGNAL PHASE TIMELINE" className="panel-wide">
        <SignalTimeline phases={phases} />
      </Panel>
    </DashboardShell>
  );
}
