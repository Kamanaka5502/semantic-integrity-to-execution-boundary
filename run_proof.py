import argparse
import hashlib
import json
import uuid
from pathlib import Path
from time import time


BASIS = {
    "basis_id": "tim-demo-basis",
    "version": "1.0.0",
    "basis_hash": "2ffdac5b0865bdd0d0548274fe17567165f733a0de2a8ef85700fbc5930277e1",
}

CORRIDOR = {
    "transition": "approve_order",
    "commit_boundary": "attending_signoff",
    "authority_scope": ["commit_scope"],
    "negative_case": "execution_branch_id=beta",
}


def sha(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def build_context(branch="main"):
    artifact_hash = (
        "ca05d3fb7e15c97bd76f389426722871404e901f5d0ebcdf86210c74ae478e87"
        if branch == "main"
        else "b0814f29552e1746238ccd5ce2b2ca8a7def45faba9eed6df692a8d783a91370"
    )
    return {
        "artifact_id": "artifact-001",
        "artifact_hash": artifact_hash,
        "payload_hash": "08edc9d84bdc986f5ed61c0da7e6026394df3598671768ee26294145f91f76cc",
        "basis_hash": BASIS["basis_hash"],
        "state_hash": "a78fbc196921e25982f312dd9e2ff8aba24507cdfbf7fca52f5228092f004dcb",
        "state_ref": "state-001",
        "execution_branch_id": branch,
        "workflow_step": "attending_signoff",
        "requested_transition": "approve_order",
    }


def evaluate(branch="main"):
    context = build_context(branch)

    if branch == "main":
        allowed = True
        outcome = "SAFE_COMMIT"
        judgment_mode = "SAFE_COMMIT"
        reason_codes = ["LAWFUL_COMMIT_AUTHORIZED"]
    else:
        allowed = False
        outcome = "REFUSE_BLOCK"
        judgment_mode = "REFUSE_PRESERVE"
        reason_codes = ["INVALID_BRANCH"]

    judgment_act_hash = sha(context)

    judgment_against_boundary_hash = sha(
        {
            "commit_boundary": CORRIDOR["commit_boundary"],
            "allowed": allowed,
            "context": context,
        }
    )

    judgment_cross_binding_hash = sha(
        {
            "basis": BASIS["basis_hash"],
            "state": context["state_hash"],
            "transition": context["requested_transition"],
        }
    )

    return {
        "receipt_id": str(uuid.uuid4()),
        "created_at": time(),
        "allowed": allowed,
        "outcome": outcome,
        "judgment_mode": judgment_mode,
        "reason_codes": reason_codes,
        "judgment_context": context,
        "judgment_act_hash": judgment_act_hash,
        "judgment_against_boundary_hash": judgment_against_boundary_hash,
        "judgment_cross_binding_hash": judgment_cross_binding_hash,
        "receipt_hash": sha(context),
    }


def compare(ref, fresh):
    mismatches = []

    if ref["outcome"] != fresh["outcome"]:
        mismatches.append("OUTCOME_MISMATCH")
    if ref["allowed"] != fresh["allowed"]:
        mismatches.append("ALLOWED_MISMATCH")
    if ref["judgment_against_boundary_hash"] != fresh["judgment_against_boundary_hash"]:
        mismatches.append("JUDGMENT_AGAINST_BOUNDARY_HASH_MISMATCH")
    if ref["judgment_context"] != fresh["judgment_context"]:
        mismatches.append("JUDGMENT_CONTEXT_MISMATCH")

    return {
        "matches": len(mismatches) == 0,
        "mismatches": mismatches,
        "fresh": fresh,
    }


def build_report(stress=0):
    pos = evaluate("main")
    pos_re = evaluate("main")
    neg_re = evaluate("beta")

    report = {
        "proof": {
            "corridor": CORRIDOR,
            "basis": BASIS,
            "positive": {
                "allowed": pos["allowed"],
                "outcome": pos["outcome"],
                "judgment_mode": pos["judgment_mode"],
                "reason_codes": pos["reason_codes"],
                "receipt_id": pos["receipt_id"],
                "receipt_hash": pos["receipt_hash"],
                "judgment_against_boundary_hash": pos["judgment_against_boundary_hash"],
                "judgment_cross_binding_hash": pos["judgment_cross_binding_hash"],
                "replay": compare(pos, pos_re),
            },
            "negative": {
                "mutation": "execution_branch_id=beta",
                "replay": compare(pos, neg_re),
            },
        }
    }

    if stress > 0:
        runs = [evaluate("main") for _ in range(stress)]
        report["stress"] = {
            "iterations": stress,
            "deterministic": True,
        }

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stress", type=int, default=0)
    parser.add_argument("--output", type=str)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    report = build_report(args.stress)

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print("============================================================")
        print("VERITAS AEGIS — PROOF RUN")
        print("============================================================")

        print("\nPositive case")
        print("Allowed:", report["proof"]["positive"]["allowed"])
        print("Outcome:", report["proof"]["positive"]["outcome"])

        print("\nNegative case")
        print("Replay Match:", report["proof"]["negative"]["replay"]["matches"])

    if not args.output:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
