import time
from app.models import Attempt, EvaluationResult, Receipt, stable_hash


def _state_hash(attempt: Attempt) -> str:
    return stable_hash(
        {
            "corridor": attempt.corridor,
            "action": attempt.action,
            "payload": attempt.payload,
            "prior_state": attempt.prior_state,
        }
    )


def _transition_hash(attempt: Attempt, result: EvaluationResult) -> str:
    return stable_hash(
        {
            "user": attempt.user,
            "authority_level": attempt.authority_level,
            "decision": result.decision.value,
            "reason": result.reason,
            "checks": result.checks,
        }
    )


def create_receipt(attempt: Attempt, result: EvaluationResult) -> Receipt:
    """
    Live runtime receipt:
    - includes wall-clock time
    - useful for real execution logs
    """
    state_hash = _state_hash(attempt)
    transition_hash = _transition_hash(attempt, result)

    now = time.time()
    receipt_id = stable_hash(
        {
            "mode": "runtime",
            "state_hash": state_hash,
            "transition_hash": transition_hash,
            "timestamp_seed": round(now, 6),
        }
    )

    return Receipt(
        receipt_id=receipt_id,
        corridor=attempt.corridor,
        action=attempt.action,
        user=attempt.user,
        decision=result.decision.value,
        reason=result.reason,
        checks=result.checks,
        state_hash=state_hash,
        transition_hash=transition_hash,
        timestamp=now,
    )


def create_proof_receipt(attempt: Attempt, result: EvaluationResult) -> Receipt:
    """
    Deterministic proof receipt:
    - stable across identical inputs and outcomes
    - useful for replay equivalence proofs
    """
    state_hash = _state_hash(attempt)
    transition_hash = _transition_hash(attempt, result)

    receipt_id = stable_hash(
        {
            "mode": "proof",
            "corridor": attempt.corridor,
            "action": attempt.action,
            "user": attempt.user,
            "authority_level": attempt.authority_level,
            "prior_state": attempt.prior_state,
            "payload": attempt.payload,
            "decision": result.decision.value,
            "reason": result.reason,
            "checks": result.checks,
            "state_hash": state_hash,
            "transition_hash": transition_hash,
        }
    )

    proof_timestamp = 0.0

    return Receipt(
        receipt_id=receipt_id,
        corridor=attempt.corridor,
        action=attempt.action,
        user=attempt.user,
        decision=result.decision.value,
        reason=result.reason,
        checks=result.checks,
        state_hash=state_hash,
        transition_hash=transition_hash,
        timestamp=proof_timestamp,
    )
