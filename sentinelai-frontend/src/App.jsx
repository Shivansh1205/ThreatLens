import { useState, useEffect, useRef } from "react";
import { Toaster, toast } from "react-hot-toast";
import { API } from "./api";
import SystemOverview from "./components/SystemOverview";
import RiskChart from "./components/RiskChart";
import TopUsers from "./components/TopUsers";
import UserBehavior from "./components/UserBehavior";
import Alerts from "./components/Alerts";
import Chat from "./components/Chat";

const fireToast = (alert) => {
  const msg = `🚨 ${alert.user_id} — Risk: ${alert.risk_score}`;
  if (alert.risk_score >= 80) toast.error(msg, { duration: 5000 });
  else if (alert.risk_score >= 60) toast(msg, { icon: "⚠️", duration: 4000, style: { background: "#744210", color: "#fefcbf" } });
  else toast.success(msg, { duration: 3000 });
};

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  const fetchDashboard = () => {
    API.get("/dashboard")
      .then((res) => setDashboard(res.data))
      .catch(() => {});
  };

  const fetchData = () => {
    Promise.all([API.get("/alerts"), API.get("/dashboard")])
      .then(([alertsRes, dashRes]) => {
        setAlerts(alertsRes.data);
        setDashboard(dashRes.data);
        setError(null);
      })
      .catch(() => setError("Failed to fetch data. Is the backend running?"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);

    const ws = new WebSocket("ws://127.0.0.1:8000/alerts/ws/alerts");
    wsRef.current = ws;
    ws.onmessage = (e) => {
      const incoming = JSON.parse(e.data);
      setAlerts((prev) => {
        if (prev.some((a) => a.id === incoming.id)) return prev;
        return [incoming, ...prev];
      });
      fetchDashboard();
      fireToast(incoming);
    };
    ws.onopen = () => ws.send("connected");
    ws.onerror = () => console.warn("WebSocket unavailable, falling back to polling");

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  return (
    <div className="app">
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: "#2d3748", color: "#e2e8f0", fontSize: "0.88rem" },
        }}
      />
      <header className="header">
        <h1>🛡️ ThreatLens</h1>
        <span className="subtitle">Adaptive Behavior-Based Intrusion Detection System</span>
      </header>

      <main className="main">
        <SystemOverview dashboard={dashboard} />

        <div className="grid-2">
          <RiskChart alerts={alerts} />
          <TopUsers alerts={alerts} />
        </div>

        <UserBehavior users={dashboard?.high_risk_users ?? []} />
        <Alerts alerts={alerts} loading={loading} error={error} />
      </main>

      <Chat />
    </div>
  );
}
