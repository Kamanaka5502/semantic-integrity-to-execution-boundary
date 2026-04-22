from typing import Dict, Tuple
from app.models import Decision, Attempt

ALLOWED_ACTIONS = {
    "SUBMIT_INTAKE",
    "REVIEW_CASE",
    "APPROVE_PATIENT",
    "COMMIT_CARE_PLAN",
}

VALID_STATE_TRANSITIONS = {
    ("INTAKE", "SUBMIT_INTAKE"): "UNDER_REVIEW",
    ("UNDER_REVIEW", "REVIEW_CASE"): "PENDING_APPROVAL",
    ("PENDING_APPROVAL", "APPROVE_PATIENT"): "APPROVED",
    ("APPROVED", "COMMIT_CARE_PLAN"): "COMMITTED",
}


def evaluate(attempt: Attempt) -> Tuple[Decision, str, Dict[str, bool]]:
    checks = {
        "action_allowed": attempt.action in ALLOWED_ACTIONS,
        "patient_id_present": bool(attempt.payload.get("patient_id")),
        "clinical_context_present": bool(attempt.payload.get("clinical_context")),
        "state_transition_valid": (attempt.prior_state, attempt.action) in VALID_STATE_TRANSITIONS,
    }

    if not checks["action_allowed"]:
        return Decision.BLOCK, "Healthcare action not allowed", checks

    if not checks["patient_id_present"]:
        return Decision.BLOCK, "Missing patient_id", checks

    if not checks["state_transition_valid"]:
        return Decision.BLOCK, "Invalid healthcare state transition", checks

    if attempt.action == "REVIEW_CASE" and not checks["clinical_context_present"]:
        return Decision.ESCALATE, "Clinical context required for review", checks

    return Decision.EXECUTE, "Healthcare action admissible", checks
