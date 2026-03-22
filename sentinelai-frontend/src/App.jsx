import { useState, useEffect, useRef } from "react";
import { API } from "./api";
import SystemOverview from "./components/SystemOverview";
import HotThreats from "./components/HotThreats";
import UserBehavior from "./components/UserBehavior";
import Alerts from "./components/Alerts";
import Chat from "./components/Chat";

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [liveAlerts, setLiveAlerts] = useState([]);
  const wsRef = useRef(null);

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

    // WebSocket for live alerts
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/alerts");
    wsRef.current = ws;
    ws.onmessage = (e) => {
      const incoming = JSON.parse(e.data);
      if (incoming.length > 0) {
        setLiveAlerts(incoming);
      }
    };

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  const mergedAlerts = liveAlerts.length > 0 ? liveAlerts : alerts;

  return (
    <div className="app">
      <header className="header">
        <h1>ThreatLens</h1>
        <span className="subtitle">Adaptive Behavior-Based Intrusion Detection System</span>
      </header>

      <main className="main">
        <SystemOverview dashboard={dashboard} />
        <HotThreats alerts={mergedAlerts} />
        <UserBehavior users={dashboard?.high_risk_users ?? []} />
        <Alerts alerts={alerts} loading={loading} error={error} />
        <Chat />
      </main>
    </div>
  );
}
