from typing import Dict
from app.models import Attempt


BASELINE_MIN_AUTHORITY: Dict[str, int] = {
    "healthcare": 6,
    "registry": 5,
    "maritime": 6,
    "education": 4,
}


def validate_authority(attempt: Attempt) -> bool:
    required = BASELINE_MIN_AUTHORITY.get(attempt.corridor, 99)
    return attempt.authority_level >= required
