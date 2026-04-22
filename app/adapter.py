from typing import Dict, Any
from app.models import Attempt


def from_sdc(payload: Dict[str, Any]) -> Attempt:
    return Attempt(
        corridor=payload.get("corridor", "").strip().lower(),
        action=payload.get("action", "").strip().upper(),
        user=payload.get("user", "unknown"),
        authority_level=int(payload.get("authority", 0)),
        payload=payload.get("payload", {}),
        prior_state=payload.get("prior_state", "UNKNOWN"),
    )
