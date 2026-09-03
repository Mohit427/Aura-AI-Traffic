import './EVConflictPanel.css';

const STAGE_META = [
  { id: 1, label: 'Active lane flush', tag: 'EV-1' },
  { id: 2, label: 'All-red safe clearance', tag: '' },
  { id: 3, label: 'Secondary axis corridor', tag: 'EV-2' },
];

export default function EVConflictPanel({ engineData }) {
  if (engineData?.priority_mode !== 'emergency_vehicle' || !engineData?.ev_data) {
    return null;
  }

  const ev1 = engineData.ev_data.ev1 ?? {};
  const ev2 = engineData.ev_data.ev2 ?? {};
  const activeStage = Number(engineData.ev_stage) || 0;

  const stageStatus = (stageId) => {
    if (stageId === activeStage) return 'active';
    if (stageId < activeStage) return 'done';
    return 'pending';
  };

  return (
    <section className="ev-conflict-panel">
      <header className="ev-conflict-header">
        <span className="ev-conflict-kicker">
          <span className="ev-conflict-pulse-dot" aria-hidden="true" />
          Emergency preemption active
        </span>
        <h2 className="ev-conflict-title">Dual emergency vehicle conflict resolution</h2>
      </header>

      <div className="ev-conflict-grid">
        <article className="ev-conflict-card ev-conflict-card--go">
          <div className="ev-conflict-card__head">
            <span className="ev-conflict-card__badge">Flushing now</span>
            <h3 className="ev-conflict-card__title">EV-1 · Primary</h3>
          </div>
          <dl className="ev-conflict-metrics">
            <div className="ev-conflict-metric">
              <dt>Lane</dt>
              <dd>{ev1.lane ?? '—'}</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt>Distance</dt>
              <dd>{ev1.distance_m ?? '—'} m</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt>Speed</dt>
              <dd>{ev1.speed_kmh ?? '—'} km/h</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt>TTI</dt>
              <dd>{ev1.tti_sec ?? '—'} s</dd>
            </div>
          </dl>
        </article>

        <article className="ev-conflict-card ev-conflict-card--hold">
          <div className="ev-conflict-card__head">
            <span className="ev-conflict-card__badge">Holding</span>
            <h3 className="ev-conflict-card__title">EV-2 · Secondary</h3>
          </div>
          <dl className="ev-conflict-metrics">
            <div className="ev-conflict-metric">
              <dt>Lane</dt>
              <dd>{ev2.lane ?? '—'}</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt>Distance</dt>
              <dd>{ev2.distance_m ?? '—'} m</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt>Speed</dt>
              <dd>{ev2.speed_kmh ?? '—'} km/h</dd>
            </div>
            <div className="ev-conflict-metric">
              <dt>TTI</dt>
              <dd>{ev2.tti_sec ?? '—'} s</dd>
            </div>
          </dl>
        </article>
      </div>

      <div className="ev-conflict-tracker">
        <h3 className="ev-conflict-tracker__title">3-stage preemption tracker</h3>
        <ol className="ev-conflict-stages">
          {STAGE_META.map((stage) => (
            <li
              key={stage.id}
              className={`ev-conflict-stage ev-conflict-stage--${stageStatus(stage.id)}`}
            >
              <span className="ev-conflict-stage__number">{stage.id}</span>
              <span className="ev-conflict-stage__label">
                {stage.label}
                {stage.tag && <span className="ev-conflict-stage__sub-label">{stage.tag}</span>}
              </span>
            </li>
          ))}
        </ol>
      </div>

      {engineData.downstream_green_wave && (
        <div className="ev-conflict-green-wave">
          <span aria-hidden="true" />
          Downstream green-wave webhook active
        </div>
      )}
    </section>
  );
}
