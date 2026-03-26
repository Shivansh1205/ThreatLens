import { useState, useRef, useEffect } from "react"
import { API } from "../api"
import { Send, Bot, User, Sparkles, RefreshCcw } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "./ui/card"
import { Button } from "./ui/button"

export default function ThreatAssistant() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [options, setOptions] = useState(null)
  const [context, setContext] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [started, setStarted] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, loading, options])

  const sendMessage = async (query, selectedContext) => {
    setMessages(prev => [...prev, { role: "user", text: query }])
    setOptions(null)
    setLoading(true)

    try {
      const res = await API.post("/chat", {
        query,
        session_id: sessionId,
        context: selectedContext,
      })

      const answer = res.data?.answer || "No response from backend."
      const newOptions = res.data?.options || null
      const newSessionId = res.data?.session_id || sessionId

      setMessages(prev => [...prev, { role: "assistant", text: answer }])
      setOptions(newOptions?.length ? newOptions : null)
      setSessionId(newSessionId)
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: "assistant", text: "Error connecting to AI service. Please verify backend." },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleStart = () => {
    setStarted(true)
    sendMessage("start", null)
  }

  const handleOptionClick = (option) => {
    if (option.includes("Back to menu")) {
      setContext(null)
      sendMessage("start", null)
      return
    }
    if (option.includes("Ask another question")) {
      setOptions(null)
      return
    }
    setContext(option)
    sendMessage(option, option)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    const q = input.trim()
    setInput("")
    sendMessage(q, context)
  }

  return (
    <Card className="flex flex-col h-[600px] border-primary/20 bg-panel shadow-glow-primary relative overflow-hidden">
      {/* Decorative gradient background */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 h-32 w-32 rounded-full bg-primary/10 blur-3xl pointer-events-none" />

      <CardHeader className="border-b border-primary/10 bg-primary/5 pb-4">
        <div className="flex items-center gap-2">
          <Bot className="text-primary" size={20} />
          <CardTitle className="text-primary">AI Threat Assistant</CardTitle>
          <span className="ml-auto flex h-2 w-2 rounded-full bg-primary animate-pulse" />
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar" ref={scrollRef}>
        {!started ? (
          <div className="flex h-full flex-col items-center justify-center space-y-6 text-center">
            <div className="rounded-full bg-primary/10 p-4 ring-1 ring-primary/20 shadow-glow-primary">
              <Sparkles className="text-primary h-8 w-8" />
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold text-lg text-white">SOC Copilot</h3>
              <p className="text-sm text-zinc-400 max-w-[250px]">
                Ask me to investigate users, summarize threats, or explain anomalies.
              </p>
            </div>
            <Button onClick={handleStart} className="w-full max-w-[200px] gap-2">
              Initialize Session
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`flex gap-3 max-w-[85%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                  <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${msg.role === "user" ? "bg-white/10 text-white" : "bg-primary/20 text-primary border border-primary/30"}`}>
                    {msg.role === "user" ? <User size={14} /> : <Bot size={14} />}
                  </div>
                  <div className={`rounded-xl px-4 py-2.5 text-sm ${
                    msg.role === "user" 
                      ? "bg-primary text-white" 
                      : "bg-white/5 text-zinc-300 border border-white/10"
                  }`}>
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="flex gap-3 max-w-[85%] flex-row">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary border border-primary/30">
                    <Bot size={14} />
                  </div>
                  <div className="rounded-xl px-4 py-3 bg-white/5 border border-white/10">
                    <div className="flex gap-1.5 pt-1 text-primary">
                      <span className="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="h-1.5 w-1.5 rounded-full bg-current animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {options && !loading && (
              <div className="flex flex-col gap-2 mt-4 ml-11">
                {options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => handleOptionClick(opt)}
                    className="text-left py-2 px-3 rounded-lg text-sm bg-white/[0.03] hover:bg-white/10 border border-white/5 text-primary hover:text-white transition-colors"
                  >
                    {opt}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>

      {started && !options && (
        <CardFooter className="p-3 border-t border-white/5 bg-black/20">
          <form onSubmit={handleSubmit} className="flex w-full items-end gap-2">
            <div className="relative flex-1">
              <input
                className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 pr-10 text-sm text-zinc-200 placeholder-zinc-500 focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/50"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                autoFocus
              />
            </div>
            <Button type="submit" size="icon" disabled={loading || !input.trim()} className="h-[46px] w-[46px] rounded-xl shrink-0">
              <Send size={18} className={input.trim() && !loading ? "text-white" : "text-white/50"} />
            </Button>
          </form>
        </CardFooter>
      )}
    </Card>
  )
}
