import logging
import re
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.alert import Alert
from app.models.user_profile import UserProfile
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_explainer import build_chat_prompt, build_context_prompt, call_llm

logger = logging.getLogger("threatlens.routes.chat")
router = APIRouter()

MENU_OPTIONS = [
    "🔴 Show high-risk users",
    "🚨 Summarise recent alerts",
    "🔍 Investigate a specific user",
    "🌐 Check risky IPs or ports",
    "💬 Ask a custom question",
]

_STOPWORDS = {"why", "is", "the", "a", "an", "what", "how", "who", "risky",
              "user", "alert", "alerts", "about", "tell", "me", "show", "any"}


def _extract_user_id(query: str) -> str | None:
    for token in re.findall(r"[a-zA-Z0-9_\-]+", query):
        if token.lower() not in _STOPWORDS:
            return token
    return None


def _serialize_alert(alert: Alert) -> dict:
    reason_str = getattr(alert, "reasons", None) or getattr(alert, "reason", "") or ""
    try:
        import json
        reasons = json.loads(reason_str)
    except Exception:
        reasons = [r.strip() for r in reason_str.split(";") if r.strip()]
    return {
        "user_id":    alert.user_id,
        "ip":         alert.ip,
        "risk_score": alert.risk_score,
        "reasons":    reasons,
        "timestamp":  alert.timestamp.isoformat() if alert.timestamp else None,
    }


def _serialize_profile(profile: UserProfile) -> dict:
    return {
        "user_id":       profile.user_id,
        "usual_ips":     [profile.usual_ip] if profile.usual_ip else [],
        "total_logins":  None,
        "failed_logins": None,
        "avg_hour":      profile.typical_login_start_hour,
        "last_seen":     profile.last_updated.isoformat() if profile.last_updated else None,
    }


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        session_id = request.session_id or str(uuid.uuid4())
        query = request.query.strip()
        context = request.context

        # Step 1: No context yet -> show menu
        if not context and not query:
            return ChatResponse(
                answer="Hey! I'm your ThreatLens security assistant. What would you like to know?",
                options=MENU_OPTIONS,
                session_id=session_id,
            )

        context_lower = context.lower() if context else ""

        alerts_q = db.query(Alert).order_by(Alert.timestamp.desc())
        profiles = db.query(UserProfile).all()

        if "high-risk" in context_lower:
            high_risk = [p for p in profiles if getattr(p, "behavior_label", "") == "high-risk"]
            auto_query = "Which users are high-risk and why?"
            alerts_data = [_serialize_alert(a) for a in alerts_q.limit(10).all()]
            profile_data = _serialize_profile(high_risk[0]) if high_risk else None

        elif "recent alerts" in context_lower or "summarise" in context_lower:
            auto_query = "Summarise the most recent security alerts."
            alerts_data = [_serialize_alert(a) for a in alerts_q.limit(10).all()]
            profile_data = None

        elif "investigate" in context_lower:
            user_id = _extract_user_id(query) if query else None
            if not user_id or query == context:
                return ChatResponse(
                    answer="Sure! Which user would you like me to investigate? Please type their username.",
                    options=None,
                    session_id=session_id,
                )
            auto_query = f"Why is {user_id} risky? Give a detailed analysis."
            user_alerts = alerts_q.filter(Alert.user_id == user_id).limit(5).all()
            alerts_data = [_serialize_alert(a) for a in (user_alerts or alerts_q.limit(5).all())]
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            profile_data = _serialize_profile(profile) if profile else None

        elif "ip" in context_lower or "port" in context_lower:
            auto_query = "Which IPs and ports are showing risky or suspicious activity?"
            alerts_data = [_serialize_alert(a) for a in alerts_q.limit(10).all()]
            profile_data = None

        else:
            auto_query = query
            user_id = _extract_user_id(query)
            user_alerts = alerts_q.filter(Alert.user_id == user_id).limit(5).all() if user_id else []
            alerts_data = [_serialize_alert(a) for a in (user_alerts or alerts_q.limit(5).all())]
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first() if user_id else None
            profile_data = _serialize_profile(profile) if profile else None

        effective_query = query if (query and query != context) else auto_query
        prompt = build_chat_prompt(effective_query, alerts_data, profile_data)
        answer = call_llm(prompt, fallback="Fallback: alice login failed brute risk port suspicious investigate alert.")

        return ChatResponse(
            answer=answer,
            options=["🔁 Ask another question", "🏠 Back to menu"],
            session_id=session_id,
        )

    except Exception as e:
        logger.error(f"[CHAT] Error: {e}", exc_info=True)
        return ChatResponse(
            answer="Something went wrong on the server. Please try again.",
            options=["🏠 Back to menu"],
            session_id=request.session_id or "",
        )
