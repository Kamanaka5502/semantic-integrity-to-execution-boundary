import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.adapter import from_sdc
from app.admissibility import evaluate_attempt
from app.commit_gate import enforce
from app.receipt import create_proof_receipt
from app.replay import replay


CASE_DIR = Path("cases")


def expected_from_filename(name: str) -> str:
    if "execute" in name:
        return "EXECUTE"
    if "block" in name:
        return "BLOCK"
    if "escalate" in name:
        return "ESCALATE"
    raise ValueError(f"Cannot infer expected decision from filename: {name}")


def main():
    failures = 0
    total = 0

    for case_path in sorted(CASE_DIR.glob("*.json")):
        total += 1
        payload = json.loads(case_path.read_text())
        attempt = from_sdc(payload)

        result = evaluate_attempt(attempt)
        replay_result = replay(attempt)

        proof_receipt_1 = create_proof_receipt(attempt, result)
        proof_receipt_2 = create_proof_receipt(attempt, replay_result)

        expected = expected_from_filename(case_path.name)

        decision_ok = result.decision.value == expected
        replay_ok = replay_result.decision.value == result.decision.value
        proof_ok = proof_receipt_1.receipt_id == proof_receipt_2.receipt_id

        commit_status = enforce(result.decision)

        if decision_ok and replay_ok and proof_ok:
            print(f"[PASS] {case_path.name} -> {result.decision.value} / {commit_status}")
        else:
            failures += 1
            print(f"[FAIL] {case_path.name}")
            print(f"  expected: {expected}")
            print(f"  actual:   {result.decision.value}")
            print(f"  replay:   {replay_result.decision.value}")
            print(f"  proof_eq: {proof_ok}")

    print("-" * 72)
    print(f"Total: {total}  Failures: {failures}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
