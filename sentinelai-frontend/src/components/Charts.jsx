import { useMemo } from "react"
import { BarChart as BarGraphic, Activity } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts"

const COLORS = {
  high: "#EF4444",
  medium: "#F59E0B",
  low: "#10B981"
}

export default function Charts({ alerts }) {
  // Process alerts for charts
  const { activityData, severityData } = useMemo(() => {
    if (!alerts || alerts.length === 0) return { activityData: [], severityData: [] }

    // Aggregate activity by hour
    const hourCounts = {}
    let highCount = 0
    let medCount = 0
    let lowCount = 0

    alerts.forEach(a => {
      // Activity
      const date = a.timestamp ? new Date(a.timestamp) : new Date()
      // Use hour formatting (e.g. "14:00")
      const hour = `${date.getHours().toString().padStart(2, "0")}:00`
      hourCounts[hour] = (hourCounts[hour] || 0) + 1

      // Severity
      if (a.risk_score >= 60) highCount++
      else if (a.risk_score >= 30) medCount++
      else lowCount++
    })

    const activity = Object.keys(hourCounts)
      .sort((a, b) => a.localeCompare(b))
      .map(time => ({ time, threats: hourCounts[time] }))

    const severity = [
      { name: "High Risk", value: highCount, color: COLORS.high },
      { name: "Medium Risk", value: medCount, color: COLORS.medium },
      { name: "Low Risk", value: lowCount, color: COLORS.low },
    ].filter(s => s.value > 0)

    return { activityData: activity, severityData: severity }
  }, [alerts])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Activity Timeline */}
      <Card className="col-span-1 lg:col-span-2 bg-panel flex flex-col h-[350px]">
        <CardHeader className="border-b border-white/5 pb-4">
          <div className="flex items-center gap-2">
            <Activity className="text-primary" size={20} />
            <CardTitle>Threat Activity Trend</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="flex-1 p-6">
          {activityData.length === 0 ? (
            <div className="flex h-full items-center justify-center text-zinc-500">
              No activity data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorThreats" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis dataKey="time" stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151" }}
                  itemStyle={{ color: "#e4e4e7" }}
                />
                <Area 
                  type="monotone" 
                  dataKey="threats" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorThreats)" 
                  animationDuration={1500}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Severity Breakdown */}
      <Card className="col-span-1 bg-panel flex flex-col h-[350px]">
        <CardHeader className="border-b border-white/5 pb-4">
          <div className="flex items-center gap-2">
            <BarGraphic className="text-accent" size={20} />
            <CardTitle>Severity Breakdown</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="flex-1 p-6">
          {severityData.length === 0 ? (
            <div className="flex h-full items-center justify-center text-zinc-500">
              No severity data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                  animationDuration={1500}
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", borderRadius: "8px" }}
                  itemStyle={{ color: "#e4e4e7" }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: "12px", paddingTop: "20px" }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
