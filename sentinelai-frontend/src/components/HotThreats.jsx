const getRiskIcon = (score) => {
  if (score >= 60) return "🔴";
  if (score >= 30) return "🟡";
  return "🟢";
};

export default function HotThreats({ alerts }) {
  const top3 = [...alerts]
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, 3);

  return (
    <section className="card">
      <h2 className="section-title">🔥 Hot Threats</h2>
      {top3.length === 0 ? (
        <p className="muted">No threats detected.</p>
      ) : (
        <ul className="threat-list">
          {top3.map((alert) => (
            <li key={alert.id} className="threat-item">
              <div className="threat-header">
                <span className="threat-icon">{getRiskIcon(alert.risk_score)}</span>
                <strong>{alert.user_id}</strong>
                <span className="threat-score">Score: {alert.risk_score}</span>
                <span className="threat-ip">{alert.ip}</span>
              </div>
              {alert.explanation && (
                <p className="threat-explanation">{alert.explanation}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
