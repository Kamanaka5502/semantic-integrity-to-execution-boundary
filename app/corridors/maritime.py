from typing import Dict, Tuple
from app.models import Decision, Attempt

ALLOWED_ACTIONS = {
    "SUBMIT_MANIFEST",
    "REVIEW_COMPLIANCE",
    "AUTHORIZE_DEPARTURE",
    "COMMIT_VOYAGE",
}

VALID_STATE_TRANSITIONS = {
    ("DRAFT", "SUBMIT_MANIFEST"): "SUBMITTED",
    ("SUBMITTED", "REVIEW_COMPLIANCE"): "REVIEWED",
    ("REVIEWED", "AUTHORIZE_DEPARTURE"): "AUTHORIZED",
    ("AUTHORIZED", "COMMIT_VOYAGE"): "COMMITTED",
}


def evaluate(attempt: Attempt) -> Tuple[Decision, str, Dict[str, bool]]:
    checks = {
        "action_allowed": attempt.action in ALLOWED_ACTIONS,
        "vessel_id_present": bool(attempt.payload.get("vessel_id")),
        "manifest_complete": bool(attempt.payload.get("manifest_complete")),
        "compliance_clear": bool(attempt.payload.get("compliance_clear")),
        "state_transition_valid": (attempt.prior_state, attempt.action) in VALID_STATE_TRANSITIONS,
    }

    if not checks["action_allowed"]:
        return Decision.BLOCK, "Maritime action not allowed", checks

    if not checks["vessel_id_present"]:
        return Decision.BLOCK, "Missing vessel_id", checks

    if not checks["state_transition_valid"]:
        return Decision.BLOCK, "Invalid maritime state transition", checks

    if attempt.action == "SUBMIT_MANIFEST" and not checks["manifest_complete"]:
        return Decision.BLOCK, "Manifest incomplete", checks

    if attempt.action in {"AUTHORIZE_DEPARTURE", "COMMIT_VOYAGE"} and not checks["compliance_clear"]:
        return Decision.ESCALATE, "Compliance review required before departure", checks

    return Decision.EXECUTE, "Maritime action admissible", checks
