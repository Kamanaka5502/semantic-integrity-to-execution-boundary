
from __future__ import annotations
from dataclasses import replace
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from .basis import GoverningBasis
from .contracts import (
    ARTIFACT_CONTRACT_VERSION, ARTIFACT_KIND, RECEIPT_CONTRACT_VERSION, RECEIPT_KIND,
    ArtifactIntegrity, ArtifactSectionIntegrity, CommitRequest, CommitResult,
    ContinuationJudgment, DecisionReceipt, ExecutionArtifact, JudgmentContext,
    OutcomeJudgment, PreservationRecord, ReceiptIntegrity, ReceiptSectionIntegrity,
    StandingJudgment, boundary_claim_material, branch_witness_material,
    continuity_witness_material, continuation_carry_material, continuation_preservation_binding_material,
    executable_act_material, continuation_act_material, judgment_against_boundary_material, judgment_witness_material,
    preservation_witness_material, standing_witness_material, outcome_witness_material,
    translation_witness_material, utcnow_iso,
)
from .derivative_ordering import evaluate_derivative_ordering
from .receipts import lawful_context_material, lawful_context_proof
from .state import snapshot_from_record
from .storage import JsonStore
from .util import sha256_obj, sign_material, verify_signature

class VeritasAegisEngine:
    def __init__(self, *, store_root: str, basis_secret: str = "basis-secret", receipt_secret: str = "receipt-secret", artifact_secret: str = "artifact-secret"):
        self.store = JsonStore(store_root)
        self.basis_secret = basis_secret
        self.receipt_secret = receipt_secret
        self.artifact_secret = artifact_secret

    def put_basis(self, basis: Dict[str, Any]) -> GoverningBasis:
        gb = GoverningBasis.from_dict(basis, secret=self.basis_secret)
        self.store.put("basis", gb.basis_id, gb.to_dict())
        self.store.put("basis_versions", f"{gb.basis_id}:{gb.version}", gb.to_dict())
        return gb

    def get_basis(self, basis_id: str) -> GoverningBasis:
        data = self.store.get("basis", basis_id)
        if not data:
            raise KeyError(f"unknown governing basis: {basis_id}")
        return GoverningBasis.from_dict(data, secret=self.basis_secret)

    def put_state(self, state_ref: str, state: Dict[str, Any]) -> None:
        normalized = {
            "entity_id": state["entity_id"],
            "current_status": state["current_status"],
            "attributes": state.get("attributes", {}),
            "open_burdens": list(state.get("open_burdens", [])),
            "continuity_chain_head": state.get("continuity_chain_head"),
            "continuity_debt": list(state.get("continuity_debt", [])),
        }
        self.store.put("state", state_ref, normalized)

    def get_state_record(self, state_ref: str) -> Dict[str, Any]:
        data = self.store.get("state", state_ref)
        if not data:
            raise KeyError(f"unknown state_ref: {state_ref}")
        return data

    def resolve_state(self, state_ref: str):
        return snapshot_from_record(state_ref, self.get_state_record(state_ref), resolved_at=utcnow_iso())

    def _seal_artifact_section(self, name: str, payload: Dict[str, Any]) -> ArtifactSectionIntegrity:
        return ArtifactSectionIntegrity(
            section=name,
            section_hash=sha256_obj(payload),
            section_signature=sign_material(self.artifact_secret, {"section": name, "payload": payload}),
        )

    def sign_artifact(self, artifact: ExecutionArtifact) -> ExecutionArtifact:
        intent = self._seal_artifact_section("intent", artifact.intent_surface.to_dict())
        translation = self._seal_artifact_section("translation", artifact.translation_record.to_dict())
        law = self._seal_artifact_section("law", artifact.law_binding.to_dict())
        continuity = self._seal_artifact_section("continuity", artifact.continuity_entry.to_dict())
        branch = self._seal_artifact_section("branch", artifact.branch_posture.to_dict())
        provisional = replace(
            artifact,
            integrity=ArtifactIntegrity(
                payload_hash=sha256_obj(artifact.payload),
                intent=intent,
                translation=translation,
                law=law,
                continuity=continuity,
                branch=branch,
                bridge_hash=sha256_obj(artifact.bridge_material()),
                witness_hash=sha256_obj(artifact.witness_material()),
                executable_act_hash="",
                continuation_act_hash="",
                boundary_act_hash="",
                cross_binding_hash="",
                boundary_claim_hash="",
                claim_surface_hash="",
                proof_surface_hash="",
                artifact_signature=None,
            ),
        )
        executable_act_hash = sha256_obj(provisional.executable_act_material())
        continuation_act_hash = sha256_obj(provisional.continuation_act_material())
        boundary_act_hash = sha256_obj(provisional.boundary_act_material())
        provisional = replace(
            provisional,
            integrity=replace(
                provisional.integrity,
                executable_act_hash=executable_act_hash,
                continuation_act_hash=continuation_act_hash,
                boundary_act_hash=boundary_act_hash,
            ),
        )
        cross_binding_hash = sha256_obj(provisional.cross_binding_material())
        boundary_claim_hash = sha256_obj(provisional.boundary_claim_material())
        provisional = replace(
            provisional,
            integrity=replace(
                provisional.integrity,
                cross_binding_hash=cross_binding_hash,
                boundary_claim_hash=boundary_claim_hash,
            ),
        )
        claim_surface_hash = sha256_obj(provisional.claim_surface_material())
        provisional = replace(
            provisional,
            integrity=replace(
                provisional.integrity,
                claim_surface_hash=claim_surface_hash,
            ),
        )
        proof_surface_hash = sha256_obj(provisional.proof_surface_material())
        provisional = replace(
            provisional,
            integrity=replace(
                provisional.integrity,
                proof_surface_hash=proof_surface_hash,
            ),
        )
        signature = sign_material(self.artifact_secret, provisional.signable_dict())
        signed = replace(provisional, integrity=replace(provisional.integrity, artifact_signature=signature))
        proof_surface_hash = sha256_obj(signed.proof_surface_material())
        signed = replace(signed, integrity=replace(signed.integrity, proof_surface_hash=proof_surface_hash))
        signature = sign_material(self.artifact_secret, signed.signable_dict())
        return replace(signed, integrity=replace(signed.integrity, artifact_signature=signature))

    def evaluate(self, request: CommitRequest) -> DecisionReceipt:
        artifact = request.artifact
        basis = self.get_basis(artifact.governing_basis_id)
        state = self.resolve_state(artifact.state_ref)
        self.store.put("snapshots", state.state_hash, state.to_dict())
        receipt = self._evaluate_internal(artifact, basis, state)
        self._write_evaluation_record(artifact, basis, state.state_hash, receipt)
        return receipt

    def commit(self, request: CommitRequest) -> CommitResult:
        artifact = request.artifact
        pre_state = self.resolve_state(artifact.state_ref)
        receipt = self.evaluate(request)
        self.store.put("receipts", receipt.receipt_id, receipt.to_dict())
        self.store.append(
            "receipt_judgments",
            {"receipt_id": receipt.receipt_id, "artifact_id": receipt.artifact_id, "outcome": receipt.outcome},
            unique_key=f"receipt:{receipt.receipt_id}",
        )
        if receipt.outcome != "SAFE_COMMIT":
            if receipt.outcome == "REFUSE_BLOCK":
                self._record_preservation_refusal(receipt, pre_state.state_ref, pre_state.state_hash)
            if receipt.outcome == "ESCALATE":
                self._record_escalation(receipt, artifact, self.get_basis(artifact.governing_basis_id))
            return CommitResult(False, receipt, pre_state.state_hash, None, None, "commit blocked")
        basis = self.get_basis(artifact.governing_basis_id)
        transition = basis.rules["transitions"][artifact.requested_transition]
        record = self.get_state_record(artifact.state_ref)
        record["current_status"] = transition["to"]
        record["continuity_chain_head"] = receipt.receipt_id
        record["continuity_debt"] = list(receipt.continuation_judgment.continuity_debt_out)
        self.put_state(artifact.state_ref, record)
        post_state = self.resolve_state(artifact.state_ref)
        return CommitResult(True, receipt, pre_state.state_hash, post_state.state_hash, transition["to"], "commit applied")

    def replay(self, receipt_id: str, artifact: ExecutionArtifact) -> Dict[str, Any]:
        stored = DecisionReceipt.from_dict(self.store.get("receipts", receipt_id))
        snapshot = self.store.get("snapshots", stored.judgment_context.state_hash)
        basis = GoverningBasis.from_dict(self.store.get("basis_versions", f"{stored.judgment_context.governing_basis_id}:{stored.judgment_context.governing_basis_version}"), secret=self.basis_secret)
        state = snapshot_from_record(snapshot["state_ref"], snapshot, resolved_at=snapshot.get("resolved_at", "snapshot"))
        fresh = self._evaluate_internal(artifact, basis, state)
        mismatches: List[str] = []
        checks = [
            ("ARTIFACT_BOUNDARY_ACT_HASH_MISMATCH", stored.judgment_context.artifact_boundary_act_hash, fresh.judgment_context.artifact_boundary_act_hash),
            ("JUDGMENT_ACT_HASH_MISMATCH", stored.integrity.judgment_act_hash, fresh.integrity.judgment_act_hash),
            ("JUDGMENT_AGAINST_BOUNDARY_HASH_MISMATCH", stored.integrity.judgment_against_boundary_hash, fresh.integrity.judgment_against_boundary_hash),
            ("CONTINUATION_PRESERVATION_BINDING_HASH_MISMATCH", stored.integrity.continuation_preservation_binding_hash, fresh.integrity.continuation_preservation_binding_hash),
            ("CONTINUATION_WITNESS_HASH_MISMATCH", stored.continuation_judgment.continuation_witness_hash, fresh.continuation_judgment.continuation_witness_hash),
            ("CARRY_FORWARD_HASH_MISMATCH", stored.continuation_judgment.carry_forward_hash, fresh.continuation_judgment.carry_forward_hash),
            ("PRESERVATION_WITNESS_HASH_MISMATCH", stored.preservation_record.preservation_witness_hash, fresh.preservation_record.preservation_witness_hash),
            ("LAWFUL_CONTEXT_PROOF_MISMATCH", stored.lawful_context_proof, fresh.lawful_context_proof),
        ]
        for code, left, right in checks:
            if left != right:
                mismatches.append(code)
        if stored.judgment_context.to_dict() != fresh.judgment_context.to_dict():
            mismatches.append("JUDGMENT_CONTEXT_MISMATCH")
        if stored.standing_judgment.to_dict() != fresh.standing_judgment.to_dict():
            mismatches.append("STANDING_JUDGMENT_MISMATCH")
        if stored.continuation_judgment.to_dict() != fresh.continuation_judgment.to_dict():
            mismatches.append("CONTINUATION_JUDGMENT_MISMATCH")
        if stored.outcome_judgment.to_dict() != fresh.outcome_judgment.to_dict():
            mismatches.append("OUTCOME_JUDGMENT_MISMATCH")
        if stored.preservation_record.to_dict() != fresh.preservation_record.to_dict():
            mismatches.append("PRESERVATION_RECORD_MISMATCH")
        return {"matches": not mismatches, "mismatches": mismatches, "stored": stored.to_dict(), "fresh": fresh.to_dict()}

    def verify_receipt(self, receipt: Dict[str, Any]) -> bool:
        return self._verify_receipt_integrity(DecisionReceipt.from_dict(receipt))

    def _verify_artifact_integrity(self, artifact: ExecutionArtifact) -> List[str]:
        reasons: List[str] = []
        if artifact.integrity.payload_hash != sha256_obj(artifact.payload):
            reasons.append("PAYLOAD_HASH_MISMATCH")
        for name, payload in [
            ("intent", artifact.intent_surface.to_dict()),
            ("translation", artifact.translation_record.to_dict()),
            ("law", artifact.law_binding.to_dict()),
            ("continuity", artifact.continuity_entry.to_dict()),
            ("branch", artifact.branch_posture.to_dict()),
        ]:
            sec = getattr(artifact.integrity, name)
            if sec.section != name:
                reasons.append(f"{name.upper()}_SECTION_NAME_MISMATCH")
            if sec.section_hash != sha256_obj(payload):
                reasons.append(f"{name.upper()}_SECTION_HASH_MISMATCH")
            if not verify_signature(self.artifact_secret, {"section": name, "payload": payload}, sec.section_signature):
                reasons.append(f"{name.upper()}_SECTION_SIGNATURE_INVALID")
        if artifact.integrity.bridge_hash != sha256_obj(artifact.bridge_material()):
            reasons.append("ARTIFACT_BRIDGE_HASH_MISMATCH")
        if artifact.integrity.witness_hash != sha256_obj(artifact.witness_material()):
            reasons.append("ARTIFACT_WITNESS_HASH_MISMATCH")
        if artifact.integrity.executable_act_hash != sha256_obj(artifact.executable_act_material()):
            reasons.append("ARTIFACT_EXECUTABLE_ACT_HASH_MISMATCH")
        if artifact.integrity.continuation_act_hash != sha256_obj(artifact.continuation_act_material()):
            reasons.append("ARTIFACT_CONTINUATION_ACT_HASH_MISMATCH")
        if artifact.integrity.boundary_act_hash != sha256_obj(artifact.boundary_act_material()):
            reasons.append("ARTIFACT_BOUNDARY_ACT_HASH_MISMATCH")
        expected_translation_witness = sha256_obj(translation_witness_material(
            payload=artifact.payload,
            intent=artifact.intent_surface.to_dict(),
            translation={k: v for k, v in artifact.translation_record.to_dict().items() if k != "translation_witness_hash"},
            law=artifact.law_binding.to_dict(),
        ))
        if artifact.translation_witness_hash != expected_translation_witness:
            reasons.append("TRANSLATION_WITNESS_HASH_MISMATCH")
        expected_continuity_witness = sha256_obj(continuity_witness_material(
            continuity={k: v for k, v in artifact.continuity_entry.to_dict().items() if k != "continuity_witness_hash"}
        ))
        if artifact.continuity_witness_hash != expected_continuity_witness:
            reasons.append("CONTINUITY_WITNESS_HASH_MISMATCH")
        expected_branch_witness = sha256_obj(branch_witness_material(
            branch={k: v for k, v in artifact.branch_posture.to_dict().items() if k != "branch_witness_hash"},
            translation=artifact.translation_record.to_dict(),
        ))
        if artifact.branch_witness_hash != expected_branch_witness:
            reasons.append("BRANCH_WITNESS_HASH_MISMATCH")
        if artifact.integrity.cross_binding_hash != sha256_obj(artifact.cross_binding_material()):
            reasons.append("ARTIFACT_CROSS_BINDING_HASH_MISMATCH")
        expected_boundary_claim = sha256_obj(artifact.boundary_claim_material())
        if artifact.integrity.boundary_claim_hash != expected_boundary_claim:
            reasons.append("ARTIFACT_BOUNDARY_CLAIM_HASH_MISMATCH")
        if artifact.integrity.claim_surface_hash != sha256_obj(artifact.claim_surface_material()):
            reasons.append("ARTIFACT_CLAIM_SURFACE_HASH_MISMATCH")
        if artifact.integrity.proof_surface_hash != sha256_obj(artifact.proof_surface_material()):
            reasons.append("ARTIFACT_PROOF_SURFACE_HASH_MISMATCH")
        if not verify_signature(self.artifact_secret, artifact.signable_dict(), artifact.artifact_signature):
            reasons.append("ARTIFACT_SIGNATURE_INVALID")
        return reasons

    def _verify_receipt_integrity(self, receipt: DecisionReceipt) -> bool:
        sections = {
            "judgment_context": receipt.judgment_context.to_dict(),
            "standing_judgment": receipt.standing_judgment.to_dict(),
            "continuation_judgment": receipt.continuation_judgment.to_dict(),
            "outcome_judgment": receipt.outcome_judgment.to_dict(),
            "preservation_record": receipt.preservation_record.to_dict(),
        }
        for name, payload in sections.items():
            sec = getattr(receipt.integrity, name)
            if sec.section != name or sec.section_hash != sha256_obj(payload):
                return False
            if not verify_signature(self.receipt_secret, {"section": name, "payload": payload}, sec.section_signature):
                return False
        if receipt.lawful_context_proof != lawful_context_proof(lawful_context_material(receipt=receipt)):
            return False
        expected_continuation_witness = sha256_obj({
            "continuity_mode": receipt.continuation_judgment.continuity_mode,
            "continuation_intent": receipt.continuation_judgment.continuation_intent,
            "continuation_constraints": list(receipt.continuation_judgment.continuation_constraints),
            "expected_continuation_result": receipt.continuation_judgment.expected_continuation_result,
            "continuity_debt_in": list(receipt.continuation_judgment.continuity_debt_in),
            "continuity_debt_out": list(receipt.continuation_judgment.continuity_debt_out),
            "parent_receipt_witness_hash": receipt.continuation_judgment.parent_receipt_witness_hash,
            "parent_branch_id": receipt.continuation_judgment.parent_branch_id,
            "continuation_result": receipt.continuation_judgment.continuation_result,
            "inherited_condition": receipt.continuation_judgment.inherited_continuity_condition,
            "carry_directive": receipt.continuation_judgment.carry_directive,
            "debt_action": receipt.continuation_judgment.debt_action,
        })
        if receipt.continuation_judgment.continuation_witness_hash != expected_continuation_witness:
            return False
        expected_carry = sha256_obj(continuation_carry_material(
            continuity_debt_in=receipt.continuation_judgment.continuity_debt_in,
            continuity_debt_out=receipt.continuation_judgment.continuity_debt_out,
            continuation_mode=receipt.continuation_judgment.continuity_mode,
            inherited_condition=receipt.continuation_judgment.inherited_continuity_condition,
            parent_receipt_witness_hash=receipt.continuation_judgment.parent_receipt_witness_hash,
            parent_branch_id=receipt.continuation_judgment.parent_branch_id,
            continuation_result=receipt.continuation_judgment.continuation_result,
            self_continuation_lawful=receipt.continuation_judgment.self_continuation_lawful,
            continuation_corridor=receipt.continuation_judgment.continuation_corridor,
            carry_directive=receipt.continuation_judgment.carry_directive,
            carry_constraints=receipt.continuation_judgment.continuation_constraints,
            carry_reason_codes=receipt.continuation_judgment.carry_reason_codes,
            debt_action=receipt.continuation_judgment.debt_action,
            next_required_witnesses=receipt.continuation_judgment.next_required_witnesses,
        ))
        if receipt.continuation_judgment.carry_forward_hash != expected_carry:
            return False
        expected_preservation = sha256_obj(preservation_witness_material(
            preserved_manifold=receipt.preservation_record.preserved_manifold,
            preservation_reason=receipt.preservation_record.preservation_reason,
            preserved_transition=receipt.preservation_record.preserved_transition,
            preserved_state_hash=receipt.preservation_record.preserved_state_hash,
            preserved_basis_hash=receipt.preservation_record.preserved_basis_hash,
            preserved_branch_id=receipt.preservation_record.preserved_branch_id,
            refusal_preserves_manifold=receipt.preservation_record.refusal_preserves_manifold,
            prevented_branch_drift=receipt.preservation_record.prevented_branch_drift,
            redirect_open=receipt.preservation_record.redirect_open,
            self_continuation_terminated=receipt.preservation_record.self_continuation_terminated,
            preservation_result=receipt.preservation_record.preservation_result,
            blocked_transition=receipt.preservation_record.blocked_transition,
            continuation_disposition=receipt.preservation_record.continuation_disposition,
            preservation_reason_codes=receipt.preservation_record.preservation_reason_codes,
            preservation_actions=receipt.preservation_record.preservation_actions,
            preserved_continuation_corridor=receipt.preservation_record.preserved_continuation_corridor,
            preserved_debt_hash=receipt.preservation_record.preserved_debt_hash,
        ))
        if receipt.preservation_record.preservation_witness_hash != expected_preservation:
            return False
        expected_standing_witness = sha256_obj(standing_witness_material(
            standing_before=receipt.standing_judgment.standing_before,
            standing_after=receipt.standing_judgment.standing_after,
            standing_result=receipt.standing_judgment.standing_result,
            standing_change_reason=receipt.standing_judgment.standing_change_reason,
            authority_scope_used=receipt.standing_judgment.authority_scope_used,
            standing_narrowed_by=receipt.standing_judgment.standing_narrowed_by,
        ))
        if receipt.standing_judgment.standing_witness_hash != expected_standing_witness:
            return False
        expected_outcome_witness = sha256_obj(outcome_witness_material(
            admissibility_result=receipt.outcome_judgment.admissibility_result,
            burden_result=receipt.outcome_judgment.burden_result,
            outcome=receipt.outcome_judgment.outcome,
            judgment_mode=receipt.outcome_judgment.judgment_mode,
            escalation_target=receipt.outcome_judgment.escalation_target,
            reason_codes=receipt.outcome_judgment.reason_codes,
            preserved_transition=receipt.outcome_judgment.preserved_transition,
        ))
        if receipt.outcome_judgment.outcome_witness_hash != expected_outcome_witness:
            return False

        expected_judgment_witness = sha256_obj(judgment_witness_material(
            judgment_context=receipt.judgment_context.to_dict(),
            standing_judgment=receipt.standing_judgment.to_dict(),
            continuation_judgment=receipt.continuation_judgment.to_dict(),
            outcome_judgment=receipt.outcome_judgment.to_dict(),
            preservation_record=receipt.preservation_record.to_dict(),
        ))
        if receipt.integrity.judgment_witness_hash != expected_judgment_witness:
            return False
        if receipt.integrity.judgment_act_hash != sha256_obj(receipt.judgment_act_material()):
            return False
        expected_against_boundary = sha256_obj(judgment_against_boundary_material(
            artifact_boundary_act_hash=receipt.judgment_context.artifact_boundary_act_hash,
            judgment_act_hash=receipt.integrity.judgment_act_hash,
            outcome_judgment=receipt.outcome_judgment.to_dict(),
            continuation_judgment=receipt.continuation_judgment.to_dict(),
            preservation_record=receipt.preservation_record.to_dict(),
        ))
        if receipt.integrity.judgment_against_boundary_hash != expected_against_boundary:
            return False
        expected_continuation_preservation_binding = sha256_obj(continuation_preservation_binding_material(
            artifact_boundary_act_hash=receipt.judgment_context.artifact_boundary_act_hash,
            continuation_judgment=receipt.continuation_judgment.to_dict(),
            preservation_record=receipt.preservation_record.to_dict(),
        ))
        if receipt.integrity.continuation_preservation_binding_hash != expected_continuation_preservation_binding:
            return False
        expected_judgment_cross_binding = sha256_obj({
            "artifact_boundary_claim_hash": receipt.judgment_context.artifact_boundary_claim_hash,
            "artifact_boundary_act_hash": receipt.judgment_context.artifact_boundary_act_hash,
            "artifact_executable_act_hash": receipt.judgment_context.artifact_executable_act_hash,
            "artifact_continuation_act_hash": receipt.judgment_context.artifact_continuation_act_hash,
            "artifact_cross_binding_hash": receipt.judgment_context.artifact_cross_binding_hash,
            "translation_witness_hash": receipt.judgment_context.translation_witness_hash,
            "continuity_witness_hash": receipt.judgment_context.continuity_witness_hash,
            "branch_witness_hash": receipt.judgment_context.branch_witness_hash,
            "judgment_witness_hash": receipt.integrity.judgment_witness_hash,
            "judgment_act_hash": receipt.integrity.judgment_act_hash,
            "judgment_against_boundary_hash": receipt.integrity.judgment_against_boundary_hash,
            "continuation_preservation_binding_hash": receipt.integrity.continuation_preservation_binding_hash,
            "continuation_witness_hash": receipt.continuation_judgment.continuation_witness_hash,
            "carry_forward_hash": receipt.continuation_judgment.carry_forward_hash,
            "preservation_witness_hash": receipt.preservation_record.preservation_witness_hash,
            "lawful_context_proof": receipt.integrity.lawful_context_proof,
        })
        if receipt.integrity.judgment_cross_binding_hash != expected_judgment_cross_binding:
            return False
        if receipt.integrity.receipt_binding_hash != sha256_obj(receipt.binding_material()):
            return False
        if receipt.integrity.judgment_surface_hash != sha256_obj(receipt.integrity.judgment_surface()):
            return False
        if receipt.integrity.proof_surface_hash != sha256_obj(receipt.integrity.proof_surface()):
            return False
        data = receipt.to_dict()
        data["proof"] = dict(data["proof"])
        claimed_hash = data["proof"]["receipt_hash"]
        data["proof"]["receipt_signature"] = ""
        if claimed_hash != sha256_obj({**data, "proof": {**data["proof"], "receipt_hash": ""}}):
            return False
        return verify_signature(self.receipt_secret, data, receipt.receipt_signature)

    def _evaluate_internal(self, artifact: ExecutionArtifact, basis: GoverningBasis, state) -> DecisionReceipt:
        reasons = []
        reasons += self._validate_basis_binding(artifact, basis)
        reasons += self._validate_structural(artifact, basis)
        reasons += self._validate_artifact_truth(artifact, state)
        reasons += self._validate_translation_discipline(artifact)
        reasons += self._validate_continuation_discipline(artifact)
        reasons += evaluate_derivative_ordering(artifact, basis)
        if reasons:
            return self._issue_receipt(artifact, basis, state, "NONE", "INVALID", "INVALID", "DENY", "DENY", "TERMINAL", "REFUSE_BLOCK", reasons, None, None)
        standing, s_reasons, standing_after, standing_change_reason, scope_used, narrowed_by = self._evaluate_standing(artifact, basis)
        admissibility, a_reasons = self._evaluate_admissibility(artifact, state, basis)
        continuation, c_reasons, inherited_cond, self_cont_ok, parent_branch_id, parent_continuity_verified = self._evaluate_continuation(artifact, state, basis)
        burden, b_reasons, debt_out = self._evaluate_burden(state, standing, continuation)
        esc_target = self._select_escalation_target(artifact, basis, standing, admissibility, continuation, burden)
        outcome, o_reasons = self._classify_outcome(standing, admissibility, continuation, burden)
        carry_directive = "CONTINUE_SELF"
        if outcome == "ESCALATE":
            carry_directive = "ESCALATE_TO_CORRIDOR"
        elif continuation == "DENY" or outcome == "REFUSE_BLOCK":
            carry_directive = "TERMINATE_SELF"
        debt_action = "UNCHANGED"
        if debt_out and debt_out != list(artifact.continuity_debt_in):
            debt_action = "TIGHTENED"
        elif not debt_out and artifact.continuity_debt_in:
            debt_action = "EXTINGUISHED"
        next_required_witnesses = []
        if outcome == "ESCALATE":
            next_required_witnesses = ["escalation_receipt", "corridor_authorization"]
        elif artifact.parent_receipt_id:
            next_required_witnesses = ["parent_receipt_witness"]
        return self._issue_receipt(artifact, basis, state, state.current_status, standing, standing_after, admissibility, continuation, burden, outcome, s_reasons+a_reasons+c_reasons+b_reasons+o_reasons, esc_target, {
            "standing_change_reason": standing_change_reason,
            "authority_scope_used": scope_used,
            "standing_narrowed_by": narrowed_by,
            "inherited_condition": inherited_cond,
            "self_continuation_lawful": self_cont_ok,
            "parent_branch_id": parent_branch_id,
            "parent_continuity_verified": parent_continuity_verified,
            "continuity_debt_out": debt_out,
            "carry_directive": carry_directive,
            "carry_reason_codes": c_reasons + b_reasons + o_reasons,
            "debt_action": debt_action,
            "next_required_witnesses": next_required_witnesses,
        })

    def _validate_basis_binding(self, artifact: ExecutionArtifact, basis: GoverningBasis) -> List[str]:
        reasons = []
        if artifact.law_binding.contract_version != ARTIFACT_CONTRACT_VERSION:
            reasons.append("ARTIFACT_CONTRACT_VERSION_MISMATCH")
        if artifact.law_binding.artifact_kind != ARTIFACT_KIND:
            reasons.append("ARTIFACT_KIND_MISMATCH")
        if artifact.governing_basis_version != basis.version:
            reasons.append("GOVERNING_BASIS_VERSION_MISMATCH")
        if artifact.governing_basis_hash != basis.basis_hash:
            reasons.append("GOVERNING_BASIS_HASH_MISMATCH")
        if artifact.basis_lineage_hash != basis.lineage_hash:
            reasons.append("BASIS_LINEAGE_MISMATCH")
        if artifact.basis_signature != basis.signature:
            reasons.append("BASIS_SIGNATURE_BINDING_MISMATCH")
        return reasons

    def _validate_structural(self, artifact: ExecutionArtifact, basis: GoverningBasis) -> List[str]:
        reasons = self._verify_artifact_integrity(artifact)
        schema = basis.rules["schema"]
        if artifact.schema_id != schema["schema_id"]:
            reasons.append("SCHEMA_ID_MISMATCH")
        if artifact.schema_version != schema["schema_version"]:
            reasons.append("SCHEMA_VERSION_MISMATCH")
        if artifact.constraint_bundle_hash != schema["constraint_bundle_hash"]:
            reasons.append("CONSTRAINT_BUNDLE_HASH_MISMATCH")
        missing = sorted(set(schema["required_payload_fields"]) - set(artifact.payload))
        reasons.extend([f"MISSING_PAYLOAD_FIELD:{m}" for m in missing])
        if artifact.executable_claim != artifact.requested_transition:
            reasons.append("EXECUTABLE_CLAIM_MISMATCH")
        return reasons


    def _validate_translation_discipline(self, artifact: ExecutionArtifact) -> List[str]:
        reasons: List[str] = []
        outcome = artifact.translation_outcome
        allowed = {"PRESERVE", "NARROW", "REDIRECT"}
        if outcome not in allowed:
            reasons.append("TRANSLATION_OUTCOME_INVALID")
            return reasons
        if not artifact.source_intent.strip():
            reasons.append("SOURCE_INTENT_EMPTY")
        if not artifact.executable_claim.strip():
            reasons.append("EXECUTABLE_CLAIM_EMPTY")
        if not artifact.translation_constraints:
            reasons.append("TRANSLATION_CONSTRAINTS_EMPTY")
        if outcome == "PRESERVE":
            if artifact.translation_narrowing:
                reasons.append("PRESERVE_CANNOT_NARROW")
            if not artifact.preserved_claims:
                reasons.append("PRESERVE_REQUIRES_PRESERVED_CLAIMS")
        elif outcome == "NARROW":
            if not artifact.translation_narrowing:
                reasons.append("NARROW_REQUIRES_NARROWING")
        elif outcome == "REDIRECT":
            if not artifact.declared_escalation_target:
                reasons.append("REDIRECT_REQUIRES_DECLARED_TARGET")
        return reasons



    def _validate_continuation_discipline(self, artifact: ExecutionArtifact) -> List[str]:
        reasons: List[str] = []
        allowed_modes = {"self", "parent", "redirect"}
        expected_allowed = {"ALLOW", "ESCALATE", "DENY"}
        if artifact.continuity_mode not in allowed_modes:
            reasons.append("CONTINUITY_MODE_INVALID")
        if not artifact.continuation_intent.strip():
            reasons.append("CONTINUATION_INTENT_EMPTY")
        if not artifact.continuation_constraints:
            reasons.append("CONTINUATION_CONSTRAINTS_EMPTY")
        if artifact.expected_continuation_result not in expected_allowed:
            reasons.append("EXPECTED_CONTINUATION_RESULT_INVALID")
        if artifact.continuity_mode == "parent" and not artifact.parent_receipt_id:
            reasons.append("PARENT_MODE_REQUIRES_PARENT_RECEIPT")
        if artifact.continuity_mode == "redirect" and not artifact.declared_escalation_target:
            reasons.append("REDIRECT_MODE_REQUIRES_DECLARED_TARGET")
        if artifact.continuity_mode == "self" and artifact.parent_receipt_id:
            reasons.append("SELF_MODE_CANNOT_DECLARE_PARENT_RECEIPT")
        return reasons

    def _validate_artifact_truth(self, artifact: ExecutionArtifact, state) -> List[str]:
        ce = artifact.continuity_entry
        reasons = []
        if ce.declared_state_hash != state.state_hash:
            reasons.append("DECLARED_STATE_HASH_MISMATCH")
        if ce.declared_entity_id != state.entity_id:
            reasons.append("DECLARED_ENTITY_ID_MISMATCH")
        if ce.declared_current_status != state.current_status:
            reasons.append("DECLARED_CURRENT_STATUS_MISMATCH")
        if sorted(ce.declared_open_burden_codes) != sorted(state.open_burdens):
            reasons.append("DECLARED_OPEN_BURDEN_CODES_MISMATCH")
        if sorted(ce.inherited_burden_codes) != sorted(state.open_burdens):
            reasons.append("INHERITED_BURDEN_CODES_MISMATCH")
        if ce.continuity_debt_in != state.continuity_debt:
            reasons.append("DECLARED_CONTINUITY_DEBT_MISMATCH")
        if ce.expected_continuation_result == "ALLOW" and ce.continuity_debt_in:
            reasons.append("EXPECTED_ALLOW_WITH_OPEN_CONTINUITY_DEBT")
        if ce.expected_continuation_result == "ALLOW" and ce.continuity_mode == "redirect":
            reasons.append("EXPECTED_ALLOW_WITH_REDIRECT_MODE")
        if ce.parent_receipt_id:
            parent_data = self.store.get("receipts", ce.parent_receipt_id)
            if not parent_data:
                reasons.append("UNKNOWN_PARENT_RECEIPT")
            else:
                parent = DecisionReceipt.from_dict(parent_data)
                if ce.parent_receipt_signature != parent.receipt_signature:
                    reasons.append("PARENT_RECEIPT_SIGNATURE_MISMATCH")
                if ce.parent_receipt_witness_hash != parent.lawful_context_proof:
                    reasons.append("PARENT_RECEIPT_WITNESS_MISMATCH")
        elif ce.parent_receipt_signature or ce.parent_receipt_witness_hash:
            reasons.append("PARENT_WITNESS_WITHOUT_PARENT_ID")
        return reasons

    def _evaluate_standing(self, artifact: ExecutionArtifact, basis: GoverningBasis) -> Tuple[str, List[str], str, Optional[str], List[str], List[str]]:
        actor_roles = set(basis.rules["actors"].get(artifact.actor_id, []))
        required = set(basis.rules["transitions"][artifact.requested_transition]["required_scope"])
        declared = set(artifact.authority_scope)
        effective = sorted(actor_roles & declared)
        if not actor_roles:
            return "INVALID", ["UNKNOWN_ACTOR"], "INVALID", "unknown_actor", effective, ["unknown_actor"]
        if not required.issubset(set(effective)):
            if actor_roles & required:
                return "PARTIAL", ["PARTIAL_STANDING_SCOPE"], "NARROWED", "scope_narrowed_by_declaration", effective, sorted(required - set(effective))
            return "INVALID", ["INSUFFICIENT_SCOPE"], "INVALID", "actor_lacks_required_scope", effective, sorted(required)
        return "VALID", [], "VALID", None, effective, []

    def _evaluate_admissibility(self, artifact: ExecutionArtifact, state, basis: GoverningBasis) -> Tuple[str, List[str]]:
        t = basis.rules["transitions"].get(artifact.requested_transition)
        if not t:
            return "DENY", ["UNKNOWN_TRANSITION"]
        if state.current_status not in t["from"]:
            return "DENY", [f"STATUS_NOT_ADMISSIBLE_FROM:{state.current_status}"]
        reasons = [f"PAYLOAD_FIELD_EMPTY:{f}" for f in t.get("required_payload_matches", []) if not artifact.payload.get(f)]
        if reasons:
            return "DENY", reasons
        if artifact.payload.get("risk_level", 0) > t.get("max_risk", 9999):
            return "CONDITIONAL", ["RISK_ABOVE_AUTO_COMMIT_THRESHOLD"]
        return "ALLOW", []

    def _evaluate_continuation(self, artifact: ExecutionArtifact, state, basis: GoverningBasis) -> Tuple[str, List[str], str, bool, Optional[str], bool]:
        required_parent = set(basis.rules.get("require_parent_receipt_for_statuses", []))
        parent_branch_id = None
        if state.current_status in required_parent and not artifact.parent_receipt_id:
            return "DENY", ["MISSING_PARENT_RECEIPT"], "parent_required", False, None, False
        if state.continuity_chain_head and artifact.parent_receipt_id != state.continuity_chain_head:
            return "DENY", ["PARENT_RECEIPT_CONTINUITY_MISMATCH"], "chain_head_mismatch", False, None, False
        if artifact.parent_receipt_id:
            parent = DecisionReceipt.from_dict(self.store.get("receipts", artifact.parent_receipt_id))
            parent_branch_id = parent.branch_id
            if parent.branch_id != artifact.execution_branch_id:
                return "DENY", ["PARENT_BRANCH_ID_MISMATCH"], "parent_branch_mismatch", False, parent_branch_id, False
            if parent.branch_derivation != artifact.branch_derivation:
                return "DENY", ["PARENT_DERIVATION_MISMATCH"], "parent_derivation_mismatch", False, parent_branch_id, False
        if state.continuity_debt:
            return "ESCALATE", ["CONTINUITY_DEBT_OPEN"], "debt_open", False, parent_branch_id, bool(artifact.parent_receipt_id)
        return "ALLOW", [], "clear", True, parent_branch_id, bool(artifact.parent_receipt_id) or not state.continuity_chain_head

    def _evaluate_burden(self, state, standing: str, continuation: str) -> Tuple[str, List[str], List[Dict[str, Any]]]:
        burdens = set(state.open_burdens)
        debt_out = list(state.continuity_debt)
        if "terminal_hold" in burdens:
            return "TERMINAL", ["TERMINAL_BURDEN_ACTIVE"], debt_out
        if debt_out:
            return "TIGHTENED", ["CONTINUITY_DEBT_TIGHTENS_THRESHOLD"], debt_out
        if burdens:
            debt_out = debt_out + [{"reason": "OPEN_BURDEN_CARRY", "source": sorted(burdens), "mode": "tightened"}]
            if standing == "VALID" and continuation in {"ALLOW", "ESCALATE"}:
                return "TIGHTENED", ["OPEN_BURDEN_TIGHTENS_THRESHOLD"], debt_out
            return "OPEN", ["OPEN_BURDEN_ACTIVE"], debt_out
        return "NONE", [], []

    def _select_escalation_target(self, artifact: ExecutionArtifact, basis: GoverningBasis, standing: str, admissibility: str, continuation: str, burden: str) -> Optional[str]:
        target = basis.rules.get("escalation_corridors", {}).get(artifact.requested_transition)
        if burden in {"TIGHTENED", "OPEN"} or standing == "PARTIAL" or admissibility == "CONDITIONAL" or continuation == "ESCALATE":
            return target
        return None

    def _classify_outcome(self, standing: str, admissibility: str, continuation: str, burden: str) -> Tuple[str, List[str]]:
        if burden == "TERMINAL":
            return "REFUSE_BLOCK", ["BURDEN_TERMINAL"]
        if standing == "INVALID":
            return "REFUSE_BLOCK", ["STANDING_INVALID"]
        if continuation == "DENY":
            return "REFUSE_BLOCK", ["CONTINUATION_UNLAWFUL"]
        if admissibility == "DENY":
            return "REFUSE_BLOCK", ["TRANSITION_INADMISSIBLE"]
        if standing == "PARTIAL":
            return "ESCALATE", ["PARTIAL_STANDING_ESCALATION_REQUIRED"]
        if continuation == "ESCALATE":
            return "ESCALATE", ["CONTINUATION_ESCALATION_REQUIRED"]
        if burden == "TIGHTENED":
            return "ESCALATE", ["BURDEN_REQUIRES_ESCALATION"]
        if admissibility == "CONDITIONAL":
            return "ESCALATE", ["ADMISSIBILITY_CONDITIONAL"]
        return "SAFE_COMMIT", ["LAWFUL_COMMIT_AUTHORIZED"]

    def _seal_receipt_section(self, name: str, payload: Dict[str, Any]) -> ReceiptSectionIntegrity:
        return ReceiptSectionIntegrity(
            section=name,
            section_hash=sha256_obj(payload),
            section_signature=sign_material(self.receipt_secret, {"section": name, "payload": payload}),
        )

    def _issue_receipt(self, artifact: ExecutionArtifact, basis: GoverningBasis, state, standing_before: str, standing: str, standing_after: str, admissibility: str, continuation: str, burden: str, outcome: str, reason_codes: List[str], escalation_target: Optional[str], details: Optional[Dict[str, Any]]) -> DecisionReceipt:
        d = details or {}
        jc = JudgmentContext(
            contract_version=RECEIPT_CONTRACT_VERSION,
            receipt_kind=RECEIPT_KIND,
            governing_basis_id=basis.basis_id,
            governing_basis_version=basis.version,
            governing_basis_hash=basis.basis_hash,
            governing_basis_lineage_hash=basis.lineage_hash,
            logic_version=artifact.logic_version,
            state_ref=artifact.state_ref,
            state_hash=state.state_hash,
            state_entity_id=state.entity_id,
            state_current_status=state.current_status,
            state_open_burden_codes=list(state.open_burdens),
            artifact_id=artifact.artifact_id,
            artifact_payload_hash=artifact.payload_hash,
            artifact_bridge_hash=artifact.integrity.bridge_hash,
            artifact_witness_hash=artifact.integrity.witness_hash,
            artifact_executable_act_hash=artifact.integrity.executable_act_hash,
            artifact_continuation_act_hash=artifact.integrity.continuation_act_hash,
            artifact_cross_binding_hash=artifact.integrity.cross_binding_hash,
            artifact_boundary_claim_hash=artifact.integrity.boundary_claim_hash,
            artifact_boundary_act_hash=artifact.integrity.boundary_act_hash,
            artifact_signature=artifact.artifact_signature or "",
            translation_witness_hash=artifact.translation_witness_hash,
            continuity_witness_hash=artifact.continuity_witness_hash,
            branch_witness_hash=artifact.branch_witness_hash,
            execution_branch_id=artifact.execution_branch_id,
            branch_role=artifact.branch_role,
            branch_derivation=artifact.branch_derivation,
            source_intent=artifact.source_intent,
            executable_claim=artifact.executable_claim,
            translation_digest=artifact.translation_digest,
            translation_outcome=artifact.translation_outcome,
            continuity_mode=artifact.continuity_mode,
            parent_receipt_id=artifact.parent_receipt_id,
            parent_receipt_witness_hash=artifact.parent_receipt_witness_hash,
            continuity_chain_head=artifact.continuity_chain_head,
        )
        standing_material = standing_witness_material(
            standing_before=standing_before,
            standing_after=standing_after,
            standing_result=standing,
            standing_change_reason=d.get("standing_change_reason"),
            authority_scope_used=list(d.get("authority_scope_used", [])),
            standing_narrowed_by=list(d.get("standing_narrowed_by", [])),
        )
        sj = StandingJudgment(
            standing_before=standing_before,
            standing_after=standing_after,
            standing_result=standing,
            standing_change_reason=d.get("standing_change_reason"),
            authority_scope_used=list(d.get("authority_scope_used", [])),
            standing_narrowed_by=list(d.get("standing_narrowed_by", [])),
            standing_witness_hash=sha256_obj(standing_material),
        )
        carry_directive = d.get("carry_directive", "CONTINUE_SELF")
        carry_reason_codes = list(d.get("carry_reason_codes", reason_codes))
        next_required_witnesses = list(d.get("next_required_witnesses", []))
        debt_action = d.get("debt_action", "UNCHANGED")
        carry_material = continuation_carry_material(
            continuity_debt_in=list(artifact.continuity_debt_in),
            continuity_debt_out=list(d.get("continuity_debt_out", [])),
            continuation_mode=artifact.continuity_mode,
            inherited_condition=d.get("inherited_condition", "clear"),
            parent_receipt_witness_hash=artifact.parent_receipt_witness_hash,
            parent_branch_id=d.get("parent_branch_id"),
            continuation_result=continuation,
            self_continuation_lawful=bool(d.get("self_continuation_lawful", False)),
            continuation_corridor=escalation_target if outcome == "ESCALATE" else None,
            carry_directive=carry_directive,
            carry_constraints=list(artifact.continuation_constraints),
            carry_reason_codes=carry_reason_codes,
            debt_action=debt_action,
            next_required_witnesses=next_required_witnesses,
        )
        cj = ContinuationJudgment(
            continuation_result=continuation,
            inherited_continuity_condition=d.get("inherited_condition", "clear"),
            continuity_mode=artifact.continuity_mode,
            continuation_intent=artifact.continuation_intent,
            continuation_constraints=list(artifact.continuation_constraints),
            expected_continuation_result=artifact.expected_continuation_result,
            continuity_debt_in=list(artifact.continuity_debt_in),
            continuity_debt_out=list(d.get("continuity_debt_out", [])),
            self_continuation_lawful=bool(d.get("self_continuation_lawful", False)),
            continuation_corridor=escalation_target if outcome == "ESCALATE" else None,
            carry_directive=carry_directive,
            carry_reason_codes=carry_reason_codes,
            debt_action=debt_action,
            next_required_witnesses=next_required_witnesses,
            parent_branch_id=d.get("parent_branch_id"),
            parent_receipt_witness_hash=artifact.parent_receipt_witness_hash,
            parent_continuity_verified=bool(d.get("parent_continuity_verified", False)),
            continuation_witness_hash=sha256_obj({
                "continuity_mode": artifact.continuity_mode,
                "continuation_intent": artifact.continuation_intent,
                "continuation_constraints": list(artifact.continuation_constraints),
                "expected_continuation_result": artifact.expected_continuation_result,
                "continuity_debt_in": list(artifact.continuity_debt_in),
                "continuity_debt_out": list(d.get("continuity_debt_out", [])),
                "parent_receipt_witness_hash": artifact.parent_receipt_witness_hash,
                "parent_branch_id": d.get("parent_branch_id"),
                "continuation_result": continuation,
                "inherited_condition": d.get("inherited_condition", "clear"),
                "carry_directive": carry_directive,
                "debt_action": debt_action,
            }),
            carry_forward_hash=sha256_obj(carry_material),
        )
        judgment_mode = "REFUSE_PRESERVE" if outcome == "REFUSE_BLOCK" else outcome
        outcome_material = outcome_witness_material(
            admissibility_result=admissibility,
            burden_result=burden,
            outcome=outcome,
            judgment_mode=judgment_mode,
            escalation_target=escalation_target,
            reason_codes=list(reason_codes),
            preserved_transition=artifact.requested_transition,
        )
        oj = OutcomeJudgment(
            admissibility_result=admissibility,
            burden_result=burden,
            outcome=outcome,
            judgment_mode=judgment_mode,
            escalation_target=escalation_target,
            reason_codes=list(reason_codes),
            preserved_transition=artifact.requested_transition,
            outcome_witness_hash=sha256_obj(outcome_material),
        )
        preservation_result = "PASS_THROUGH" if outcome == "SAFE_COMMIT" else ("REDIRECT_OPEN" if outcome == "ESCALATE" else "PRESERVE_BLOCK")
        continuation_disposition = "SELF_CONTINUATION_TERMINATED" if continuation == "DENY" else ("ESCALATED_CORRIDOR" if outcome == "ESCALATE" else "CONTINUATION_CLEAR")
        preservation_actions = list(d.get("preservation_actions", []))
        if outcome == "REFUSE_BLOCK":
            preservation_actions = preservation_actions or ["BLOCK_STATE_MUTATION", "PRESERVE_BRANCH_MANIFOLD"]
        elif outcome == "ESCALATE":
            preservation_actions = preservation_actions or ["HOLD_COMMIT", "OPEN_ESCALATION_CORRIDOR"]
        preserved_debt_hash = sha256_obj(list(d.get("continuity_debt_out", [])))
        preservation_material = preservation_witness_material(
            preserved_manifold="commit_boundary_manifold",
            preservation_reason=reason_codes[0] if reason_codes else None,
            preserved_transition=artifact.requested_transition,
            preserved_state_hash=state.state_hash,
            preserved_basis_hash=basis.basis_hash,
            preserved_branch_id=artifact.execution_branch_id,
            refusal_preserves_manifold=(outcome == "REFUSE_BLOCK"),
            prevented_branch_drift=any(code in {"DERIVATIVE_ORDERING_VIOLATION", "EXECUTION_BRANCH_MISMATCH", "SOVEREIGN_CLAIM_FORBIDDEN", "TRANSLATION_ACT_MISMATCH"} for code in reason_codes),
            redirect_open=(outcome == "ESCALATE"),
            self_continuation_terminated=(continuation == "DENY"),
            preservation_result=preservation_result,
            blocked_transition=artifact.requested_transition,
            continuation_disposition=continuation_disposition,
            preservation_reason_codes=list(reason_codes),
            preservation_actions=preservation_actions,
            preserved_continuation_corridor=escalation_target if outcome == "ESCALATE" else None,
            preserved_debt_hash=preserved_debt_hash,
        )
        pr = PreservationRecord(
            preservation_result=preservation_result,
            refusal_preserves_manifold=(outcome == "REFUSE_BLOCK"),
            preserved_manifold="commit_boundary_manifold",
            preserved_transition=artifact.requested_transition,
            blocked_transition=artifact.requested_transition,
            prevented_branch_drift=any(code in {"DERIVATIVE_ORDERING_VIOLATION", "EXECUTION_BRANCH_MISMATCH", "SOVEREIGN_CLAIM_FORBIDDEN", "TRANSLATION_ACT_MISMATCH"} for code in reason_codes),
            redirect_open=(outcome == "ESCALATE"),
            preservation_reason=reason_codes[0] if reason_codes else None,
            preservation_reason_codes=list(reason_codes),
            preservation_actions=preservation_actions,
            continuation_disposition=continuation_disposition,
            preserved_continuation_corridor=escalation_target if outcome == "ESCALATE" else None,
            preserved_state_hash=state.state_hash,
            preserved_debt_hash=preserved_debt_hash,
            self_continuation_terminated=(continuation == "DENY"),
            preserved_basis_hash=basis.basis_hash,
            preserved_branch_id=artifact.execution_branch_id,
            preservation_witness_hash=sha256_obj(preservation_material),
        )
        partial = DecisionReceipt(
            receipt_id=str(uuid4()),
            artifact_id=artifact.artifact_id,
            judgment_context=jc,
            standing_judgment=sj,
            continuation_judgment=cj,
            outcome_judgment=oj,
            preservation_record=pr,
            integrity=ReceiptIntegrity(
                judgment_context=self._seal_receipt_section("judgment_context", jc.to_dict()),
                standing_judgment=self._seal_receipt_section("standing_judgment", sj.to_dict()),
                continuation_judgment=self._seal_receipt_section("continuation_judgment", cj.to_dict()),
                outcome_judgment=self._seal_receipt_section("outcome_judgment", oj.to_dict()),
                preservation_record=self._seal_receipt_section("preservation_record", pr.to_dict()),
                lawful_context_proof="",
                judgment_witness_hash="",
                judgment_act_hash="",
                judgment_against_boundary_hash="",
                continuation_preservation_binding_hash="",
                judgment_cross_binding_hash="",
                receipt_binding_hash="",
                judgment_surface_hash="",
                proof_surface_hash="",
                receipt_hash="",
                receipt_signature="",
            ),
            created_at=utcnow_iso(),
        )
        proof = lawful_context_proof(lawful_context_material(receipt=partial))
        partial = replace(partial, integrity=replace(partial.integrity, lawful_context_proof=proof))
        judgment_witness_hash = sha256_obj(judgment_witness_material(
            judgment_context=partial.judgment_context.to_dict(),
            standing_judgment=partial.standing_judgment.to_dict(),
            continuation_judgment=partial.continuation_judgment.to_dict(),
            outcome_judgment=partial.outcome_judgment.to_dict(),
            preservation_record=partial.preservation_record.to_dict(),
        ))
        partial = replace(partial, integrity=replace(partial.integrity, judgment_witness_hash=judgment_witness_hash))
        judgment_act_hash = sha256_obj(partial.judgment_act_material())
        judgment_against_boundary_hash = sha256_obj(judgment_against_boundary_material(
            artifact_boundary_act_hash=partial.judgment_context.artifact_boundary_act_hash,
            judgment_act_hash=judgment_act_hash,
            outcome_judgment=partial.outcome_judgment.to_dict(),
            continuation_judgment=partial.continuation_judgment.to_dict(),
            preservation_record=partial.preservation_record.to_dict(),
        ))
        continuation_preservation_binding_hash = sha256_obj(continuation_preservation_binding_material(
            artifact_boundary_act_hash=partial.judgment_context.artifact_boundary_act_hash,
            continuation_judgment=partial.continuation_judgment.to_dict(),
            preservation_record=partial.preservation_record.to_dict(),
        ))
        partial = replace(partial, integrity=replace(
            partial.integrity,
            judgment_act_hash=judgment_act_hash,
            judgment_against_boundary_hash=judgment_against_boundary_hash,
            continuation_preservation_binding_hash=continuation_preservation_binding_hash,
        ))
        judgment_cross_binding_hash = sha256_obj({
            "artifact_boundary_claim_hash": partial.judgment_context.artifact_boundary_claim_hash,
            "artifact_boundary_act_hash": partial.judgment_context.artifact_boundary_act_hash,
            "artifact_executable_act_hash": partial.judgment_context.artifact_executable_act_hash,
            "artifact_continuation_act_hash": partial.judgment_context.artifact_continuation_act_hash,
            "artifact_cross_binding_hash": partial.judgment_context.artifact_cross_binding_hash,
            "translation_witness_hash": partial.judgment_context.translation_witness_hash,
            "continuity_witness_hash": partial.judgment_context.continuity_witness_hash,
            "branch_witness_hash": partial.judgment_context.branch_witness_hash,
            "judgment_witness_hash": partial.integrity.judgment_witness_hash,
            "judgment_act_hash": partial.integrity.judgment_act_hash,
            "judgment_against_boundary_hash": partial.integrity.judgment_against_boundary_hash,
            "continuation_preservation_binding_hash": partial.integrity.continuation_preservation_binding_hash,
            "continuation_witness_hash": partial.continuation_judgment.continuation_witness_hash,
            "carry_forward_hash": partial.continuation_judgment.carry_forward_hash,
            "preservation_witness_hash": partial.preservation_record.preservation_witness_hash,
            "lawful_context_proof": partial.integrity.lawful_context_proof,
        })
        partial = replace(partial, integrity=replace(partial.integrity, judgment_cross_binding_hash=judgment_cross_binding_hash))
        judgment_surface_hash = sha256_obj(partial.integrity.judgment_surface())
        partial = replace(partial, integrity=replace(partial.integrity, judgment_surface_hash=judgment_surface_hash))
        binding_hash = sha256_obj(partial.binding_material())
        partial = replace(partial, integrity=replace(partial.integrity, receipt_binding_hash=binding_hash))
        proof_surface_hash = sha256_obj(partial.integrity.proof_surface())
        partial = replace(partial, integrity=replace(partial.integrity, proof_surface_hash=proof_surface_hash))
        data = partial.to_dict()
        data["proof"] = dict(data["proof"])
        data["proof"]["receipt_hash"] = ""
        data["proof"]["receipt_signature"] = ""
        receipt_hash = sha256_obj(data)
        data["proof"]["receipt_hash"] = receipt_hash
        signature = sign_material(self.receipt_secret, data)
        return replace(partial, integrity=replace(partial.integrity, receipt_hash=receipt_hash, receipt_signature=signature))

    def _write_evaluation_record(self, artifact: ExecutionArtifact, basis: GoverningBasis, state_hash: str, receipt: DecisionReceipt) -> None:
        self.store.append("evaluations", {
            "artifact_id": artifact.artifact_id,
            "basis_id": basis.basis_id,
            "basis_version": basis.version,
            "state_hash": state_hash,
            "artifact_bridge_hash": artifact.integrity.bridge_hash,
            "artifact_witness_hash": artifact.integrity.witness_hash,
            "artifact_boundary_act_hash": artifact.integrity.boundary_act_hash,
            "receipt_id": receipt.receipt_id,
            "judgment_act_hash": receipt.integrity.judgment_act_hash,
            "judgment_against_boundary_hash": receipt.integrity.judgment_against_boundary_hash,
            "continuation_preservation_binding_hash": receipt.integrity.continuation_preservation_binding_hash,
            "receipt_hash": receipt.integrity.receipt_hash,
            "outcome": receipt.outcome,
            "judgment_mode": receipt.outcome_judgment.judgment_mode,
            "reason_codes": receipt.reason_codes,
            "recorded_at": utcnow_iso(),
        }, unique_key=f"evaluation:{artifact.artifact_id}:{state_hash}:{receipt.integrity.receipt_hash}")

    def _record_preservation_refusal(self, receipt: DecisionReceipt, state_ref: str, state_hash: str) -> None:
        self.store.append("preservations", {
            "receipt_id": receipt.receipt_id,
            "state_ref": state_ref,
            "state_hash": state_hash,
            "judgment_mode": receipt.outcome_judgment.judgment_mode,
            "preserved_manifold": receipt.preservation_record.preserved_manifold,
            "continuation_preservation_binding_hash": receipt.integrity.continuation_preservation_binding_hash,
            "judgment_against_boundary_hash": receipt.integrity.judgment_against_boundary_hash,
            "recorded_at": utcnow_iso(),
        }, unique_key=f"preservation:{receipt.receipt_id}")

    def _record_escalation(self, receipt: DecisionReceipt, artifact: ExecutionArtifact, basis: GoverningBasis) -> None:
        self.store.append("escalations", {
            "receipt_id": receipt.receipt_id,
            "artifact_id": artifact.artifact_id,
            "transition": artifact.requested_transition,
            "resolved_target": receipt.escalation_target,
            "policy_target": basis.rules.get("escalation_corridors", {}).get(artifact.requested_transition),
            "recorded_at": utcnow_iso(),
        }, unique_key=f"escalation:{receipt.receipt_id}")
