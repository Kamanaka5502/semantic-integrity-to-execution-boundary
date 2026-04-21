from __future__ import annotations
import copy
import hashlib
import json
import time
import uuid
from typing import Any, Dict

def _stable(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(_stable(obj)).hexdigest()

def now_ts() -> float:
    return time.time()

def build_governing_basis() -> Dict[str, Any]:
    basis = {
        "basis_id": "tim-demo-basis",
        "version": "1.0.0",
        "rules": {
            "required_authority": ["commit_scope"],
            "required_branch": "main",
            "required_fields": ["order_id", "target_state", "risk_level"],
            "max_risk": 5,
            "allowed_from_status": ["PENDING"],
            "allowed_to_status": ["APPROVED"],
        },
    }
    basis["basis_hash"] = sha256_obj(basis["rules"])
    return basis

def build_state() -> Dict[str, Any]:
    state = {
        "state_ref": "state-001",
        "entity_id": "entity-001",
        "current_status": "PENDING",
        "attributes": {"risk_level": 1},
        "open_burdens": [],
    }
    state["state_hash"] = sha256_obj({
        "entity_id": state["entity_id"],
        "current_status": state["current_status"],
        "attributes": state["attributes"],
        "open_burdens": state["open_burdens"],
    })
    return state

def build_demo_payload() -> Dict[str, Any]:
    return {
        "order_id": "ORD-1001",
        "target_state": "APPROVED",
        "risk_level": 1,
    }

def sign_artifact(payload: Dict[str, Any], state: Dict[str, Any], basis: Dict[str, Any]) -> Dict[str, Any]:
    artifact = {
        "artifact_id": "artifact-001",
        "payload": payload,
        "state_ref": state["state_ref"],
        "declared_state_hash": state["state_hash"],
        "declared_status": state["current_status"],
        "authority_scope": ["commit_scope"],
        "execution_branch_id": "main",
        "source_intent": "approve order under SDC -> Veritas execution boundary",
        "workflow_step": "attending_signoff",
        "requested_transition": "approve_order",
        "basis_id": basis["basis_id"],
        "basis_version": basis["version"],
        "basis_hash": basis["basis_hash"],
    }
    artifact["payload_hash"] = sha256_obj(artifact["payload"])
    artifact["artifact_hash"] = sha256_obj({
        "artifact_id": artifact["artifact_id"],
        "payload_hash": artifact["payload_hash"],
        "state_ref": artifact["state_ref"],
        "declared_state_hash": artifact["declared_state_hash"],
        "declared_status": artifact["declared_status"],
        "authority_scope": artifact["authority_scope"],
        "execution_branch_id": artifact["execution_branch_id"],
        "basis_id": artifact["basis_id"],
        "basis_version": artifact["basis_version"],
        "basis_hash": artifact["basis_hash"],
        "workflow_step": artifact["workflow_step"],
        "requested_transition": artifact["requested_transition"],
    })
    return artifact

def _verify_artifact(artifact: Dict[str, Any], state: Dict[str, Any], basis: Dict[str, Any]) -> list[str]:
    reasons = []
    for field in basis["rules"]["required_fields"]:
        if field not in artifact["payload"]:
            reasons.append(f"MISSING_FIELD:{field}")
    if artifact["declared_state_hash"] != state["state_hash"]:
        reasons.append("DECLARED_STATE_HASH_MISMATCH")
    if artifact["declared_status"] != state["current_status"]:
        reasons.append("DECLARED_STATUS_MISMATCH")
    if artifact["basis_hash"] != basis["basis_hash"]:
        reasons.append("BASIS_HASH_MISMATCH")
    if artifact["execution_branch_id"] != basis["rules"]["required_branch"]:
        reasons.append("INVALID_BRANCH")
    needed = set(basis["rules"]["required_authority"])
    have = set(artifact["authority_scope"])
    if not needed.issubset(have):
        reasons.append("INSUFFICIENT_AUTHORITY")
    if state["current_status"] not in basis["rules"]["allowed_from_status"]:
        reasons.append("STATUS_NOT_ADMISSIBLE")
    if artifact["payload"]["target_state"] not in basis["rules"]["allowed_to_status"]:
        reasons.append("TARGET_NOT_ADMISSIBLE")
    if artifact["payload"]["risk_level"] > basis["rules"]["max_risk"]:
        reasons.append("RISK_ABOVE_THRESHOLD")
    return reasons

def evaluate_commit(artifact: Dict[str, Any], state: Dict[str, Any], basis: Dict[str, Any]) -> Dict[str, Any]:
    reasons = _verify_artifact(artifact, state, basis)

    if "RISK_ABOVE_THRESHOLD" in reasons:
        outcome = "ESCALATE"
        allowed = False
        mode = "ESCALATE"
    elif reasons:
        outcome = "REFUSE_BLOCK"
        allowed = False
        mode = "REFUSE_PRESERVE"
    else:
        outcome = "SAFE_COMMIT"
        allowed = True
        mode = "SAFE_COMMIT"

    judgment_context = {
        "artifact_id": artifact["artifact_id"],
        "artifact_hash": artifact["artifact_hash"],
        "payload_hash": artifact["payload_hash"],
        "basis_hash": basis["basis_hash"],
        "state_hash": state["state_hash"],
        "state_ref": state["state_ref"],
        "execution_branch_id": artifact["execution_branch_id"],
        "workflow_step": artifact["workflow_step"],
        "requested_transition": artifact["requested_transition"],
    }

    receipt = {
        "receipt_id": str(uuid.uuid4()),
        "created_at": now_ts(),
        "allowed": allowed,
        "outcome": outcome,
        "judgment_mode": mode,
        "reason_codes": reasons if reasons else ["LAWFUL_COMMIT_AUTHORIZED"],
        "judgment_context": judgment_context,
    }

    receipt["judgment_act_hash"] = sha256_obj({
        "allowed": receipt["allowed"],
        "outcome": receipt["outcome"],
        "judgment_mode": receipt["judgment_mode"],
        "reason_codes": receipt["reason_codes"],
    })
    receipt["judgment_against_boundary_hash"] = sha256_obj({
        "artifact_hash": artifact["artifact_hash"],
        "state_hash": state["state_hash"],
        "basis_hash": basis["basis_hash"],
        "judgment_act_hash": receipt["judgment_act_hash"],
    })
    receipt["judgment_cross_binding_hash"] = sha256_obj({
        "artifact_hash": artifact["artifact_hash"],
        "payload_hash": artifact["payload_hash"],
        "basis_hash": basis["basis_hash"],
        "state_hash": state["state_hash"],
        "branch": artifact["execution_branch_id"],
        "judgment_against_boundary_hash": receipt["judgment_against_boundary_hash"],
    })
    receipt["receipt_hash"] = sha256_obj({
        "receipt_id": receipt["receipt_id"],
        "created_at": receipt["created_at"],
        "allowed": receipt["allowed"],
        "outcome": receipt["outcome"],
        "judgment_mode": receipt["judgment_mode"],
        "reason_codes": receipt["reason_codes"],
        "judgment_context": receipt["judgment_context"],
        "judgment_act_hash": receipt["judgment_act_hash"],
        "judgment_against_boundary_hash": receipt["judgment_against_boundary_hash"],
        "judgment_cross_binding_hash": receipt["judgment_cross_binding_hash"],
    })
    return receipt

def replay_receipt(stored_receipt: Dict[str, Any], artifact: Dict[str, Any], state: Dict[str, Any], basis: Dict[str, Any]) -> Dict[str, Any]:
    fresh = evaluate_commit(artifact, state, basis)
    mismatches = []

    checks = [
        ("OUTCOME_MISMATCH", stored_receipt["outcome"], fresh["outcome"]),
        ("ALLOWED_MISMATCH", stored_receipt["allowed"], fresh["allowed"]),
        ("JUDGMENT_MODE_MISMATCH", stored_receipt["judgment_mode"], fresh["judgment_mode"]),
        ("REASON_CODES_MISMATCH", stored_receipt["reason_codes"], fresh["reason_codes"]),
        ("BOUNDARY_HASH_MISMATCH", stored_receipt["judgment_against_boundary_hash"], fresh["judgment_against_boundary_hash"]),
        ("CROSS_BINDING_HASH_MISMATCH", stored_receipt["judgment_cross_binding_hash"], fresh["judgment_cross_binding_hash"]),
    ]
    for code, left, right in checks:
        if left != right:
            mismatches.append(code)

    if stored_receipt["judgment_context"] != fresh["judgment_context"]:
        mismatches.append("JUDGMENT_CONTEXT_MISMATCH")

    return {
        "matches": not mismatches,
        "mismatches": mismatches,
        "fresh": fresh,
    }

def run_proof(stress: int = 0) -> Dict[str, Any]:
    basis = build_governing_basis()
    state = build_state()
    payload = build_demo_payload()
    artifact = sign_artifact(payload, state, basis)

    receipt = evaluate_commit(artifact, state, basis)
    replay = replay_receipt(receipt, artifact, state, basis)

    tampered_artifact = copy.deepcopy(artifact)
    tampered_artifact["execution_branch_id"] = "beta"
    tampered_artifact["artifact_hash"] = sha256_obj({
        "artifact_id": tampered_artifact["artifact_id"],
        "payload_hash": tampered_artifact["payload_hash"],
        "state_ref": tampered_artifact["state_ref"],
        "declared_state_hash": tampered_artifact["declared_state_hash"],
        "declared_status": tampered_artifact["declared_status"],
        "authority_scope": tampered_artifact["authority_scope"],
        "execution_branch_id": tampered_artifact["execution_branch_id"],
        "basis_id": tampered_artifact["basis_id"],
        "basis_version": tampered_artifact["basis_version"],
        "basis_hash": tampered_artifact["basis_hash"],
        "workflow_step": tampered_artifact["workflow_step"],
        "requested_transition": tampered_artifact["requested_transition"],
    })
    tampered_replay = replay_receipt(receipt, tampered_artifact, state, basis)

    report = {
        "proof": {
            "corridor": {
                "transition": "approve_order",
                "commit_boundary": "attending_signoff",
                "authority_scope": ["commit_scope"],
                "negative_case": "execution_branch_id=beta",
            },
            "basis": {
                "basis_id": basis["basis_id"],
                "version": basis["version"],
                "basis_hash": basis["basis_hash"],
            },
            "positive": {
                "allowed": receipt["allowed"],
                "outcome": receipt["outcome"],
                "judgment_mode": receipt["judgment_mode"],
                "reason_codes": receipt["reason_codes"],
                "receipt_id": receipt["receipt_id"],
                "receipt_hash": receipt["receipt_hash"],
                "judgment_against_boundary_hash": receipt["judgment_against_boundary_hash"],
                "judgment_cross_binding_hash": receipt["judgment_cross_binding_hash"],
                "replay": replay,
            },
            "negative": {
                "mutation": "execution_branch_id=beta",
                "replay": tampered_replay,
            },
        }
    }

    if stress > 0:
        boundary_hashes = []
        cross_binding_hashes = []
        outcomes = []
        replay_matches = []
        for _ in range(stress):
            r = run_proof(stress=0)["proof"]["positive"]
            boundary_hashes.append(r["judgment_against_boundary_hash"])
            cross_binding_hashes.append(r["judgment_cross_binding_hash"])
            outcomes.append(r["outcome"])
            replay_matches.append(r["replay"]["matches"])
        report["stress"] = {
            "iterations": stress,
            "unique_judgment_against_boundary_hash_count": len(set(boundary_hashes)),
            "unique_judgment_cross_binding_hash_count": len(set(cross_binding_hashes)),
            "unique_outcomes": sorted(set(outcomes)),
            "all_positive_replays_match": all(replay_matches),
            "deterministic": len(set(boundary_hashes)) == 1 and len(set(cross_binding_hashes)) == 1 and sorted(set(outcomes)) == ["SAFE_COMMIT"] and all(replay_matches),
        }

    return report
