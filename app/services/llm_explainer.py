# REQUIREMENT:
# Run local model before starting backend:
# ollama run mistral

import logging
import requests

logger = logging.getLogger("threatlens.llm")


def _format_alerts(alerts: list[dict]) -> str:
    if not alerts:
        return "No significant suspicious activity detected in the system."

    sorted_alerts = sorted(alerts, key=lambda a: a.get("risk_score", 0), reverse=True)
    lines = []
    for a in sorted_alerts[:5]:
        reasons = a.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [r.strip() for r in reasons.split("|") if r.strip()]
        reason_lines = "\n".join(f"  - {r}" for r in reasons) if reasons else "  - No specific reasons recorded"
        lines.append(
            f"User: {a['user_id']} | IP: {a['ip']} | Risk: {a['risk_score']}\n"
            f"Reasons:\n{reason_lines}"
        )
    return "\n\n".join(lines)


def _format_profile(profile: dict | None) -> str:
    if not profile:
        return "No profile data available for this user."
    usual_ips = profile.get("usual_ips", [])
    return (
        f"User: {profile['user_id']}\n"
        f"Known IPs: {', '.join(usual_ips) if usual_ips else 'None'}\n"
        f"Total Logins: {profile.get('total_logins', 0)}\n"
        f"Failed Logins: {profile.get('failed_logins', 0)}\n"
        f"Avg Login Hour: {profile.get('avg_hour', 'N/A')}\n"
        f"Last Seen: {profile.get('last_seen', 'N/A')}"
    )


def build_chat_prompt(query: str, alerts: list[dict], profile: dict | None) -> str:
    security_keywords = {
        "alert", "risk", "threat", "attack", "login", "ip", "port", "user",
        "brute", "suspicious", "hack", "intrusion", "endpoint", "scan",
        "failed", "unusual", "malicious", "breach", "vulnerability"
    }
    is_security_query = any(kw in query.lower() for kw in security_keywords)

    if not is_security_query:
        return f"""You are a helpful assistant. Answer the following question naturally and concisely.

Question: {query}"""

    alerts_text = _format_alerts(alerts)
    profile_text = _format_profile(profile)

    return f"""You are a senior cybersecurity analyst reporting directly to a system administrator.

Tone: Be concise and decisive. No unnecessary explanations. Identify risk clearly and give actionable steps immediately.

RULES:
- Use short, direct sentences
- Reference actual values: user IDs, IPs, risk scores, ports, reasons
- Identify attack patterns (brute-force, port scan, off-hours access, etc.) when evident
- Never use generic filler statements
- Prioritise actionable recommendations over explanation

RESPONSE FORMAT (always follow this structure):
Summary:
(1–2 lines, high-impact, name the user and risk score)

Analysis:
(2–4 lines max — what the data shows, what attack pattern it suggests)

Recommended Actions:
- Immediate action
- Preventive action
- Monitoring step

---

User Question:
{query}

---

Recent Alerts:
{alerts_text}

---

User Behavior Profile:
{profile_text}

---

Now respond using the format above. Be specific. Be brief.
"""


def call_ollama(prompt: str) -> str | None:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            timeout=120,
        )
        return response.json().get("response", "").strip() or None
    except Exception as e:
        print("Ollama error:", e)
        return None


def call_llm(prompt: str, fallback: str = "No response generated.") -> str:
    print("Using Ollama (Mistral)...")
    try:
        result = call_ollama(prompt)
        if result:
            return result.strip()
    except Exception as e:
        print("LLM ERROR:", e)
    return fallback


# alias used by chat route
build_context_prompt = build_chat_prompt
