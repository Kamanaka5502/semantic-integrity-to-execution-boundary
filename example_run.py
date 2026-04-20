from datetime import datetime, UTC

def semantic_gate(semantic):
    if not semantic["context_complete"]:
        return "REDIRECT", "Context incomplete"

    if not semantic["ambiguity_low"]:
        return "ESCALATE", "Meaning remains ambiguous"

    if semantic["confidence"] < 0.80:
        return "ESCALATE", "Semantic confidence below threshold"

    return "PASS", "Semantic gate passed"


def execution_gate(action, state, authority):
    if not authority["valid"]:
        return "REFUSE", "Authority invalid"

    if state["risk"] > 7:
        return "ESCALATE", "Execution risk threshold exceeded"

    if not state["ready"]:
        return "REDIRECT", "Target state not ready"

    return "EXECUTE", "Execution gate passed"


action = "APPROVE_PRODUCTION_DEPLOYMENT"

semantic = {
    "context_complete": True,
    "ambiguity_low": True,
    "confidence": 0.91
}

state = {
    "risk": 8,
    "ready": True
}

authority = {
    "valid": True
}

semantic_decision, semantic_reason = semantic_gate(semantic)

if semantic_decision != "PASS":
    result = {
        "semantic_gate": semantic_decision,
        "semantic_reason": semantic_reason,
        "execution_gate": "NOT_REACHED",
        "decision": semantic_decision,
        "timestamp": datetime.now(UTC).isoformat()
    }
else:
    execution_decision, execution_reason = execution_gate(action, state, authority)
    result = {
        "semantic_gate": "PASS",
        "semantic_reason": semantic_reason,
        "execution_gate": execution_decision,
        "decision": execution_decision,
        "reason": execution_reason,
        "timestamp": datetime.now(UTC).isoformat()
    }

print(result)
