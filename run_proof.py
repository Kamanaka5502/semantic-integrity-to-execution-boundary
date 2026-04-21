from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import replace
from pathlib import Path
from typing import Any

from veritas_aegis import CommitRequest, VeritasAegisEngine, build_artifact
from veritas_aegis.util import sha256_obj

DEFAULT_STORE_ROOT = Path("demo_store")
DEFAULT_OUTPUT_PATH = Path("proof_output.json")


def reset_store(store_root: Path) -> None:
    if store_root.exists():
        shutil.rmtree(store_root)


def seed_basis(engine: VeritasAegisEngine):
    rules = {
        "schema": {
            "schema_id": "tmu.transition",
            "schema_version": "1.0",
            "constraint_bundle_hash": "bundle-hash-001",
            "required_payload_fields": ["order_id", "target_state", "risk_level"],
        },
        "actors": {
            "operator_1": ["commit_scope"],
        },
        "transitions": {
            "approve_order": {
                "from": ["PENDING"],
                "to": "APPROVED",
                "required_scope": ["commit_scope"],
                "required_payload_matches": ["target_state"],
                "max_risk": 5,
            }
        },
        "branch_policy": {
            "allowed_branch_id": "branch-alpha",
            "required_derivation": "DERIVATIVE",
            "required_branch_role": "EXECUTION_BOUNDARY_STEWARD",
            "forbid_sovereign_claim": True,
            "required_steward_lane": "visible_operator_lane",
            "required_visible_surface": "operator_surface",
            "allowed_workflows": ["tmu_demo_flow"],
            "require_translation_digest": True,
            "require_source_intent": True,
        },
        "escalation_corridors": {
            "approve_order": "senior_review"
        },
        "require_parent_receipt_for_statuses": [],
    }
    return engine.put_basis({
        "basis_id": "tmu-demo-basis",
        "version": "1.0.0",
        "rules": rules,
    })


def seed_state(engine: VeritasAegisEngine) -> None:
    engine.put_state(
        "state-001",
        {
            "entity_id": "entity-001",
            "current_status": "PENDING",
            "attributes": {"risk_level": 1},
            "open_burdens": [],
            "continuity_chain_head": None,
            "continuity_debt": [],
        },
    )


def build_demo_artifact(engine: VeritasAegisEngine, basis):
    state = engine.resolve_state("state-001")
    artifact = build_artifact(
        artifact_id="artifact-001",
        payload={
            "order_id": "ORD-1001",
            "target_state": "APPROVED",
            "risk_level": 1,
        },
        workflow_id="tmu_demo_flow",
        workflow_step="attending_signoff",
        requested_transition="approve_order",
        actor_id="operator_1",
        authority_scope=["commit_scope"],
        schema_id="tmu.transition",
        schema_version="1.0",
        constraint_bundle_hash="bundle-hash-001",
        governing_basis_id=basis.basis_id,
        governing_basis_version=basis.version,
        governing_basis_hash=basis.basis_hash,
        basis_lineage_hash=basis.lineage_hash,
        basis_signature=basis.signature,
        logic_version="demo.logic.v1",
        source_intent="approve order under TMU boundary demo",
        executable_claim="approve_order",
        translation_constraints=["must_match_basis", "must_match_state"],
        translation_outcome="PRESERVE",
        steward_lane="visible_operator_lane",
        visible_surface="operator_surface",
        translation_digest="digest-001",
        translation_narrowing=[],
        preserved_claims=["approve_order"],
        state_ref="state-001",
        declared_state_hash=state.state_hash,
        declared_entity_id=state.entity_id,
        declared_current_status=state.current_status,
        declared_open_burden_codes=[],
        parent_receipt_id=None,
        parent_receipt_signature=None,
        parent_receipt_witness_hash=None,
        continuity_chain_head=state.continuity_chain_head,
        continuity_mode="self",
        continuation_intent="continue current lawful branch",
        continuation_constraints=["no_open_debt"],
        expected_continuation_result="ALLOW",
        continuity_debt_in=[],
        inherited_burden_codes=[],
        execution_branch_id="branch-alpha",
        branch_derivation="DERIVATIVE",
        branch_role="EXECUTION_BOUNDARY_STEWARD",
        claims_sovereign_authority=False,
        declared_escalation_target=None,
        surface_steward="Samantha/Terry",
    )
    return engine.sign_artifact(artifact)


def make_wrong_branch_variant(engine: VeritasAegisEngine, artifact):
    tampered_artifact = replace(
        artifact,
        branch_posture=replace(artifact.branch_posture, execution_branch_id="branch-beta"),
    )
    return engine.sign_artifact(tampered_artifact)


def summarize_result(result, replay: dict[str, Any]) -> dict[str, Any]:
    receipt = result.receipt
    return {
        "allowed": result.allowed,
        "outcome": receipt.outcome,
        "judgment_mode": receipt.outcome_judgment.judgment_mode,
        "reason_codes": receipt.reason_codes,
        "receipt_id": receipt.receipt_id,
        "receipt_hash": receipt.integrity.receipt_hash,
        "judgment_against_boundary_hash": receipt.integrity.judgment_against_boundary_hash,
        "judgment_cross_binding_hash": receipt.integrity.judgment_cross_binding_hash,
        "replay": replay,
    }


def build_proof_report(store_root: Path) -> dict[str, Any]:
    reset_store(store_root)
    engine = VeritasAegisEngine(store_root=str(store_root))
    basis = seed_basis(engine)
    seed_state(engine)
    artifact = build_demo_artifact(engine, basis)

    result = engine.commit(CommitRequest(artifact=artifact))
    replay = engine.replay(result.receipt.receipt_id, artifact)

    tampered_artifact = make_wrong_branch_variant(engine, artifact)
    tampered_replay = engine.replay(result.receipt.receipt_id, tampered_artifact)

    return {
        "proof": {
            "corridor": {
                "transition": "approve_order",
                "commit_boundary": "attending_signoff",
                "authority_scope": ["commit_scope"],
                "negative_case": "execution_branch_id=branch-beta",
            },
            "basis": {
                "basis_id": basis.basis_id,
                "version": basis.version,
                "basis_hash": basis.basis_hash,
                "lineage_hash": basis.lineage_hash,
            },
            "positive": summarize_result(result, replay),
            "negative": {
                "mutation": "execution_branch_id=branch-beta",
                "tampered_artifact_hash": sha256_obj(tampered_artifact.to_dict()),
                "replay": tampered_replay,
            },
        }
    }


def run_stress(iterations: int) -> dict[str, Any]:
    receipt_hashes: list[str] = []
    boundary_hashes: list[str] = []
    binding_hashes: list[str] = []
    outcomes: list[str] = []
    replay_matches: list[bool] = []

    for idx in range(iterations):
        report = build_proof_report(Path(f"demo_store_stress_{idx}"))
        positive = report["proof"]["positive"]
        receipt_hashes.append(positive["receipt_hash"])
        boundary_hashes.append(positive["judgment_against_boundary_hash"])
        binding_hashes.append(positive["judgment_cross_binding_hash"])
        outcomes.append(positive["outcome"])
        replay_matches.append(bool(positive["replay"]["matches"]))

    unique_receipt_hashes = sorted(set(receipt_hashes))
    unique_boundary_hashes = sorted(set(boundary_hashes))
    unique_binding_hashes = sorted(set(binding_hashes))
    unique_outcomes = sorted(set(outcomes))
    all_replays_match = all(replay_matches)
    return {
        "iterations": iterations,
        "unique_receipt_hash_count": len(unique_receipt_hashes),
        "unique_receipt_hashes": unique_receipt_hashes,
        "unique_judgment_against_boundary_hash_count": len(unique_boundary_hashes),
        "unique_judgment_against_boundary_hashes": unique_boundary_hashes,
        "unique_judgment_cross_binding_hash_count": len(unique_binding_hashes),
        "unique_judgment_cross_binding_hashes": unique_binding_hashes,
        "unique_outcomes": unique_outcomes,
        "all_positive_replays_match": all_replays_match,
        "receipt_identity_varies_per_run": len(unique_receipt_hashes) > 1,
        "deterministic": len(unique_boundary_hashes) == 1 and len(unique_binding_hashes) == 1 and unique_outcomes == ["SAFE_COMMIT"] and all_replays_match,
    }


def print_header(title: str) -> None:
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_positive(report: dict[str, Any]) -> None:
    positive = report["proof"]["positive"]
    print("Positive case")
    print("Allowed:", positive["allowed"])
    print("Outcome:", positive["outcome"])
    print("Judgment mode:", positive["judgment_mode"])
    print("Reason codes:", ", ".join(positive["reason_codes"]) or "(none)")
    print("Receipt ID:", positive["receipt_id"])
    print("Receipt Hash:", positive["receipt_hash"])
    print("Replay Match:", positive["replay"]["matches"])
    print("Replay Mismatches:", positive["replay"]["mismatches"])
    print()


def print_negative(report: dict[str, Any]) -> None:
    negative = report["proof"]["negative"]
    print("Negative case (wrong branch id)")
    print("Mutation:", negative["mutation"])
    print("Replay Match:", negative["replay"]["matches"])
    print("Replay Mismatches:", negative["replay"]["mismatches"])
    print()


def print_stress(stress: dict[str, Any]) -> None:
    print("Determinism stress")
    print("Iterations:", stress["iterations"])
    print("Unique receipt hashes:", stress["unique_receipt_hash_count"])
    print("Unique boundary hashes:", stress["unique_judgment_against_boundary_hash_count"])
    print("Unique cross-binding hashes:", stress["unique_judgment_cross_binding_hash_count"])
    print("Unique outcomes:", ", ".join(stress["unique_outcomes"]))
    print("All positive replays match:", stress["all_positive_replays_match"])
    print("Receipt identity varies per run:", stress["receipt_identity_varies_per_run"])
    print("Deterministic:", stress["deterministic"])
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Veritas Aegis deterministic proof corridor.")
    parser.add_argument("--store-root", type=Path, default=DEFAULT_STORE_ROOT, help="Store root used for the main proof run.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Path to write the proof report JSON.")
    parser.add_argument("--stress", type=int, default=0, help="Run deterministic proof this many extra times and verify stable receipt hashes.")
    parser.add_argument("--quiet", action="store_true", help="Suppress terminal output and only write JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_proof_report(args.store_root)
    if args.stress:
        report["stress"] = run_stress(args.stress)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True))

    if not args.quiet:
        print_header("VERITAS AEGIS — PROOF RUN")
        print_positive(report)
        print_negative(report)
        if "stress" in report:
            print_stress(report["stress"])


if __name__ == "__main__":
    main()
