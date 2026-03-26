import { useState, useEffect, useRef } from "react"
import { API } from "./api"

import Sidebar from "./components/Sidebar"
import TopNavbar from "./components/TopNavbar"
import HeroSummary from "./components/HeroSummary"
import HotThreats from "./components/HotThreats"
import UserBehavior from "./components/UserBehavior"
import Alerts from "./components/Alerts"
import ThreatAssistant from "./components/ThreatAssistant"
import Charts from "./components/Charts"

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard")
  const [searchQuery, setSearchQuery] = useState("")
  
  const [alerts, setAlerts] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [users, setUsers] = useState([])
  
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [liveAlerts, setLiveAlerts] = useState([])
  const wsRef = useRef(null)

  const fetchData = () => {
    Promise.all([
      API.get("/alerts"), 
      API.get("/dashboard"),
      API.get("/users").catch(() => ({ data: [] })) // Fallback if backend not updated yet
    ])
      .then(([alertsRes, dashRes, usersRes]) => {
        setAlerts(alertsRes.data)
        setDashboard(dashRes.data)
        setUsers(usersRes.data)
        setError(null)
      })
      .catch(() => setError("Failed to fetch data. Is the backend running?"))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000)

    const ws = new WebSocket("ws://127.0.0.1:8000/ws/alerts")
    wsRef.current = ws
    ws.onmessage = (e) => {
      try {
        const incoming = JSON.parse(e.data)
        if (incoming.length > 0) setLiveAlerts(incoming)
      } catch (err) {
         // ignore parse error 
      }
    }

    return () => {
      clearInterval(interval)
      if (ws.readyState === 1 || ws.readyState === 0) ws.close()
    }
  }, [])

  const mergedAlerts = liveAlerts.length > 0 ? liveAlerts : alerts

  const renderContent = () => {
    switch(activeTab) {
      case "dashboard":
        return (
          <>
            <div className="flex flex-col gap-2 mb-2">
              <h1 className="text-3xl font-bold tracking-tight text-white">System Overview</h1>
              <p className="text-sm text-zinc-500">
                Monitor and analyze active threats across your infrastructure in real-time.
              </p>
            </div>

            <HeroSummary dashboard={dashboard} />
            <Charts alerts={mergedAlerts} />

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 lg:h-[600px]">
              <div className="flex flex-col gap-6 h-full">
                <div className="flex-1">
                  <HotThreats alerts={mergedAlerts} limit={3} searchQuery={searchQuery} />
                </div>
                <div className="flex-1">
                  <UserBehavior users={dashboard?.high_risk_users ?? []} limit={5} searchQuery={searchQuery} />
                </div>
              </div>
              <div className="h-full">
                <ThreatAssistant />
              </div>
            </div>

            <div className="pt-2">
              <Alerts alerts={mergedAlerts} loading={loading} error={error} searchQuery={searchQuery} />
            </div>
          </>
        )

      case "threats":
        return (
          <div className="space-y-6">
            <div className="flex flex-col gap-2 mb-2">
              <h1 className="text-3xl font-bold tracking-tight text-white">Live Threat Feed</h1>
              <p className="text-sm text-zinc-500">Real-time stream of all detected anomalous activities.</p>
            </div>
            <HotThreats alerts={mergedAlerts} searchQuery={searchQuery} />
          </div>
        )

      case "users":
        return (
          <div className="space-y-6">
            <div className="flex flex-col gap-2 mb-2">
              <h1 className="text-3xl font-bold tracking-tight text-white">User Analytics</h1>
              <p className="text-sm text-zinc-500">Comprehensive behavioral profiling and risk scoring.</p>
            </div>
            <UserBehavior users={users.length > 0 ? users : (dashboard?.high_risk_users ?? [])} searchQuery={searchQuery} />
          </div>
        )

      case "alerts":
        return (
          <div className="space-y-6">
            <div className="flex flex-col gap-2 mb-2">
              <h1 className="text-3xl font-bold tracking-tight text-white">All Alerts</h1>
              <p className="text-sm text-zinc-500">Historical log of all system warnings and critical alerts.</p>
            </div>
            <Alerts alerts={mergedAlerts} loading={loading} error={error} searchQuery={searchQuery} />
          </div>
        )

      case "assistant":
        return (
          <div className="space-y-6 h-full flex flex-col">
            <div className="flex flex-col gap-2 mb-2">
              <h1 className="text-3xl font-bold tracking-tight text-white">Threat Assistant</h1>
              <p className="text-sm text-zinc-500">AI-powered Copilot for SOC investigation and query.</p>
            </div>
            <div className="flex-1 w-full max-w-5xl mx-auto h-[700px]">
              <ThreatAssistant />
            </div>
          </div>
        )

      case "reports":
      case "settings":
        return (
          <div className="flex h-[400px] flex-col items-center justify-center space-y-4 rounded-xl border border-white/5 bg-panel mt-10">
            <div className="rounded-full bg-white/5 p-4 ring-1 ring-white/10">
              <h2 className="text-xl font-semibold text-zinc-300 capitalize">{activeTab} Coming Soon</h2>
            </div>
            <p className="text-sm text-zinc-500">This module is currently under development.</p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="flex h-screen w-full bg-background text-zinc-300 font-sans selection:bg-primary/30">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <div className="ml-64 flex flex-1 flex-col overflow-hidden">
        <TopNavbar searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
        
        <main className="flex-1 overflow-y-auto bg-[#0B0F19] p-8 no-scrollbar">
          <div className="mx-auto max-w-7xl pb-12">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  )
}
