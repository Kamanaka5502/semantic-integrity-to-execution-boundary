from typing import Dict, Tuple
from app.models import Decision, Attempt

ALLOWED_ACTIONS = {
    "SUBMIT_ENROLLMENT",
    "REVIEW_ELIGIBILITY",
    "AUTHORIZE_ENROLLMENT",
    "COMMIT_ENROLLMENT",
}

VALID_STATE_TRANSITIONS = {
    ("DRAFT", "SUBMIT_ENROLLMENT"): "SUBMITTED",
    ("SUBMITTED", "REVIEW_ELIGIBILITY"): "REVIEWED",
    ("REVIEWED", "AUTHORIZE_ENROLLMENT"): "AUTHORIZED",
    ("AUTHORIZED", "COMMIT_ENROLLMENT"): "COMMITTED",
}


def evaluate(attempt: Attempt) -> Tuple[Decision, str, Dict[str, bool]]:
    checks = {
        "action_allowed": attempt.action in ALLOWED_ACTIONS,
        "student_id_present": bool(attempt.payload.get("student_id")),
        "eligibility_confirmed": bool(attempt.payload.get("eligibility_confirmed")),
        "state_transition_valid": (attempt.prior_state, attempt.action) in VALID_STATE_TRANSITIONS,
    }

    if not checks["action_allowed"]:
        return Decision.BLOCK, "Education action not allowed", checks

    if not checks["student_id_present"]:
        return Decision.BLOCK, "Missing student_id", checks

    if not checks["state_transition_valid"]:
        return Decision.BLOCK, "Invalid education state transition", checks

    if attempt.action in {"AUTHORIZE_ENROLLMENT", "COMMIT_ENROLLMENT"} and not checks["eligibility_confirmed"]:
        return Decision.BLOCK, "Eligibility not confirmed", checks

    if attempt.action == "REVIEW_ELIGIBILITY" and not attempt.payload.get("program_code"):
        return Decision.ESCALATE, "Program code required for eligibility review", checks

    return Decision.EXECUTE, "Education action admissible", checks
