import './DashboardShell.css';

export default function DashboardShell({ children }) {
  return (
    <div className="shell">
      <header className="shell-header">
        <div className="shell-brand">
          <span className="shell-brand-mark" />
          <div>
            <h1>AURA</h1>
            <p className="shell-subtitle">Vadapalani Junction — Live Control</p>
          </div>
        </div>
        <div className="shell-status">
          <span className="status-dot" />
          <span>SYSTEM ACTIVE</span>
        </div>
      </header>
      <main className="shell-grid">{children}</main>
    </div>
  );
}
