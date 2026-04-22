print("SDC → Veritas handoff demo running")

data = {
    "action": "APPROVE_PRODUCTION_DEPLOYMENT",
    "semantic_gate": "PASS",
    "execution_gate": "ESCALATE",
    "decision": "ESCALATE",
    "reason": "Execution risk threshold exceeded"
}

import json
print(json.dumps(data, indent=2))
