import { BellRing, RefreshCw, AlertCircle } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"

const getSeverity = (score) => {
  if (score >= 80) return { label: "CRITICAL", variant: "danger" }
  if (score >= 60) return { label: "HIGH", variant: "warning" }
  if (score >= 30) return { label: "MEDIUM", variant: "accent" }
  return { label: "LOW", variant: "success" }
}

export default function Alerts({ alerts, loading, error, searchQuery = "" }) {
  const filteredAlerts = (alerts || []).filter(a => 
      !searchQuery || 
      a.user_id.toLowerCase().includes(searchQuery.toLowerCase()) || 
      a.ip.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (a.explanation && a.explanation.toLowerCase().includes(searchQuery.toLowerCase()))
    )

  return (
    <Card className="flex flex-col h-[600px] w-full bg-panel">
      <CardHeader className="border-b border-white/5 pb-4 sticky top-0 bg-panel/95 backdrop-blur z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BellRing className="text-primary" size={20} />
            <CardTitle>All Alerts</CardTitle>
          </div>
          <Badge variant="outline">{filteredAlerts.length} Total</Badge>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-y-auto p-0 no-scrollbar">
        {loading ? (
          <div className="flex h-full flex-col items-center justify-center space-y-4 p-8">
            <RefreshCw className="h-8 w-8 animate-spin text-primary/50" />
            <p className="text-sm text-zinc-400">Loading alerts...</p>
          </div>
        ) : error ? (
          <div className="flex h-[300px] flex-col items-center justify-center space-y-4 p-8 text-center bg-danger/5">
            <div className="rounded-full bg-danger/10 p-3 text-danger border border-danger/20">
              <AlertCircle size={24} />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-semibold text-danger">Connection Error</p>
              <p className="text-xs text-zinc-400">{error}</p>
            </div>
            <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry Connection
            </Button>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="flex h-[300px] flex-col items-center justify-center space-y-3 p-8 text-center">
            <BellRing className="text-zinc-600 mb-2" size={32} />
            <p className="text-sm font-medium text-zinc-400">No alerts found</p>
            <p className="text-xs text-zinc-500">System is currently operating normally.</p>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {filteredAlerts.map((alert) => {
              const severity = getSeverity(alert.risk_score)
              const reasons = Array.isArray(alert.reasons)
                ? alert.reasons
                : typeof alert.reasons === "string"
                ? alert.reasons.split("|").map(r => r.trim()).filter(Boolean)
                : []

              return (
                <div key={alert.id} className="group p-5 hover:bg-white/[0.02] transition-colors relative">
                  <div className={`absolute left-0 top-0 h-full w-[3px] bg-${severity.variant}`} />
                  
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className="font-semibold text-zinc-200">{alert.user_id}</span>
                      <span className="rounded bg-white/5 px-2 py-0.5 text-xs font-mono text-zinc-400 border border-white/10">
                        {alert.ip}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-zinc-500 shrink-0">
                        {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : "Just now"}
                      </span>
                      <Badge variant={severity.variant}>{severity.label}</Badge>
                    </div>
                  </div>

                  <div className="space-y-2 pl-1">
                    {alert.explanation && (
                      <p className="text-sm text-zinc-300">{alert.explanation}</p>
                    )}
                    
                    {reasons.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {reasons.map((r, i) => (
                          <span key={i} className="inline-flex items-center rounded-md bg-white/[0.03] px-2 py-1 text-[10px] font-medium text-zinc-500 border border-white/5">
                            {r}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
