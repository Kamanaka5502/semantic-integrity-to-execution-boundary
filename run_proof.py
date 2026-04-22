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


def stable_hash(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def make_context(branch="main"):
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
    context = make_context(branch)

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

    judgment_act_hash = stable_hash(
        {
            "requested_transition": context["requested_transition"],
            "workflow_step": context["workflow_step"],
            "execution_branch_id": context["execution_branch_id"],
        }
    )

    judgment_against_boundary_hash = stable_hash(
        {
            "commit_boundary": CORRIDOR["commit_boundary"],
            "allowed": allowed,
            "judgment_mode": judgment_mode,
            "reason_codes": reason_codes,
            "context": context,
        }
    )

    judgment_cross_binding_hash = stable_hash(
        {
            "basis_hash": BASIS["basis_hash"],
            "state_hash": context["state_hash"],
            "transition": context["requested_transition"],
            "workflow_step": context["workflow_step"],
        }
    )

    receipt_core = {
        "allowed": allowed,
        "outcome": outcome,
        "judgment_mode": judgment_mode,
        "reason_codes": reason_codes,
        "judgment_context": context,
        "judgment_act_hash": judgment_act_hash,
        "judgment_against_boundary_hash": judgment_against_boundary_hash,
        "judgment_cross_binding_hash": judgment_cross_binding_hash,
    }

    receipt_hash = stable_hash(
        {
            **receipt_core,
            "receipt_id": str(uuid.uuid4()),
            "created_at": time(),
        }
    )

    return {
        "receipt_id": str(uuid.uuid4()),
        "created_at": time(),
        **receipt_core,
        "receipt_hash": receipt_hash,
    }


def compare(reference, fresh):
    mismatches = []

    if reference["outcome"] != fresh["outcome"]:
        mismatches.append("OUTCOME_MISMATCH")
    if reference["allowed"] != fresh["allowed"]:
        mismatches.append("ALLOWED_MISMATCH")
    if reference["judgment_mode"] != fresh["judgment_mode"]:
        mismatches.append("JUDGMENT_MODE_MISMATCH")
    if reference["reason_codes"] != fresh["reason_codes"]:
        mismatches.append("REASON_CODES_MISMATCH")
    if (
        reference["judgment_against_boundary_hash"]
        != fresh["judgment_against_boundary_hash"]
    ):
        mismatches.append("JUDGMENT_AGAINST_BOUNDARY_HASH_MISMATCH")
    if reference["judgment_cross_binding_hash"] != fresh["judgment_cross_binding_hash"]:
        mismatches.append("CROSS_BINDING_HASH_MISMATCH")
    if reference["judgment_context"] != fresh["judgment_context"]:
        mismatches.append("JUDGMENT_CONTEXT_MISMATCH")

    return {
        "matches": len(mismatches) == 0,
        "mismatches": mismatches,
        "fresh": fresh,
    }


def build_report(stress_iterations=0):
    positive = evaluate("main")
    positive_replay = evaluate("main")
    negative_replay = evaluate("beta")

    report = {
        "proof": {
            "corridor": CORRIDOR,
            "basis": BASIS,
            "positive": {
                "allowed": positive["allowed"],
                "outcome": positive["outcome"],
                "judgment_mode": positive["judgment_mode"],
                "reason_codes": positive["reason_codes"],
                "receipt_id": positive["receipt_id"],
                "receipt_hash": positive["receipt_hash"],
                "judgment_against_boundary_hash": positive["judgment_against_boundary_hash"],
                "judgment_cross_binding_hash": positive["judgment_cross_binding_hash"],
                "replay": compare(positive, positive_replay),
            },
            "negative": {
                "mutation": "execution_branch_id=beta",
                "replay": compare(positive, negative_replay),
            },
        }
    }

    if stress_iterations > 0:
        runs = [evaluate("main") for _ in range(stress_iterations)]
        positive_replays = [compare(positive, evaluate("main")) for _ in range(stress_iterations)]

        report["stress"] = {
            "iterations": stress_iterations,
            "unique_judgment_against_boundary_hash_count": len(
                {r["judgment_against_boundary_hash"] for r in runs}
            ),
            "unique_judgment_cross_binding_hash_count": len(
                {r["judgment_cross_binding_hash"] for r in runs}
            ),
            "unique_outcomes": sorted({r["outcome"] for r in runs}),
            "all_positive_replays_match": all(r["matches"] for r in positive_replays),
            "deterministic": (
                len({r["judgment_against_boundary_hash"] for r in runs}) == 1
                and len({r["judgment_cross_binding_hash"] for r in runs}) == 1
                and all(r["matches"] for r in positive_replays)
            ),
        }

    return report


def print_human_summary(report, stress_iterations):
    print("============================================================")
    print("VERITAS AEGIS — PROOF RUN")
    print("============================================================")

    positive = report["proof"]["positive"]
    negative = report["proof"]["negative"]

    print("\nPositive case")
    print(f"Allowed: {positive['allowed']}")
    print(f"Outcome: {positive['outcome']}")
    print(f"Judgment mode: {positive['judgment_mode']}")
    print(f"Reason codes: {', '.join(positive['reason_codes'])}")
    print(f"Receipt ID: {positive['receipt_id']}")
    print(f"Receipt Hash: {positive['receipt_hash']}")
    print(f"Replay Match: {positive['replay']['matches']}")
    print(f"Replay Mismatches: {positive['replay']['mismatches']}")

    print("\nNegative case (wrong branch id)")
    print(f"Mutation: {negative['mutation']}")
    print(f"Replay Match: {negative['replay']['matches']}")
    print(f"Replay Mismatches: {negative['replay']['mismatches']}")

    if stress_iterations > 0:
        stress = report["stress"]
        print("\nDeterminism stress")
        print(f"Iterations: {stress['iterations']}")
        print(
            "Unique boundary hashes: "
            f"{stress['unique_judgment_against_boundary_hash_count']}"
        )
        print(
            "Unique cross-binding hashes: "
            f"{stress['unique_judgment_cross_binding_hash_count']}"
        )
        print(f"Unique outcomes: {', '.join(stress['unique_outcomes'])}")
        print(f"All positive replays match: {stress['all_positive_replays_match']}")
        print(f"Deterministic: {stress['deterministic']}")


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
        print_human_summary(report, args.stress)
        print()
        print(json.dumps(report, indent=2))
    elif not args.output:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
