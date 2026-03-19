from app.models.alert import Alert


def generate_explanation(alert: Alert) -> str:
    """
    Placeholder for LLM-based explanation of why an alert was raised.
    """
    return (
        f"Alert {alert.id} flagged for user {alert.user_id} "
        f"with risk score {alert.risk_score}."
    )
