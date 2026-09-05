import { useEffect, useState } from 'react';
import './AdvisorPanel.css';

const API_BASE_URL = 'https://aura-backend-v27b.onrender.com';

export default function AdvisorPanel({ engineData }) {
  const [explanation, setExplanation] = useState('');
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
        const response = await fetch(`${API_BASE_URL}/api/advisor/explain`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ engine_output: engineData }),
        });

        if (!response.ok) {
          throw new Error(`Advisor request failed: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        if (isMounted) {
          setExplanation(typeof data.explanation === 'string' ? data.explanation : JSON.stringify(data));
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
  }, [engineData]);

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
      </div>
    </section>
  );
}
