import { Activity, AlertTriangle, ShieldAlert, Users } from "lucide-react"
import { Card, CardContent } from "./ui/card"

export default function HeroSummary({ dashboard }) {
  if (!dashboard) return null

  const stats = [
    {
      title: "Total Alerts (24h)",
      value: dashboard.recent_alerts?.length || 0,
      icon: Activity,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
      shadow: "shadow-glow-primary",
    },
    {
      title: "Active Threats",
      value: dashboard.active_threats || 0,
      icon: ShieldAlert,
      color: "text-danger",
      bg: "bg-danger/10",
      shadow: "shadow-glow-danger",
    },
    {
      title: "Total Users",
      value: dashboard.total_users || 0,
      icon: Users,
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
    },
    {
      title: "Suspicious Activity",
      value: dashboard.high_risk_users?.length || 0,
      icon: AlertTriangle,
      color: "text-warning",
      bg: "bg-warning/10",
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, i) => {
        const Icon = stat.icon
        return (
          <Card key={i} className="relative overflow-hidden group hover:border-white/10 transition-colors">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <p className="text-sm font-medium text-zinc-400">{stat.title}</p>
                  <p className="text-3xl font-bold tracking-tight text-white">
                    {stat.value}
                  </p>
                </div>
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${stat.bg} ${stat.color} ${stat.shadow || ''}`}>
                  <Icon size={24} />
                </div>
              </div>
            </CardContent>
            {/* Soft bottom glow line */}
            <div className={`absolute bottom-0 left-0 h-[2px] w-full ${stat.bg} opacity-0 transition-opacity group-hover:opacity-100`} />
          </Card>
        )
      })}
    </div>
  )
}
