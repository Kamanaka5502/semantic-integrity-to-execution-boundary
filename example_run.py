from datetime import datetime, UTC

def evaluate(action, state, authority):
    if not authority["valid"]:
        return "REFUSE"

    if state["risk"] > 7:
        return "ESCALATE"

    if not state["ready"]:
        return "REDIRECT"

    return "EXECUTE"

action = "DEPLOY_CHANGE"
state = {"risk": 8, "ready": True}
authority = {"valid": True}

decision = evaluate(action, state, authority)

print({
    "decision": decision,
    "timestamp": datetime.now(UTC).isoformat()
})
