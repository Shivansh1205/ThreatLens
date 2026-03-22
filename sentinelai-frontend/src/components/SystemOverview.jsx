export default function SystemOverview({ dashboard }) {
  if (!dashboard) return null;

  return (
    <section className="card">
      <h2 className="section-title">📊 System Overview</h2>
      <div className="overview-stats">
        <div className="stat-box">
          <span className="stat-value">{dashboard.total_users}</span>
          <span className="stat-label">Total Users</span>
        </div>
        <div className="stat-box stat-box--threat">
          <span className="stat-value">{dashboard.active_threats}</span>
          <span className="stat-label">Active Threats</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{dashboard.recent_alerts.length}</span>
          <span className="stat-label">Alerts (24h)</span>
        </div>
      </div>
    </section>
  );
}
