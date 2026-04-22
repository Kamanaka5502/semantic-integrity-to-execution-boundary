from typing import Dict, Tuple
from app.models import Decision, Attempt

ALLOWED_ACTIONS = {
    "REQUEST_RECORD_UPDATE",
    "VALIDATE_IDENTITY",
    "APPROVE_RECORD_CHANGE",
    "COMMIT_RECORD_UPDATE",
}

VALID_STATE_TRANSITIONS = {
    ("REQUESTED", "VALIDATE_IDENTITY"): "IDENTITY_VALIDATED",
    ("IDENTITY_VALIDATED", "APPROVE_RECORD_CHANGE"): "CHANGE_APPROVED",
    ("CHANGE_APPROVED", "COMMIT_RECORD_UPDATE"): "COMMITTED",
}


def evaluate(attempt: Attempt) -> Tuple[Decision, str, Dict[str, bool]]:
    checks = {
        "action_allowed": attempt.action in ALLOWED_ACTIONS,
        "record_id_present": bool(attempt.payload.get("record_id")),
        "identity_match": bool(attempt.payload.get("identity_match")),
        "state_transition_valid": (attempt.prior_state, attempt.action) in VALID_STATE_TRANSITIONS,
    }

    if not checks["action_allowed"]:
        return Decision.BLOCK, "Registry action not allowed", checks

    if not checks["record_id_present"]:
        return Decision.BLOCK, "Missing record_id", checks

    if attempt.action in {"APPROVE_RECORD_CHANGE", "COMMIT_RECORD_UPDATE"} and not checks["identity_match"]:
        return Decision.BLOCK, "Identity validation failed", checks

    if attempt.action != "REQUEST_RECORD_UPDATE" and not checks["state_transition_valid"]:
        return Decision.BLOCK, "Invalid registry state transition", checks

    if attempt.action == "REQUEST_RECORD_UPDATE" and not attempt.payload.get("change_summary"):
        return Decision.ESCALATE, "Change summary required", checks

    return Decision.EXECUTE, "Registry action admissible", checks
