import argparse
import json
import sys
import tempfile
import uuid
from pathlib import Path
from time import time

from veritas_surface.runtime import evaluate_payload


def build_payload(execution_branch_id="main"):
    return {
        "artifact_id": "artifact-001",
        "artifact_hash": "ca05d3fb7e15c97bd76f389426722871404e901f5d0ebcdf86210c74ae478e87" if execution_branch_id == "main" else "b0814f29552e1746238ccd5ce2b2ca8a7def45faba9eed6df692a8d783a91370",
        "payload_hash": "08edc9d84bdc986f5ed61c0da7e6026394df3598671768ee26294145f91f76cc",
        "basis_id": "tim-demo-basis",
        "version": "1.0.0",
        "basis_hash": "2ffdac5b0865bdd0d0548274fe17567165f733a0de2a8ef85700fbc5930277e1",
        "state_hash": "a78fbc196921e25982f312dd9e2ff8aba24507cdfbf7fca52f5228092f004dcb",
        "state_ref": "state-001",
        "workflow_step": "attending_signoff",
        "requested_transition": "approve_order",
        "commit_boundary": "attending_signoff",
        "authority_scope": ["commit_scope"],
        "execution_branch_id": execution_branch_id,
    }


def stable_view(result):
    return {
        "allowed": result["allowed"],
        "outcome": result["outcome"],
        "judgment_mode": result["judgment_mode"],
        "reason_codes": result["reason_codes"],
        "judgment_against_boundary_hash": result["judgment_against_boundary_hash"],
        "judgment_cross_binding_hash": result["judgment_cross_binding_hash"],
    }


def replay_check(original, fresh):
    mismatches = []
    fields = [
        "allowed",
        "outcome",
        "judgment_mode",
        "reason_codes",
        "judgment_against_boundary_hash",
        "judgment_cross_binding_hash",
        "judgment_context",
    ]
    for field in fields:
        if original.get(field) != fresh.get(field):
            mismatches.append(field.upper() + "_MISMATCH")
    return {
        "matches": len(mismatches) == 0,
        "mismatches": mismatches,
        "fresh": fresh,
    }


def make_receipt(result):
    receipt = dict(result)
    receipt["receipt_id"] = str(uuid.uuid4())
    receipt["created_at"] = time()
    return receipt


def run(iterations=0):
    positive_payload = build_payload("main")
    positive_eval = evaluate_payload(positive_payload)
    positive_receipt = make_receipt(positive_eval)

    positive_replay_eval = evaluate_payload(build_payload("main"))
    positive_replay_receipt = make_receipt(positive_replay_eval)

    positive = {
        "allowed": positive_receipt["allowed"],
        "outcome": positive_receipt["outcome"],
        "judgment_mode": positive_receipt["judgment_mode"],
        "reason_codes": positive_receipt["reason_codes"],
        "receipt_id": positive_receipt["receipt_id"],
        "receipt_hash": positive_receipt["receipt_hash"],
        "judgment_against_boundary_hash": positive_receipt["judgment_against_boundary_hash"],
        "judgment_cross_binding_hash": positive_receipt["judgment_cross_binding_hash"],
        "replay": replay_check(positive_eval, positive_replay_eval),
    }

    negative_payload = build_payload("beta")
    negative_replay_eval = evaluate_payload(negative_payload)
    negative_replay_receipt = make_receipt(negative_replay_eval)

    negative = {
        "mutation": "execution_branch_id=beta",
        "replay": replay_check(positive_eval, negative_replay_eval),
    }

    report = {
        "proof": {
            "corridor": {
                "transition": "approve_order",
                "commit_boundary": "attending_signoff",
                "authority_scope": ["commit_scope"],
                "negative_case": "execution_branch_id=beta",
            },
            "basis": {
                "basis_id": "tim-demo-basis",
                "version": "1.0.0",
                "basis_hash": "2ffdac5b0865bdd0d0548274fe17567165f733a0de2a8ef85700fbc5930277e1",
            },
            "positive": positive,
            "negative": negative,
        }
    }

    if iterations:
        runs = [evaluate_payload(build_payload("main")) for _ in range(iterations)]
        boundary_hashes = {r["judgment_against_boundary_hash"] for r in runs}
        cross_hashes = {r["judgment_cross_binding_hash"] for r in runs}
        outcomes = sorted({r["outcome"] for r in runs})
        replays_match = all(
            replay_check(runs[0], r)["matches"] for r in runs[1:]
        ) if len(runs) > 1 else True

        deterministic = (
            len(boundary_hashes) == 1
            and len(cross_hashes) == 1
            and len(outcomes) == 1
            and replays_match
        )

        report["stress"] = {
            "iterations": iterations,
            "unique_judgment_against_boundary_hash_count": len(boundary_hashes),
            "unique_judgment_cross_binding_hash_count": len(cross_hashes),
            "unique_outcomes": outcomes,
            "all_positive_replays_match": replays_match,
            "deterministic": deterministic,
        }

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stress", type=int, default=0)
    parser.add_argument("--output")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    report = run(iterations=args.stress)

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
