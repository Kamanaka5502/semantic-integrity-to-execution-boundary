import json
from app.adapter import from_sdc
from app.admissibility import evaluate_attempt
from app.commit_gate import enforce
from app.receipt import create_receipt, create_proof_receipt
from app.replay import replay


SAMPLE_PAYLOADS = [
    {
        "corridor": "healthcare",
        "action": "APPROVE_PATIENT",
        "user": "doctor_1",
        "authority": 7,
        "prior_state": "PENDING_APPROVAL",
        "payload": {
            "patient_id": "P-1001",
            "clinical_context": "stable",
        },
    },
    {
        "corridor": "registry",
        "action": "APPROVE_RECORD_CHANGE",
        "user": "clerk_1",
        "authority": 5,
        "prior_state": "IDENTITY_VALIDATED",
        "payload": {
            "record_id": "R-221",
            "identity_match": True,
            "change_summary": "address update",
        },
    },
    {
        "corridor": "maritime",
        "action": "AUTHORIZE_DEPARTURE",
        "user": "harbor_master",
        "authority": 7,
        "prior_state": "REVIEWED",
        "payload": {
            "vessel_id": "V-900",
            "manifest_complete": True,
            "compliance_clear": False,
        },
    },
    {
        "corridor": "education",
        "action": "AUTHORIZE_ENROLLMENT",
        "user": "registrar_1",
        "authority": 4,
        "prior_state": "REVIEWED",
        "payload": {
            "student_id": "S-777",
            "eligibility_confirmed": True,
            "program_code": "ENG101",
        },
    },
]


def run_payload(payload):
    attempt = from_sdc(payload)
    result = evaluate_attempt(attempt)
    commit_result = enforce(result.decision)
    runtime_receipt = create_receipt(attempt, result)
    proof_receipt = create_proof_receipt(attempt, result)
    replay_result = replay(attempt)
    replay_proof_receipt = create_proof_receipt(attempt, replay_result)

    output = {
        "attempt": {
            "corridor": attempt.corridor,
            "action": attempt.action,
            "user": attempt.user,
            "authority_level": attempt.authority_level,
            "prior_state": attempt.prior_state,
            "payload": attempt.payload,
        },
        "evaluation": {
            "decision": result.decision.value,
            "reason": result.reason,
            "checks": result.checks,
        },
        "commit_result": commit_result,
        "runtime_receipt": runtime_receipt.to_dict(),
        "proof_receipt": proof_receipt.to_dict(),
        "replay": {
            "decision": replay_result.decision.value,
            "reason": replay_result.reason,
            "checks": replay_result.checks,
        },
        "proof_replay_equivalent": (
            proof_receipt.receipt_id == replay_proof_receipt.receipt_id
        ),
    }

    print("=" * 80)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    for payload in SAMPLE_PAYLOADS:
        run_payload(payload)
