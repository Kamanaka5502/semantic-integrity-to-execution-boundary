from app.models import Attempt, EvaluationResult
from app.admissibility import evaluate_attempt


def replay(attempt: Attempt) -> EvaluationResult:
    return evaluate_attempt(attempt)
