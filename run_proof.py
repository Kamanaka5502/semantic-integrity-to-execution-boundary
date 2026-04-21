import json
import hashlib
import time

def hash_obj(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

def evaluate(payload):
    if payload.get("branch") != "main":
        return {
            "allowed": False,
            "outcome": "REFUSE_BLOCK",
            "reason": "INVALID_BRANCH"
        }
    return {
        "allowed": True,
        "outcome": "SAFE_COMMIT",
        "reason": "LAWFUL_COMMIT_AUTHORIZED"
    }

def run():
    payload = {
        "action": "TRANSFER_FUNDS",
        "branch": "main",
        "state": {"balance": 100}
    }

    state_hash = hash_obj(payload["state"])
    decision = evaluate(payload)

    receipt = {
        "timestamp": time.time(),
        "payload": payload,
        "decision": decision,
        "state_hash": state_hash
    }

    replay = evaluate(payload)

    mutated_payload = payload.copy()
    mutated_payload["branch"] = "beta"
    mutated_replay = evaluate(mutated_payload)

    output = {
        "proof": {
            "positive": {
                "allowed": decision["allowed"],
                "outcome": decision["outcome"],
                "replay": {"matches": decision == replay}
            },
            "negative": {
                "replay": {
                    "matches": decision == mutated_replay,
                    "mismatches": ["branch violation"]
                }
            }
        }
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    run()
