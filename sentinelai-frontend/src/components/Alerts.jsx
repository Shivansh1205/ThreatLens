import { motion, AnimatePresence } from "framer-motion";

const getColor = (risk) => {
  if (risk < 30) return "green";
  if (risk < 60) return "orange";
  return "red";
};

function AlertCard({ alert }) {
  const color = getColor(alert.risk_score);
  const reasons = Array.isArray(alert.reasons)
    ? alert.reasons
    : typeof alert.reasons === "string"
    ? alert.reasons.split("|").map((r) => r.trim()).filter(Boolean)
    : [];

  return (
    <motion.div
      className="alert-card"
      style={{ borderLeftColor: color }}
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      layout
    >
      <div className="alert-header">
        <span className="alert-user">{alert.user_id}</span>
        <span className="alert-ip">{alert.ip}</span>
        <span className="alert-score" style={{ color }}>
          Risk: {alert.risk_score}
        </span>
        <span className="alert-time">
          {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : ""}
        </span>
      </div>

      {reasons.length > 0 && (
        <ul className="alert-reasons">
          {reasons.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      )}

      {alert.explanation && (
        <p className="alert-explanation">{alert.explanation}</p>
      )}
    </motion.div>
  );
}

export default function Alerts({ alerts, loading, error }) {
  return (
    <section className="card">
      <h2 className="section-title">🚨 All Alerts</h2>

      {loading && <p className="muted">Loading...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && alerts.length === 0 && (
        <p className="muted">No alerts found.</p>
      )}

      <div className="alert-list">
        <AnimatePresence initial={false}>
          {alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </AnimatePresence>
      </div>
    </section>
  );
}
