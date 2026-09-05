import { useEffect, useState } from 'react';
import './AdvisorPanel.css';

const API_BASE_URL = 'https://aura-backend-v27b.onrender.com';

export default function AdvisorPanel({ engineData }) {
  const [explanation, setExplanation] = useState('');
  const [context, setContext] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!engineData) return;

    let isMounted = true;
    const token = import.meta.env.VITE_CORA_TOKEN;

    async function fetchExplanation() {
      setLoading(true);
      setError(null);

      try {
        const [explainResponse, contextResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/api/advisor/explain`, {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ engine_output: engineData }),
          }),
          fetch(`${API_BASE_URL}/api/search/context`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location: 'Vadapalani Junction, Chennai' }),
          }),
        ]);

        if (!explainResponse.ok) {
          throw new Error(`Advisor request failed: ${explainResponse.status} ${explainResponse.statusText}`);
        }

        const explainData = await explainResponse.json();
        const contextData = contextResponse.ok ? await contextResponse.json() : { events: [] };

        if (isMounted) {
          setExplanation(typeof explainData.explanation === 'string' ? explainData.explanation : JSON.stringify(explainData));
          setContext(contextData.events || []);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchExplanation();

    return () => {
      isMounted = false;
    };
  }, [engineData?.timestamp]);

  const alertTone =
    engineData?.priority_mode === 'emergency_vehicle'
      ? 'critical'
      : engineData?.priority_mode === 'vulnerable_user'
        ? 'warning'
        : 'neutral';

  return (
    <section className={`advisor-panel advisor-panel--${alertTone}`}>
      <div className="advisor-panel__rail" aria-hidden="true" />
      <div className="advisor-panel__content">
        <h2 className="advisor-panel__title">Advisor explanation</h2>
        <div className="advisor-panel__body">
          {loading && <p className="advisor-panel__status">Generating explanation…</p>}
          {error && (
            <p className="advisor-panel__status advisor-panel__status--error">
              <span className="advisor-panel__status-dot" aria-hidden="true" />
              {error}
            </p>
          )}
          {!loading && !error && (
            <p className="advisor-panel__explanation">
              {explanation || 'Waiting for advisor response…'}
            </p>
          )}
        </div>
        {!loading && context.length > 0 && (
          <div className="advisor-panel__context">
            <span className="advisor-panel__context-label">Live context — Tavily</span>
            <ul className="advisor-panel__context-list">
              {context.map((event, i) => (
                <li key={i} className="advisor-panel__context-item">{event.title}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
