import { Home, ShieldAlert, Users, Bell, MessageSquare, BarChart, Settings, LayoutDashboard } from "lucide-react"

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "threats", label: "Threat Feed", icon: ShieldAlert },
    { id: "users", label: "User Analytics", icon: Users },
    { id: "alerts", label: "Alerts", icon: Bell },
    { id: "assistant", label: "Assistant", icon: MessageSquare },
    { id: "reports", label: "Reports", icon: BarChart },
    { id: "settings", label: "Settings", icon: Settings },
  ]

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-white/5 bg-[#0B0F19] transition-transform">
      <div className="flex h-full flex-col overflow-y-auto px-4 py-6 text-zinc-400">
        <div className="mb-8 flex items-center justify-center gap-3 px-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/20 text-primary shadow-glow-primary">
            <ShieldAlert size={24} />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">ThreatLens</span>
        </div>
        
        <div className="space-y-2 font-medium">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 transition-colors ${
                  isActive
                    ? "bg-primary/10 text-primary shadow-[inset_4px_0_0_0_#3B82F6]"
                    : "hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </div>
      </div>
    </aside>
  )
}
