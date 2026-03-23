import { useState } from "react";
import { API } from "../api";

export default function Chat() {
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

    console.log("Sending query:", query, "context:", selectedContext);

    try {
      const res = await API.post("/chat", {
        query,
        session_id: sessionId,
        context: selectedContext,
      });

      console.log("Response:", res.data);

      const answer = res.data?.answer || "No response from backend.";
      const newOptions = res.data?.options || null;
      const newSessionId = res.data?.session_id || sessionId;

      setMessages((prev) => [...prev, { role: "assistant", text: answer }]);
      setOptions(newOptions?.length ? newOptions : null);
      setSessionId(newSessionId);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Error connecting to backend. Is it running?" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = () => {
    setStarted(true);
    sendMessage("start", null);
  };

  const handleOptionClick = (option) => {
    if (option === "🏠 Back to menu") {
      setContext(null);
      sendMessage("start", null);
      return;
    }
    if (option === "🔁 Ask another question") {
      setOptions(null);
      return;
    }
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
    <section className="card">
      <h2 className="section-title">💬 Threat Assistant</h2>

      {!started ? (
        <div className="chat-start">
          <p className="muted">Ask me anything about your system's security posture.</p>
          <button className="chat-btn" onClick={handleStart}>
            Start Chat
          </button>
        </div>
      ) : (
        <>
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble chat-bubble--${msg.role}`}>
                <span className="chat-bubble-label">
                  {msg.role === "user" ? "You" : "ThreatLens"}
                </span>
                <p>{msg.text}</p>
              </div>
            ))}
            {loading && (
              <div className="chat-bubble chat-bubble--assistant">
                <span className="chat-bubble-label">ThreatLens</span>
                <p className="muted">Thinking...</p>
              </div>
            )}
          </div>

          {options && !loading && (
            <div className="chat-options">
              {options.map((opt, i) => (
                <button key={i} className="chat-option-btn" onClick={() => handleOptionClick(opt)}>
                  {opt}
                </button>
              ))}
            </div>
          )}

          {!options && (
            <form className="chat-form" onSubmit={handleSubmit}>
              <input
                className="chat-input"
                type="text"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                autoFocus
              />
              <button className="chat-btn" type="submit" disabled={loading}>
                {loading ? "Thinking..." : "Send"}
              </button>
            </form>
          )}
        </>
      )}
    </section>
  );
}
