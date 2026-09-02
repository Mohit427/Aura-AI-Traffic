import './EVConflictPanel.css';

export default function EVConflictPanel({ engineData }) {
  if (engineData?.priority_mode !== 'emergency_vehicle' || !engineData?.ev_data) {
    return null;
  }

  const ev1 = engineData.ev_data.ev1 ?? {};
  const ev2 = engineData.ev_data.ev2 ?? {};
  const activeStage = Number(engineData.ev_stage) || 0;

  const stages = [
    { id: 1, label: 'Active Lane Flush', subLabel: 'EV-1' },
    { id: 2, label: 'All-Red Safe Clearance', subLabel: '' },
    { id: 3, label: 'Secondary Axis Corridor', subLabel: 'EV-2' },
  ];

  const getStageClass = (stageId) => {
    if (stageId === activeStage) return 'ev-conflict-stage--active';
    if (stageId < activeStage) return 'ev-conflict-stage--completed';
    return 'ev-conflict-stage--pending';
  };

  return (
    <section className="ev-conflict-panel">
      <header className="ev-conflict-header">
        <span className="ev-conflict-pulse-dot" aria-hidden="true" />
        <h2 className="ev-conflict-title">DUAL EMERGENCY VEHICLE CONFLICT RESOLUTION</h2>
      </header>

      <div className="ev-conflict-grid">
        <div className="ev-conflict-card ev-conflict-card--primary">
          <div className="ev-conflict-card__badge">Priority Axis</div>
          <h3 className="ev-conflict-card__title">EV-1 Primary</h3>
          <dl className="ev-conflict-metrics">
            <div className="ev-conflict-metric">
              <dt className="ev-conflict-metric__label">Lane</dt>
              <dd className="ev-conflict-metric__value">{ev1.lane ?? '—'}</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt className="ev-conflict-metric__label">Distance</dt>
              <dd className="ev-conflict-metric__value">{ev1.distance_m ?? '—'} m</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt className="ev-conflict-metric__label">Speed</dt>
              <dd className="ev-conflict-metric__value">{ev1.speed_kmh ?? '—'} km/h</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt className="ev-conflict-metric__label">TTI</dt>
              <dd className="ev-conflict-metric__value">{ev1.tti_sec ?? '—'} s</dd>
            </div>
          </dl>
        </div>

        <div className="ev-conflict-card ev-conflict-card--secondary">
          <div className="ev-conflict-card__badge">Holding/Preempted</div>
          <h3 className="ev-conflict-card__title">EV-2 Secondary</h3>
          <dl className="ev-conflict-metrics">
            <div className="ev-conflict-metric">
              <dt className="ev-conflict-metric__label">Lane</dt>
              <dd className="ev-conflict-metric__value">{ev2.lane ?? '—'}</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt className="ev-conflict-metric__label">Distance</dt>
              <dd className="ev-conflict-metric__value">{ev2.distance_m ?? '—'} m</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt className="ev-conflict-metric__label">Speed</dt>
              <dd className="ev-conflict-metric__value">{ev2.speed_kmh ?? '—'} km/h</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt className="ev-conflict-metric__label">TTI</dt>
              <dd className="ev-conflict-metric__value">{ev2.tti_sec ?? '—'} s</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="ev-conflict-tracker">
        <h3 className="ev-conflict-tracker__title">3-Stage Preemption Tracker</h3>
        <ol className="ev-conflict-stages">
          {stages.map((stage) => (
            <li
              key={stage.id}
              className={`ev-conflict-stage ${getStageClass(stage.id)}`}
            >
              <span className="ev-conflict-stage__number">{stage.id}</span>
              <span className="ev-conflict-stage__label">{stage.label}</span>
              {stage.subLabel && (
                <span className="ev-conflict-stage__sub-label">{stage.subLabel}</span>
              )}
            </li>
          ))}
        </ol>
      </div>

      {engineData.downstream_green_wave && (
        <div className="ev-conflict-green-wave">
          Downstream Green-Wave Webhook: ACTIVE
        </div>
      )}
    </section>
  );
}