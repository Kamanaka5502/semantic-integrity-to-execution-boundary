from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
import time
import hashlib
import json


class Decision(str, Enum):
    EXECUTE = "EXECUTE"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"
    REVERT = "REVERT"


@dataclass
class Attempt:
    corridor: str
    action: str
    user: str
    authority_level: int
    payload: Dict[str, Any]
    prior_state: str = "UNKNOWN"
    timestamp: float = field(default_factory=time.time)


@dataclass
class EvaluationResult:
    decision: Decision
    reason: str
    checks: Dict[str, bool]
    corridor: str
    action: str


@dataclass
class Receipt:
    receipt_id: str
    corridor: str
    action: str
    user: str
    decision: str
    reason: str
    checks: Dict[str, bool]
    state_hash: str
    transition_hash: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "corridor": self.corridor,
            "action": self.action,
            "user": self.user,
            "decision": self.decision,
            "reason": self.reason,
            "checks": self.checks,
            "state_hash": self.state_hash,
            "transition_hash": self.transition_hash,
            "timestamp": self.timestamp,
        }


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
