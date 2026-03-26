import { Users, UserX, UserMinus, UserCheck } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"

const getBehaviorDetails = (label) => {
  switch (label?.toLowerCase()) {
    case "high-risk": return { icon: UserX, variant: "danger", text: "High Risk" }
    case "suspicious": return { icon: UserMinus, variant: "warning", text: "Suspicious" }
    case "normal": return { icon: UserCheck, variant: "success", text: "Normal" }
    default: return { icon: Users, variant: "outline", text: "Unknown" }
  }
}

export default function UserBehavior({ users, limit, searchQuery = "" }) {
  const filteredUsers = (users || []).filter(u => 
    !searchQuery || 
    u.user_id.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (u.usual_ip && u.usual_ip.toLowerCase().includes(searchQuery.toLowerCase()))
  ).sort((a, b) => b.risk_score - a.risk_score)

  const displayUsers = limit ? filteredUsers.slice(0, limit) : filteredUsers

  return (
    <Card className="flex flex-col h-full bg-panel">
      <CardHeader className="border-b border-white/5 pb-4 sticky top-0 bg-panel z-10">
        <div className="flex items-center gap-2">
          <Users className="text-accent" size={20} />
          <CardTitle>User Behavior Profiling</CardTitle>
          <Badge variant="outline" className="ml-auto">{displayUsers.length} Users</Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto p-0 no-scrollbar">
        {displayUsers.length === 0 ? (
          <div className="flex h-[200px] flex-col items-center justify-center space-y-3 p-8 text-center bg-black/20">
            <div className="rounded-full bg-white/5 p-4">
              <Users className="text-zinc-600" size={32} />
            </div>
            <p className="text-sm font-medium text-zinc-400">No anomalous user behavior identified.</p>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {displayUsers.map((u) => {
              const details = getBehaviorDetails(u.behavior_label)
              const Icon = details.icon
              return (
                <div key={u.user_id} className="flex items-center justify-between p-4 hover:bg-white/[0.02] transition-colors relative">
                  <div className={`absolute left-0 top-0 h-full w-[3px] bg-${details.variant} opacity-30`} />
                  <div className="flex items-center gap-4">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/5 text-zinc-400 border border-white/10 shrink-0">
                      <Icon size={16} />
                    </div>
                    <div>
                      <h4 className="font-semibold text-zinc-200">{u.user_id}</h4>
                      <p className="text-xs text-zinc-500 font-mono">{u.usual_ip || "Unknown IP"}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Badge variant={details.variant}>{details.text}</Badge>
                    <div className="flex flex-col items-end">
                      <span className="text-xs text-zinc-500">Score</span>
                      <span className="text-sm font-semibold font-mono text-zinc-300">{u.risk_score}/100</span>
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
