import { ShieldAlert, Crosshair } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"

const getSeverity = (score) => {
  if (score >= 90) return { label: "CRITICAL", variant: "danger" } 
  if (score >= 60) return { label: "HIGH", variant: "warning" }
  if (score >= 30) return { label: "MEDIUM", variant: "accent" }
  return { label: "LOW", variant: "success" }
}

export default function HotThreats({ alerts, limit, searchQuery = "" }) {
  const filtered = [...(alerts || [])]
    .filter(a => 
      !searchQuery || 
      a.user_id.toLowerCase().includes(searchQuery.toLowerCase()) || 
      a.ip.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => b.risk_score - a.risk_score)

  const top = limit ? filtered.slice(0, limit) : filtered

  return (
    <Card className="flex flex-col h-full bg-panel">
      <CardHeader className="border-b border-white/5 pb-4 sticky top-0 bg-panel z-10">
        <div className="flex items-center gap-2">
          <ShieldAlert className="text-danger" size={20} />
          <CardTitle>Hot Threats</CardTitle>
          <Badge variant="outline" className="ml-auto">{top.length} Found</Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto p-0 no-scrollbar">
        {top.length === 0 ? (
          <div className="flex h-[200px] flex-col items-center justify-center space-y-3 p-8 text-center bg-black/20">
            <div className="rounded-full bg-white/5 p-4">
              <ShieldAlert className="text-zinc-600" size={32} />
            </div>
            <p className="text-sm font-medium text-zinc-400">No active threats detected across monitored endpoints.</p>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {top.map((alert) => {
              const severity = getSeverity(alert.risk_score)
              return (
                <div key={alert.id} className="group p-5 hover:bg-white/[0.02] transition-colors relative">
                  <div className={`absolute left-0 top-0 h-full w-[3px] bg-${severity.variant} opacity-50`} />
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-danger/10 text-danger border border-danger/20 shadow-glow-danger shrink-0">
                        <Crosshair size={18} />
                      </div>
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-zinc-200">{alert.user_id}</span>
                          <span className="text-xs text-zinc-500">[{alert.ip}]</span>
                        </div>
                        <p className="text-sm text-zinc-400 line-clamp-2 pr-4">{alert.explanation || alert.action}</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2 shrink-0">
                      <Badge variant={severity.variant}>{severity.label}</Badge>
                      <span className="text-xs font-mono text-zinc-500">Score: {alert.risk_score}</span>
                    </div>
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
