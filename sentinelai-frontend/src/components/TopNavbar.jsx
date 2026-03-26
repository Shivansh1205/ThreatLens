import { Bell, Search, User } from "lucide-react"

export default function TopNavbar({ searchQuery, setSearchQuery }) {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-white/5 bg-[#0B0F19]/80 px-8 backdrop-blur-md">
      <div className="flex w-full items-center justify-between">
        
        {/* Search */}
        <div className="relative flex w-1/3 items-center">
          <Search className="absolute left-3 text-zinc-500" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search threats, users, IPs..."
            className="h-10 w-full rounded-full border border-white/10 bg-black/20 pl-10 pr-4 text-sm text-zinc-200 placeholder-zinc-500 focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
          />
        </div>

        {/* Right Nav */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 rounded-full border border-success/20 bg-success/10 px-3 py-1.5 text-xs font-semibold text-success">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-success"></span>
            </span>
            System Secure
          </div>

          <button className="relative text-zinc-400 hover:text-white transition-colors">
            <Bell size={20} />
            <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-danger text-[10px] font-bold text-white shadow-glow-danger">
              3
            </span>
          </button>
          
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-zinc-300 ring-2 ring-primary/20 backdrop-blur-sm cursor-pointer hover:bg-white/20 transition-colors">
            <User size={18} />
          </div>
        </div>
      </div>
    </header>
  )
}
