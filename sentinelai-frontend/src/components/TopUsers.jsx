import { motion, AnimatePresence } from "framer-motion";

export default function TopUsers({ alerts }) {
  const seen = new Set();
  const top5 = [...alerts]
    .sort((a, b) => b.risk_score - a.risk_score)
    .filter(({ user_id }) => seen.has(user_id) ? false : seen.add(user_id))
    .slice(0, 5);

  return (
    <section className="card">
      <h2 className="section-title">⚠️ Top Risk Users</h2>
      {top5.length === 0 ? (
        <p className="muted">No threats detected.</p>
      ) : (
        <ul className="top-users-list">
          <AnimatePresence initial={false}>
            {top5.map((a) => {
              const isCritical = a.risk_score >= 80;
              const reasons = Array.isArray(a.reasons) ? a.reasons : [];
              return (
                <motion.li
                  key={a.user_id}
                  className={`top-user-item${isCritical ? " top-user-item--critical" : ""}`}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 16 }}
                  transition={{ duration: 0.3, ease: "easeOut" }}
                  layout
                >
                  <div className="top-user-header">
                    <span>{isCritical ? "🔴" : "🟡"}</span>
                    <strong>{a.user_id}</strong>
                    <span className="top-user-score">Score: {a.risk_score}</span>
                  </div>
                  <div className="top-user-ip">{a.ip}</div>
                  {reasons[0] && <div className="top-user-reason">{reasons[0]}</div>}
                </motion.li>
              );
            })}
          </AnimatePresence>
        </ul>
      )}
    </section>
  );
}
