const labelColor = { "high-risk": "#fc8181", suspicious: "#f6ad55", normal: "#68d391" };
const labelIcon = { "high-risk": "🔴", suspicious: "🟡", normal: "🟢" };

export default function UserBehavior({ users }) {
  if (!users || users.length === 0)
    return (
      <section className="card">
        <h2 className="section-title">🧠 User Behavior</h2>
        <p className="muted">No high-risk or suspicious users detected.</p>
      </section>
    );

  return (
    <section className="card">
      <h2 className="section-title">🧠 User Behavior</h2>
      <div className="behavior-list">
        {users.map((u) => (
          <div key={u.user_id} className="behavior-row">
            <span className="behavior-icon">{labelIcon[u.behavior_label] ?? "⚪"}</span>
            <span className="behavior-user">{u.user_id}</span>
            <span className="behavior-label" style={{ color: labelColor[u.behavior_label] ?? "#e2e8f0" }}>
              {u.behavior_label}
            </span>
            <span className="behavior-ip">{u.usual_ip ?? "—"}</span>
            <span className="behavior-score">Score: {u.risk_score}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
