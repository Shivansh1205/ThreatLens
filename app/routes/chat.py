import json
import logging
import re

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.alert import Alert
from app.models.user_profile import UserProfile
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_explainer import build_chat_prompt, call_llm

logger = logging.getLogger("sentinelai.routes.chat")
router = APIRouter()

_STOPWORDS = {"why", "is", "the", "a", "an", "what", "how", "who", "risky",
              "user", "alert", "alerts", "about", "tell", "me", "show", "any"}


def _extract_user_id(query: str) -> str | None:
    """Extract a user_id token from the query, ignoring common stopwords."""
    for token in re.findall(r"[a-zA-Z0-9_\-]+", query):
        if token.lower() not in _STOPWORDS:
            return token
    return None


def _serialize_alert(alert: Alert) -> dict:
    try:
        reasons = json.loads(alert.reasons or "[]")
    except (json.JSONDecodeError, TypeError):
        reasons = [alert.reasons]
    return {
        "user_id":    alert.user_id,
        "ip":         alert.ip,
        "risk_score": alert.risk_score,
        "reasons":    reasons,
        "timestamp":  alert.timestamp.isoformat() if alert.timestamp else None,
    }


def _serialize_profile(profile: UserProfile) -> dict:
    try:
        usual_ips = json.loads(profile.usual_ips or "[]")
    except (json.JSONDecodeError, TypeError):
        usual_ips = []
    return {
        "user_id":       profile.user_id,
        "usual_ips":     usual_ips,
        "total_logins":  profile.total_logins,
        "failed_logins": profile.failed_logins,
        "avg_hour":      round(profile.avg_hour, 2) if profile.avg_hour >= 0 else None,
        "last_seen":     profile.last_seen.isoformat() if profile.last_seen else None,
    }


@router.post("/chat", response_model=ChatResponse, summary="RAG-style threat chat", tags=["Chat"])
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Answer a natural-language question about recent alerts and user behaviour.

    Context injected into the prompt:
    - Last 10 alerts (filtered by user_id if mentioned in query, else global)
    - Behaviour profile of the mentioned user (if found)

    Example queries:
    - "Why is alice risky?"
    - "What happened with IP 10.99.0.1?"
    - "Summarise the latest threats"
    """
    query = request.query
    logger.info(f"[CHAT] Query: {query!r}")

    # ── Context retrieval ────────────────────────────────────────────────────
    user_id = _extract_user_id(query)
    alerts_q = db.query(Alert).order_by(Alert.timestamp.desc())

    if user_id:
        user_alerts = alerts_q.filter(Alert.user_id == user_id).limit(10).all()
        recent_alerts = user_alerts if user_alerts else alerts_q.limit(10).all()
    else:
        recent_alerts = alerts_q.limit(10).all()

    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if user_id else None
    )

    alerts_data  = [_serialize_alert(a) for a in recent_alerts]
    profile_data = _serialize_profile(profile) if profile else None

    logger.info(
        f"[CHAT] Context — alerts={len(alerts_data)}  "
        f"user_id={user_id!r}  profile_found={profile_data is not None}"
    )

    # ── Build prompt + call LLM ──────────────────────────────────────────────
    prompt = build_chat_prompt(query, alerts_data, profile_data)
    answer = call_llm(
        prompt,
        fallback="Based on recent alerts, suspicious activity was detected. "
                 "Please review the /alerts endpoint for details."
    )

    return ChatResponse(answer=answer)
