from app.models import Decision


def enforce(decision: Decision) -> str:
    if decision == Decision.EXECUTE:
        return "COMMITTED"
    if decision == Decision.BLOCK:
        return "BLOCKED"
    if decision == Decision.ESCALATE:
        return "ESCALATED"
    if decision == Decision.REVERT:
        return "REVERTED"
    return "UNKNOWN"
