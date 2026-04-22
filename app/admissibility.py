from typing import Callable, Dict, Tuple
from app.authority import validate_authority
from app.models import Attempt, EvaluationResult, Decision

from app.corridors import healthcare, registry, maritime, education


CORRIDOR_EVALUATORS: Dict[str, Callable[[Attempt], Tuple[Decision, str, dict]]] = {
    "healthcare": healthcare.evaluate,
    "registry": registry.evaluate,
    "maritime": maritime.evaluate,
    "education": education.evaluate,
}


def evaluate_attempt(attempt: Attempt) -> EvaluationResult:
    if attempt.corridor not in CORRIDOR_EVALUATORS:
        return EvaluationResult(
            decision=Decision.BLOCK,
            reason=f"Unknown corridor: {attempt.corridor}",
            checks={"corridor_known": False},
            corridor=attempt.corridor,
            action=attempt.action,
        )

    authority_ok = validate_authority(attempt)
    if not authority_ok:
        return EvaluationResult(
            decision=Decision.BLOCK,
            reason="Insufficient authority",
            checks={"authority_valid": False},
            corridor=attempt.corridor,
            action=attempt.action,
        )

    decision, reason, checks = CORRIDOR_EVALUATORS[attempt.corridor](attempt)
    checks["authority_valid"] = True

    return EvaluationResult(
        decision=decision,
        reason=reason,
        checks=checks,
        corridor=attempt.corridor,
        action=attempt.action,
    )
