import { useState } from "react";
import { API } from "../api";

export default function Chat() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [options, setOptions] = useState(null);
  const [context, setContext] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);

  const sendMessage = async (query, selectedContext) => {
    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setOptions(null);
    setLoading(true);

    try {
      const res = await API.post("/chat", {
        query,
        session_id: sessionId,
        context: selectedContext,
      });

      const answer = res.data?.answer || "No response from backend.";
      const newOptions = res.data?.options || null;
      setMessages((prev) => [...prev, { role: "assistant", text: answer }]);
      setOptions(newOptions?.length ? newOptions : null);
      if (res.data?.session_id) setSessionId(res.data.session_id);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [...prev, { role: "assistant", text: "Error connecting to backend." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = () => {
    setStarted(true);
    sendMessage("start", null);
  };

  const handleOptionClick = (option) => {
    if (option === "🏠 Back to menu") { setContext(null); sendMessage("start", null); return; }
    if (option === "🔁 Ask another question") { setOptions(null); return; }
    setContext(option);
    sendMessage(option, option);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput("");
    sendMessage(q, context);
  };

  return (
    <>
      {open && (
        <div className="chat-window">
          <div className="chat-window-header">
            <span>💬 Threat Assistant</span>
            <button className="chat-close-btn" onClick={() => setOpen(false)}>✕</button>
          </div>

          <div className="chat-messages">
            {!started ? (
              <div className="chat-bubble chat-bubble--assistant">
                <span className="chat-bubble-label">ThreatLens</span>
                <p>Hey! I'm your security assistant. Click below to start.</p>
              </div>
            ) : (
              messages.map((msg, i) => (
                <div key={i} className={`chat-bubble chat-bubble--${msg.role}`}>
                  <span className="chat-bubble-label">{msg.role === "user" ? "You" : "ThreatLens"}</span>
                  <p>{msg.text}</p>
                </div>
              ))
            )}
            {loading && (
              <div className="chat-bubble chat-bubble--assistant">
                <span className="chat-bubble-label">ThreatLens</span>
                <p className="muted">Thinking...</p>
              </div>
            )}
          </div>

          {!started ? (
            <div className="chat-window-footer">
              <button className="chat-btn" style={{ width: "100%" }} onClick={handleStart}>Start Chat</button>
            </div>
          ) : options && !loading ? (
            <div className="chat-options">
              {options.map((opt, i) => (
                <button key={i} className="chat-option-btn" onClick={() => handleOptionClick(opt)}>{opt}</button>
              ))}
            </div>
          ) : (
            <form className="chat-window-footer" onSubmit={handleSubmit}>
              <input
                className="chat-input"
                type="text"
                placeholder="Type a message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                autoFocus
              />
              <button className="chat-btn" type="submit" disabled={loading}>➤</button>
            </form>
          )}
        </div>
      )}

      <button className="chat-fab" onClick={() => setOpen((o) => !o)}>
        {open ? "✕" : "💬"}
      </button>
    </>
  );
}
