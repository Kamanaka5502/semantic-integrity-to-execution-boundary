from datetime import datetime, UTC
import hashlib
import json

def hash_state(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

def semantic_gate(semantic):
    if not semantic["context_complete"]:
        return "REDIRECT", "Context incomplete"
    if not semantic["ambiguity_low"]:
        return "ESCALATE", "Meaning ambiguous"
    if semantic["confidence"] < 0.80:
        return "ESCALATE", "Low semantic confidence"
    return "PASS", "Semantic gate passed"

def execution_gate(action, state, authority):
    if not authority["valid"]:
        return "REFUSE", "Authority invalid"
    if state["risk"] > 7:
        return "ESCALATE", "Execution risk threshold exceeded"
    if not state["ready"]:
        return "REDIRECT", "Target not ready"
    return "EXECUTE", "Execution allowed"

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
    final_decision = semantic_decision
    reason = semantic_reason
    execution_status = "NOT_REACHED"
else:
    execution_decision, execution_reason = execution_gate(action, state, authority)
    final_decision = execution_decision
    reason = execution_reason
    execution_status = execution_decision

receipt = {
    "action": action,
    "semantic_gate": semantic_decision,
    "execution_gate": execution_status,
    "decision": final_decision,
    "reason": reason,
    "state_hash": hash_state(state),
    "timestamp": datetime.now(UTC).isoformat()
}

print(json.dumps(receipt, indent=2))
