import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = { Low: "#68d391", Medium: "#f6ad55", High: "#fc8181", Critical: "#9b2335" };
const ORDER = ["Low", "Medium", "High", "Critical"];

export default function RiskChart({ alerts }) {
  const counts = { Low: 0, Medium: 0, High: 0, Critical: 0 };

  alerts.forEach(({ risk_score }) => {
    if (risk_score >= 80) counts.Critical++;
    else if (risk_score >= 60) counts.High++;
    else if (risk_score >= 30) counts.Medium++;
    else counts.Low++;
  });

  const data = ORDER.filter((k) => counts[k] > 0).map((k) => ({ name: k, value: counts[k] }));

  return (
    <section className="card">
      <h2 className="section-title">🥧 Risk Distribution</h2>
      {data.length === 0 ? (
        <p className="muted">No alert data yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              cx="50%"
              cy="50%"
              outerRadius={90}
              isAnimationActive={true}
              animationDuration={800}
              animationEasing="ease-out"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={COLORS[entry.name]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ background: "#1a202c", border: "1px solid #2d3748", color: "#e2e8f0" }} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}
