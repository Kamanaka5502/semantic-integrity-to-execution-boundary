
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .util import sha256_obj

ARTIFACT_CONTRACT_VERSION = "sam.v13"
ARTIFACT_KIND = "execution_bridge_act"
RECEIPT_CONTRACT_VERSION = "sam.v13"
RECEIPT_KIND = "continuation_judgment_receipt"

def utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def translation_witness_material(*, payload: Dict[str, Any], intent: Dict[str, Any], translation: Dict[str, Any], law: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "payload_hash": sha256_obj(payload),
        "requested_transition": intent["requested_transition"],
        "actor_id": intent["actor_id"],
        "authority_scope": sorted(intent["authority_scope"]),
        "source_intent": translation["source_intent"],
        "executable_claim": translation["executable_claim"],
        "translation_constraints": list(translation["translation_constraints"]),
        "translation_outcome": translation["translation_outcome"],
        "translation_narrowing": list(translation["translation_narrowing"]),
        "preserved_claims": list(translation["preserved_claims"]),
        "steward_lane": translation["steward_lane"],
        "visible_surface": translation["visible_surface"],
        "governing_basis_hash": law["governing_basis_hash"],
        "logic_version": law["logic_version"],
    }

def continuity_witness_material(*, continuity: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "state_ref": continuity["state_ref"],
        "declared_state_hash": continuity["declared_state_hash"],
        "declared_entity_id": continuity["declared_entity_id"],
        "declared_current_status": continuity["declared_current_status"],
        "declared_open_burden_codes": sorted(continuity["declared_open_burden_codes"]),
        "parent_receipt_id": continuity["parent_receipt_id"],
        "parent_receipt_signature": continuity["parent_receipt_signature"],
        "parent_receipt_witness_hash": continuity["parent_receipt_witness_hash"],
        "continuity_chain_head": continuity["continuity_chain_head"],
        "continuity_mode": continuity["continuity_mode"],
        "continuation_intent": continuity["continuation_intent"],
        "continuation_constraints": list(continuity["continuation_constraints"]),
        "expected_continuation_result": continuity["expected_continuation_result"],
        "continuity_debt_in": list(continuity["continuity_debt_in"]),
        "inherited_burden_codes": sorted(continuity["inherited_burden_codes"]),
    }

def branch_witness_material(*, branch: Dict[str, Any], translation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "execution_branch_id": branch["execution_branch_id"],
        "branch_derivation": branch["branch_derivation"],
        "branch_role": branch["branch_role"],
        "claims_sovereign_authority": branch["claims_sovereign_authority"],
        "declared_escalation_target": branch["declared_escalation_target"],
        "surface_steward": branch["surface_steward"],
        "steward_lane": translation["steward_lane"],
        "visible_surface": translation["visible_surface"],
    }


def boundary_claim_material(*, payload: Dict[str, Any], intent: Dict[str, Any], translation: Dict[str, Any], continuity: Dict[str, Any], branch: Dict[str, Any], law: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "payload_hash": sha256_obj(payload),
        "requested_transition": intent["requested_transition"],
        "actor_id": intent["actor_id"],
        "authority_scope": sorted(intent["authority_scope"]),
        "schema_id": intent["schema_id"],
        "schema_version": intent["schema_version"],
        "source_intent": translation["source_intent"],
        "executable_claim": translation["executable_claim"],
        "translation_outcome": translation["translation_outcome"],
        "translation_constraints": list(translation["translation_constraints"]),
        "translation_narrowing": list(translation["translation_narrowing"]),
        "preserved_claims": list(translation["preserved_claims"]),
        "state_ref": continuity["state_ref"],
        "declared_state_hash": continuity["declared_state_hash"],
        "declared_current_status": continuity["declared_current_status"],
        "continuity_mode": continuity["continuity_mode"],
        "continuity_debt_in": list(continuity["continuity_debt_in"]),
        "parent_receipt_id": continuity["parent_receipt_id"],
        "parent_receipt_witness_hash": continuity["parent_receipt_witness_hash"],
        "execution_branch_id": branch["execution_branch_id"],
        "branch_derivation": branch["branch_derivation"],
        "branch_role": branch["branch_role"],
        "surface_steward": branch["surface_steward"],
        "governing_basis_id": law["governing_basis_id"],
        "governing_basis_hash": law["governing_basis_hash"],
        "logic_version": law["logic_version"],
    }

def executable_act_material(*, intent: Dict[str, Any], translation: Dict[str, Any], continuity: Dict[str, Any], branch: Dict[str, Any], law: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "requested_transition": intent["requested_transition"],
        "actor_id": intent["actor_id"],
        "authority_scope": sorted(intent["authority_scope"]),
        "schema_id": intent["schema_id"],
        "schema_version": intent["schema_version"],
        "source_intent": translation["source_intent"],
        "executable_claim": translation["executable_claim"],
        "translation_outcome": translation["translation_outcome"],
        "translation_constraints": list(translation["translation_constraints"]),
        "translation_narrowing": list(translation["translation_narrowing"]),
        "preserved_claims": list(translation["preserved_claims"]),
        "state_ref": continuity["state_ref"],
        "declared_state_hash": continuity["declared_state_hash"],
        "declared_current_status": continuity["declared_current_status"],
        "execution_branch_id": branch["execution_branch_id"],
        "branch_role": branch["branch_role"],
        "surface_steward": branch["surface_steward"],
        "governing_basis_id": law["governing_basis_id"],
        "governing_basis_hash": law["governing_basis_hash"],
        "logic_version": law["logic_version"],
    }

def continuation_act_material(*, continuity: Dict[str, Any], branch: Dict[str, Any], law: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "state_ref": continuity["state_ref"],
        "declared_state_hash": continuity["declared_state_hash"],
        "declared_entity_id": continuity["declared_entity_id"],
        "declared_current_status": continuity["declared_current_status"],
        "declared_open_burden_codes": sorted(continuity["declared_open_burden_codes"]),
        "parent_receipt_id": continuity["parent_receipt_id"],
        "parent_receipt_witness_hash": continuity["parent_receipt_witness_hash"],
        "continuity_chain_head": continuity["continuity_chain_head"],
        "continuity_mode": continuity["continuity_mode"],
        "continuity_debt_in": list(continuity["continuity_debt_in"]),
        "inherited_burden_codes": sorted(continuity["inherited_burden_codes"]),
        "execution_branch_id": branch["execution_branch_id"],
        "branch_derivation": branch["branch_derivation"],
        "branch_role": branch["branch_role"],
        "governing_basis_id": law["governing_basis_id"],
        "governing_basis_hash": law["governing_basis_hash"],
        "logic_version": law["logic_version"],
    }


def continuation_carry_material(*, continuity_debt_in: List[Dict[str, Any]], continuity_debt_out: List[Dict[str, Any]], continuation_mode: str, inherited_condition: str, parent_receipt_witness_hash: Optional[str], parent_branch_id: Optional[str], continuation_result: str, self_continuation_lawful: bool, continuation_corridor: Optional[str], carry_directive: str, carry_constraints: List[str], carry_reason_codes: List[str], debt_action: str, next_required_witnesses: List[str]) -> Dict[str, Any]:
    return {
        "continuity_debt_in": list(continuity_debt_in),
        "continuity_debt_out": list(continuity_debt_out),
        "continuation_mode": continuation_mode,
        "inherited_condition": inherited_condition,
        "parent_receipt_witness_hash": parent_receipt_witness_hash,
        "parent_branch_id": parent_branch_id,
        "continuation_result": continuation_result,
        "self_continuation_lawful": self_continuation_lawful,
        "continuation_corridor": continuation_corridor,
        "carry_directive": carry_directive,
        "carry_constraints": list(carry_constraints),
        "carry_reason_codes": list(carry_reason_codes),
        "debt_action": debt_action,
        "next_required_witnesses": list(next_required_witnesses),
    }


def standing_witness_material(*, standing_before: str, standing_after: str, standing_result: str, standing_change_reason: Optional[str], authority_scope_used: List[str], standing_narrowed_by: List[str]) -> Dict[str, Any]:
    return {
        "standing_before": standing_before,
        "standing_after": standing_after,
        "standing_result": standing_result,
        "standing_change_reason": standing_change_reason,
        "authority_scope_used": sorted(authority_scope_used),
        "standing_narrowed_by": list(standing_narrowed_by),
    }

def outcome_witness_material(*, admissibility_result: str, burden_result: str, outcome: str, judgment_mode: str, escalation_target: Optional[str], reason_codes: List[str], preserved_transition: str) -> Dict[str, Any]:
    return {
        "admissibility_result": admissibility_result,
        "burden_result": burden_result,
        "outcome": outcome,
        "judgment_mode": judgment_mode,
        "escalation_target": escalation_target,
        "reason_codes": list(reason_codes),
        "preserved_transition": preserved_transition,
    }

def preservation_witness_material(*, preserved_manifold: str, preservation_reason: Optional[str], preserved_transition: str, preserved_state_hash: str, preserved_basis_hash: str, preserved_branch_id: str, refusal_preserves_manifold: bool, prevented_branch_drift: bool, redirect_open: bool, self_continuation_terminated: bool, preservation_result: str, blocked_transition: str, continuation_disposition: str, preservation_reason_codes: List[str], preservation_actions: List[str], preserved_continuation_corridor: Optional[str], preserved_debt_hash: str) -> Dict[str, Any]:
    return {
        "preserved_manifold": preserved_manifold,
        "preservation_reason": preservation_reason,
        "preserved_transition": preserved_transition,
        "preserved_state_hash": preserved_state_hash,
        "preserved_basis_hash": preserved_basis_hash,
        "preserved_branch_id": preserved_branch_id,
        "refusal_preserves_manifold": refusal_preserves_manifold,
        "prevented_branch_drift": prevented_branch_drift,
        "redirect_open": redirect_open,
        "self_continuation_terminated": self_continuation_terminated,
        "preservation_result": preservation_result,
        "blocked_transition": blocked_transition,
        "continuation_disposition": continuation_disposition,
        "preservation_reason_codes": list(preservation_reason_codes),
        "preservation_actions": list(preservation_actions),
        "preserved_continuation_corridor": preserved_continuation_corridor,
        "preserved_debt_hash": preserved_debt_hash,
    }


def boundary_act_material(*, payload: Dict[str, Any], intent: Dict[str, Any], translation: Dict[str, Any], continuity: Dict[str, Any], branch: Dict[str, Any], law: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "payload_hash": sha256_obj(payload),
        "requested_transition": intent["requested_transition"],
        "actor_id": intent["actor_id"],
        "authority_scope": sorted(intent["authority_scope"]),
        "schema_id": intent["schema_id"],
        "schema_version": intent["schema_version"],
        "constraint_bundle_hash": intent["constraint_bundle_hash"],
        "source_intent": translation["source_intent"],
        "executable_claim": translation["executable_claim"],
        "translation_outcome": translation["translation_outcome"],
        "translation_constraints": list(translation["translation_constraints"]),
        "translation_narrowing": list(translation["translation_narrowing"]),
        "preserved_claims": list(translation["preserved_claims"]),
        "continuity_mode": continuity["continuity_mode"],
        "continuation_intent": continuity["continuation_intent"],
        "continuation_constraints": list(continuity["continuation_constraints"]),
        "expected_continuation_result": continuity["expected_continuation_result"],
        "continuity_debt_in": list(continuity["continuity_debt_in"]),
        "parent_receipt_id": continuity["parent_receipt_id"],
        "parent_receipt_witness_hash": continuity["parent_receipt_witness_hash"],
        "execution_branch_id": branch["execution_branch_id"],
        "branch_derivation": branch["branch_derivation"],
        "branch_role": branch["branch_role"],
        "declared_escalation_target": branch["declared_escalation_target"],
        "governing_basis_id": law["governing_basis_id"],
        "governing_basis_hash": law["governing_basis_hash"],
        "logic_version": law["logic_version"],
        "boundary_claim_hash": sha256_obj(boundary_claim_material(payload=payload, intent=intent, translation=translation, continuity=continuity, branch=branch, law=law)),
        "executable_act_hash": sha256_obj(executable_act_material(intent=intent, translation=translation, continuity=continuity, branch=branch, law=law)),
        "continuation_act_hash": sha256_obj(continuation_act_material(continuity=continuity, branch=branch, law=law)),
    }


def judgment_act_material(*, judgment_context: Dict[str, Any], continuation_judgment: Dict[str, Any], outcome_judgment: Dict[str, Any], preservation_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_boundary_act_hash": judgment_context["artifact_boundary_act_hash"],
        "artifact_boundary_claim_hash": judgment_context["artifact_boundary_claim_hash"],
        "artifact_continuation_act_hash": judgment_context["artifact_continuation_act_hash"],
        "continuation_result": continuation_judgment["continuation_result"],
        "continuation_intent": continuation_judgment["continuation_intent"],
        "expected_continuation_result": continuation_judgment["expected_continuation_result"],
        "carry_directive": continuation_judgment["carry_directive"],
        "carry_reason_codes": list(continuation_judgment["carry_reason_codes"]),
        "debt_action": continuation_judgment["debt_action"],
        "continuation_witness_hash": continuation_judgment["continuation_witness_hash"],
        "carry_forward_hash": continuation_judgment["carry_forward_hash"],
        "outcome": outcome_judgment["outcome"],
        "judgment_mode": "REFUSE_PRESERVE" if outcome_judgment["outcome"] == "REFUSE_BLOCK" else outcome_judgment["outcome"],
        "preservation_result": preservation_record["preservation_result"],
        "blocked_transition": preservation_record["blocked_transition"],
        "preserved_transition": preservation_record["preserved_transition"],
        "continuation_disposition": preservation_record["continuation_disposition"],
        "preserved_continuation_corridor": preservation_record["preserved_continuation_corridor"],
        "preservation_witness_hash": preservation_record["preservation_witness_hash"],
    }

@dataclass(frozen=True)
class ArtifactIntentSurface:
    workflow_id: str
    workflow_step: str
    requested_transition: str
    actor_id: str
    authority_scope: List[str]
    schema_id: str
    schema_version: str
    constraint_bundle_hash: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ArtifactTranslationRecord:
    source_intent: str
    executable_claim: str
    translation_constraints: List[str]
    translation_outcome: str
    steward_lane: str
    visible_surface: str
    translation_digest: str
    translation_narrowing: List[str]
    preserved_claims: List[str]
    translation_witness_hash: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ArtifactLawBinding:
    contract_version: str
    artifact_kind: str
    governing_basis_id: str
    governing_basis_version: str
    governing_basis_hash: str
    basis_lineage_hash: str
    basis_signature: str
    logic_version: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ArtifactContinuityEntry:
    state_ref: str
    declared_state_hash: str
    declared_entity_id: str
    declared_current_status: str
    declared_open_burden_codes: List[str]
    parent_receipt_id: Optional[str]
    parent_receipt_signature: Optional[str]
    parent_receipt_witness_hash: Optional[str]
    continuity_chain_head: Optional[str]
    continuity_mode: str
    continuation_intent: str
    continuation_constraints: List[str]
    expected_continuation_result: str
    continuity_debt_in: List[Dict[str, Any]]
    inherited_burden_codes: List[str]
    continuity_witness_hash: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ArtifactBranchPosture:
    execution_branch_id: str
    branch_derivation: str
    branch_role: str
    claims_sovereign_authority: bool
    declared_escalation_target: Optional[str]
    surface_steward: str
    branch_witness_hash: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ArtifactSectionIntegrity:
    section: str
    section_hash: str
    section_signature: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ArtifactIntegrity:
    payload_hash: str
    intent: ArtifactSectionIntegrity
    translation: ArtifactSectionIntegrity
    law: ArtifactSectionIntegrity
    continuity: ArtifactSectionIntegrity
    branch: ArtifactSectionIntegrity
    bridge_hash: str
    witness_hash: str
    executable_act_hash: str
    continuation_act_hash: str
    boundary_act_hash: str
    cross_binding_hash: str
    boundary_claim_hash: str
    claim_surface_hash: str
    proof_surface_hash: str
    artifact_signature: Optional[str] = None
    def claim_surface(self) -> Dict[str, Any]:
        return {
            "executable_act_hash": self.executable_act_hash,
            "continuation_act_hash": self.continuation_act_hash,
            "boundary_act_hash": self.boundary_act_hash,
            "boundary_claim_hash": self.boundary_claim_hash,
            "cross_binding_hash": self.cross_binding_hash,
        }
    def proof_surface(self) -> Dict[str, Any]:
        return {
            "payload_hash": self.payload_hash,
            "intent_section_hash": self.intent.section_hash,
            "translation_section_hash": self.translation.section_hash,
            "law_section_hash": self.law.section_hash,
            "continuity_section_hash": self.continuity.section_hash,
            "branch_section_hash": self.branch.section_hash,
            "bridge_hash": self.bridge_hash,
            "witness_hash": self.witness_hash,
            "artifact_signature": self.artifact_signature,
        }
    def to_dict(self) -> Dict[str, Any]:
        return {
            "payload_hash": self.payload_hash,
            "intent": self.intent.to_dict(),
            "translation": self.translation.to_dict(),
            "law": self.law.to_dict(),
            "continuity": self.continuity.to_dict(),
            "branch": self.branch.to_dict(),
            "bridge_hash": self.bridge_hash,
            "witness_hash": self.witness_hash,
            "executable_act_hash": self.executable_act_hash,
            "continuation_act_hash": self.continuation_act_hash,
            "boundary_act_hash": self.boundary_act_hash,
            "cross_binding_hash": self.cross_binding_hash,
            "boundary_claim_hash": self.boundary_claim_hash,
            "claim_surface_hash": self.claim_surface_hash,
            "proof_surface_hash": self.proof_surface_hash,
            "artifact_signature": self.artifact_signature,
        }


@dataclass(frozen=True)
class ArtifactClaim:
    intent_surface: ArtifactIntentSurface
    translation_record: ArtifactTranslationRecord
    law_binding: ArtifactLawBinding
    continuity_entry: ArtifactContinuityEntry
    branch_posture: ArtifactBranchPosture

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_surface": self.intent_surface.to_dict(),
            "translation_record": self.translation_record.to_dict(),
            "law_binding": self.law_binding.to_dict(),
            "continuity_entry": self.continuity_entry.to_dict(),
            "branch_posture": self.branch_posture.to_dict(),
        }

@dataclass(frozen=True)
class ArtifactProof:
    integrity: ArtifactIntegrity

    def to_dict(self) -> Dict[str, Any]:
        return self.integrity.to_dict()

@dataclass(frozen=True)
class ExecutionArtifact:
    artifact_id: str
    payload: Dict[str, Any]
    intent_surface: ArtifactIntentSurface
    translation_record: ArtifactTranslationRecord
    law_binding: ArtifactLawBinding
    continuity_entry: ArtifactContinuityEntry
    branch_posture: ArtifactBranchPosture
    integrity: ArtifactIntegrity
    timestamp: str

    def __post_init__(self) -> None:
        nested = [
            ("intent_surface", ArtifactIntentSurface),
            ("translation_record", ArtifactTranslationRecord),
            ("law_binding", ArtifactLawBinding),
            ("continuity_entry", ArtifactContinuityEntry),
            ("branch_posture", ArtifactBranchPosture),
        ]
        for name, cls in nested:
            value = getattr(self, name)
            if isinstance(value, dict):
                if name == "outcome_judgment" and "judgment_mode" not in value:
                    value = {**value, "judgment_mode": ("REFUSE_PRESERVE" if value.get("outcome") == "REFUSE_BLOCK" else value.get("outcome"))}
                object.__setattr__(self, name, cls(**value))
        if isinstance(self.integrity, dict):
            i = self.integrity
            object.__setattr__(self, "integrity", ArtifactIntegrity(
                payload_hash=i["payload_hash"],
                intent=ArtifactSectionIntegrity(**i["intent"]),
                translation=ArtifactSectionIntegrity(**i["translation"]),
                law=ArtifactSectionIntegrity(**i["law"]),
                continuity=ArtifactSectionIntegrity(**i["continuity"]),
                branch=ArtifactSectionIntegrity(**i["branch"]),
                bridge_hash=i["bridge_hash"],
                witness_hash=i["witness_hash"],
                executable_act_hash=i["executable_act_hash"],
                continuation_act_hash=i["continuation_act_hash"],
                boundary_act_hash=i.get("boundary_act_hash", ""),
                cross_binding_hash=i["cross_binding_hash"],
                boundary_claim_hash=i["boundary_claim_hash"],
                claim_surface_hash=i.get("claim_surface_hash",""),
                proof_surface_hash=i.get("proof_surface_hash",""),
                artifact_signature=i.get("artifact_signature"),
            ))


    @property
    def claim(self) -> ArtifactClaim:
        return ArtifactClaim(
            intent_surface=self.intent_surface,
            translation_record=self.translation_record,
            law_binding=self.law_binding,
            continuity_entry=self.continuity_entry,
            branch_posture=self.branch_posture,
        )

    @property
    def proof(self) -> ArtifactProof:
        return ArtifactProof(integrity=self.integrity)

    def bridge_material(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "timestamp": self.timestamp,
            "payload_hash": sha256_obj(self.payload),
            "intent_hash": sha256_obj(self.intent_surface.to_dict()),
            "translation_hash": sha256_obj(self.translation_record.to_dict()),
            "law_hash": sha256_obj(self.law_binding.to_dict()),
            "continuity_hash": sha256_obj(self.continuity_entry.to_dict()),
            "branch_hash": sha256_obj(self.branch_posture.to_dict()),
        }

    def witness_material(self) -> Dict[str, Any]:
        return {
            "bridge_hash": sha256_obj(self.bridge_material()),
            "translation_witness_hash": self.translation_record.translation_witness_hash,
            "continuity_witness_hash": self.continuity_entry.continuity_witness_hash,
            "branch_witness_hash": self.branch_posture.branch_witness_hash,
            "declared_state_hash": self.continuity_entry.declared_state_hash,
            "parent_receipt_id": self.continuity_entry.parent_receipt_id,
            "parent_receipt_signature": self.continuity_entry.parent_receipt_signature,
            "parent_receipt_witness_hash": self.continuity_entry.parent_receipt_witness_hash,
            "governing_basis_hash": self.law_binding.governing_basis_hash,
            "basis_signature": self.law_binding.basis_signature,
        }

    def boundary_claim_material(self) -> Dict[str, Any]:
        return boundary_claim_material(
            payload=self.payload,
            intent=self.intent_surface.to_dict(),
            translation={k: v for k, v in self.translation_record.to_dict().items() if k != "translation_witness_hash"},
            continuity={k: v for k, v in self.continuity_entry.to_dict().items() if k != "continuity_witness_hash"},
            branch={k: v for k, v in self.branch_posture.to_dict().items() if k != "branch_witness_hash"},
            law=self.law_binding.to_dict(),
        )

    def executable_act_material(self) -> Dict[str, Any]:
        return executable_act_material(
            intent=self.intent_surface.to_dict(),
            translation=self.translation_record.to_dict(),
            continuity=self.continuity_entry.to_dict(),
            branch=self.branch_posture.to_dict(),
            law=self.law_binding.to_dict(),
        )

    def continuation_act_material(self) -> Dict[str, Any]:
        return continuation_act_material(
            continuity=self.continuity_entry.to_dict(),
            branch=self.branch_posture.to_dict(),
            law=self.law_binding.to_dict(),
        )

    def boundary_act_material(self) -> Dict[str, Any]:
        return boundary_act_material(
            payload=self.payload,
            intent=self.intent_surface.to_dict(),
            translation=self.translation_record.to_dict(),
            continuity=self.continuity_entry.to_dict(),
            branch=self.branch_posture.to_dict(),
            law=self.law_binding.to_dict(),
        )

    def cross_binding_material(self) -> Dict[str, Any]:
        return {
            "contract_version": self.law_binding.contract_version,
            "artifact_kind": self.law_binding.artifact_kind,
            "payload_hash": self.integrity.payload_hash,
            "intent_section_hash": self.integrity.intent.section_hash,
            "translation_section_hash": self.integrity.translation.section_hash,
            "law_section_hash": self.integrity.law.section_hash,
            "continuity_section_hash": self.integrity.continuity.section_hash,
            "branch_section_hash": self.integrity.branch.section_hash,
            "bridge_hash": self.integrity.bridge_hash,
            "witness_hash": self.integrity.witness_hash,
            "executable_act_hash": self.integrity.executable_act_hash,
            "continuation_act_hash": self.integrity.continuation_act_hash,
            "translation_witness_hash": self.translation_record.translation_witness_hash,
            "continuity_witness_hash": self.continuity_entry.continuity_witness_hash,
            "branch_witness_hash": self.branch_posture.branch_witness_hash,
        }

    def claim_surface_material(self) -> Dict[str, Any]:
        return self.integrity.claim_surface()

    def proof_surface_material(self) -> Dict[str, Any]:
        return {
            "payload_hash": self.integrity.payload_hash,
            "intent_section_hash": self.integrity.intent.section_hash,
            "translation_section_hash": self.integrity.translation.section_hash,
            "law_section_hash": self.integrity.law.section_hash,
            "continuity_section_hash": self.integrity.continuity.section_hash,
            "branch_section_hash": self.integrity.branch.section_hash,
            "bridge_hash": self.integrity.bridge_hash,
            "witness_hash": self.integrity.witness_hash,
            "claim_surface_hash": self.integrity.claim_surface_hash,
        }

    @property
    def artifact_signature(self) -> Optional[str]: return self.integrity.artifact_signature
    @property
    def payload_hash(self) -> str: return self.integrity.payload_hash
    @property
    def requested_transition(self) -> str: return self.intent_surface.requested_transition
    @property
    def actor_id(self) -> str: return self.intent_surface.actor_id
    @property
    def authority_scope(self) -> List[str]: return self.intent_surface.authority_scope
    @property
    def workflow_id(self) -> str: return self.intent_surface.workflow_id
    @property
    def workflow_step(self) -> str: return self.intent_surface.workflow_step
    @property
    def schema_id(self) -> str: return self.intent_surface.schema_id
    @property
    def schema_version(self) -> str: return self.intent_surface.schema_version
    @property
    def constraint_bundle_hash(self) -> str: return self.intent_surface.constraint_bundle_hash
    @property
    def source_intent(self) -> str: return self.translation_record.source_intent
    @property
    def executable_claim(self) -> str: return self.translation_record.executable_claim
    @property
    def translation_digest(self) -> str: return self.translation_record.translation_digest
    @property
    def translation_constraints(self) -> List[str]: return self.translation_record.translation_constraints
    @property
    def translation_outcome(self) -> str: return self.translation_record.translation_outcome
    @property
    def steward_lane(self) -> str: return self.translation_record.steward_lane
    @property
    def visible_surface(self) -> str: return self.translation_record.visible_surface
    @property
    def translation_narrowing(self) -> List[str]: return self.translation_record.translation_narrowing
    @property
    def preserved_claims(self) -> List[str]: return self.translation_record.preserved_claims
    @property
    def translation_witness_hash(self) -> str: return self.translation_record.translation_witness_hash
    @property
    def governing_basis_id(self) -> str: return self.law_binding.governing_basis_id
    @property
    def governing_basis_version(self) -> str: return self.law_binding.governing_basis_version
    @property
    def governing_basis_hash(self) -> str: return self.law_binding.governing_basis_hash
    @property
    def basis_lineage_hash(self) -> str: return self.law_binding.basis_lineage_hash
    @property
    def basis_signature(self) -> str: return self.law_binding.basis_signature
    @property
    def logic_version(self) -> str: return self.law_binding.logic_version
    @property
    def state_ref(self) -> str: return self.continuity_entry.state_ref
    @property
    def declared_state_hash(self) -> str: return self.continuity_entry.declared_state_hash
    @property
    def parent_receipt_id(self) -> Optional[str]: return self.continuity_entry.parent_receipt_id
    @property
    def parent_receipt_signature(self) -> Optional[str]: return self.continuity_entry.parent_receipt_signature
    @property
    def parent_receipt_witness_hash(self) -> Optional[str]: return self.continuity_entry.parent_receipt_witness_hash
    @property
    def continuity_chain_head(self) -> Optional[str]: return self.continuity_entry.continuity_chain_head
    @property
    def continuity_mode(self) -> str: return self.continuity_entry.continuity_mode
    @property
    def continuation_intent(self) -> str: return self.continuity_entry.continuation_intent
    @property
    def continuation_constraints(self) -> List[str]: return self.continuity_entry.continuation_constraints
    @property
    def expected_continuation_result(self) -> str: return self.continuity_entry.expected_continuation_result
    @property
    def continuity_debt_in(self) -> List[Dict[str, Any]]: return self.continuity_entry.continuity_debt_in
    @property
    def inherited_burden_codes(self) -> List[str]: return self.continuity_entry.inherited_burden_codes
    @property
    def continuity_witness_hash(self) -> str: return self.continuity_entry.continuity_witness_hash
    @property
    def execution_branch_id(self) -> str: return self.branch_posture.execution_branch_id
    @property
    def branch_derivation(self) -> str: return self.branch_posture.branch_derivation
    @property
    def branch_role(self) -> str: return self.branch_posture.branch_role
    @property
    def claims_sovereign_authority(self) -> bool: return self.branch_posture.claims_sovereign_authority
    @property
    def declared_escalation_target(self) -> Optional[str]: return self.branch_posture.declared_escalation_target
    @property
    def surface_steward(self) -> str: return self.branch_posture.surface_steward
    @property
    def branch_witness_hash(self) -> str: return self.branch_posture.branch_witness_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "payload": self.payload,
            "claim": {
                "intent_surface": self.intent_surface.to_dict(),
                "translation_record": self.translation_record.to_dict(),
                "law_binding": self.law_binding.to_dict(),
                "continuity_entry": self.continuity_entry.to_dict(),
                "branch_posture": self.branch_posture.to_dict(),
            },
            "proof": self.integrity.to_dict(),
            "timestamp": self.timestamp,
        }

    def signable_dict(self) -> Dict[str, Any]:
        data = self.to_dict()
        data["proof"] = dict(data["proof"])
        data["proof"]["artifact_signature"] = None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionArtifact":
        if "claim" not in data or "proof" not in data:
            raise ValueError("execution artifact must use explicit claim/proof surfaces")
        claim = data["claim"]
        normalized = {
            "artifact_id": data["artifact_id"],
            "payload": data["payload"],
            "intent_surface": claim["intent_surface"],
            "translation_record": claim["translation_record"],
            "law_binding": claim["law_binding"],
            "continuity_entry": claim["continuity_entry"],
            "branch_posture": claim["branch_posture"],
            "integrity": data["proof"],
            "timestamp": data["timestamp"],
        }
        return cls(**normalized)

@dataclass(frozen=True)
class JudgmentContext:
    contract_version: str
    receipt_kind: str
    governing_basis_id: str
    governing_basis_version: str
    governing_basis_hash: str
    governing_basis_lineage_hash: str
    logic_version: str
    state_ref: str
    state_hash: str
    state_entity_id: str
    state_current_status: str
    state_open_burden_codes: List[str]
    artifact_id: str
    artifact_payload_hash: str
    artifact_bridge_hash: str
    artifact_witness_hash: str
    artifact_executable_act_hash: str
    artifact_continuation_act_hash: str
    artifact_cross_binding_hash: str
    artifact_boundary_claim_hash: str
    artifact_boundary_act_hash: str
    artifact_signature: str
    translation_witness_hash: str
    continuity_witness_hash: str
    branch_witness_hash: str
    execution_branch_id: str
    branch_role: str
    branch_derivation: str
    source_intent: str
    executable_claim: str
    translation_digest: str
    translation_outcome: str
    continuity_mode: str
    parent_receipt_id: Optional[str]
    parent_receipt_witness_hash: Optional[str]
    continuity_chain_head: Optional[str]
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class StandingJudgment:
    standing_before: str
    standing_after: str
    standing_result: str
    standing_change_reason: Optional[str]
    authority_scope_used: List[str]
    standing_narrowed_by: List[str]
    standing_witness_hash: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ContinuationJudgment:
    continuation_result: str
    inherited_continuity_condition: str
    continuity_mode: str
    continuation_intent: str
    continuation_constraints: List[str]
    expected_continuation_result: str
    continuity_debt_in: List[Dict[str, Any]]
    continuity_debt_out: List[Dict[str, Any]]
    self_continuation_lawful: bool
    continuation_corridor: Optional[str]
    carry_directive: str
    carry_reason_codes: List[str]
    debt_action: str
    next_required_witnesses: List[str]
    parent_branch_id: Optional[str]
    parent_receipt_witness_hash: Optional[str]
    parent_continuity_verified: bool
    continuation_witness_hash: str
    carry_forward_hash: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class OutcomeJudgment:
    admissibility_result: str
    burden_result: str
    outcome: str
    judgment_mode: str
    escalation_target: Optional[str]
    reason_codes: List[str]
    preserved_transition: str
    outcome_witness_hash: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class PreservationRecord:
    preservation_result: str
    refusal_preserves_manifold: bool
    preserved_manifold: str
    preserved_transition: str
    blocked_transition: str
    prevented_branch_drift: bool
    redirect_open: bool
    preservation_reason: Optional[str]
    preservation_reason_codes: List[str]
    preservation_actions: List[str]
    continuation_disposition: str
    preserved_continuation_corridor: Optional[str]
    preserved_state_hash: str
    preserved_debt_hash: str
    self_continuation_terminated: bool
    preserved_basis_hash: str
    preserved_branch_id: str
    preservation_witness_hash: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

def continuation_preservation_binding_material(*, artifact_boundary_act_hash: str, continuation_judgment: Dict[str, Any], preservation_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_boundary_act_hash": artifact_boundary_act_hash,
        "continuation_result": continuation_judgment["continuation_result"],
        "continuation_intent": continuation_judgment["continuation_intent"],
        "continuation_constraints": list(continuation_judgment["continuation_constraints"]),
        "expected_continuation_result": continuation_judgment["expected_continuation_result"],
        "continuation_corridor": continuation_judgment["continuation_corridor"],
        "carry_directive": continuation_judgment["carry_directive"],
        "carry_reason_codes": list(continuation_judgment["carry_reason_codes"]),
        "debt_action": continuation_judgment["debt_action"],
        "next_required_witnesses": list(continuation_judgment["next_required_witnesses"]),
        "carry_forward_hash": continuation_judgment["carry_forward_hash"],
        "preservation_result": preservation_record["preservation_result"],
        "blocked_transition": preservation_record["blocked_transition"],
        "preserved_transition": preservation_record["preserved_transition"],
        "preservation_reason_codes": list(preservation_record["preservation_reason_codes"]),
        "preservation_actions": list(preservation_record["preservation_actions"]),
        "continuation_disposition": preservation_record["continuation_disposition"],
        "preserved_continuation_corridor": preservation_record["preserved_continuation_corridor"],
        "preserved_debt_hash": preservation_record["preserved_debt_hash"],
        "self_continuation_terminated": preservation_record["self_continuation_terminated"],
        "preservation_witness_hash": preservation_record["preservation_witness_hash"],
    }



def judgment_against_boundary_material(*, artifact_boundary_act_hash: str, judgment_act_hash: str, outcome_judgment: Dict[str, Any], continuation_judgment: Dict[str, Any], preservation_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_boundary_act_hash": artifact_boundary_act_hash,
        "judgment_act_hash": judgment_act_hash,
        "outcome": outcome_judgment["outcome"],
        "judgment_mode": outcome_judgment["judgment_mode"],
        "reason_codes": list(outcome_judgment["reason_codes"]),
        "carry_forward_hash": continuation_judgment["carry_forward_hash"],
        "continuation_result": continuation_judgment["continuation_result"],
        "continuation_disposition": preservation_record["continuation_disposition"],
        "preservation_result": preservation_record["preservation_result"],
        "preservation_witness_hash": preservation_record["preservation_witness_hash"],
        "blocked_transition": preservation_record["blocked_transition"],
        "preserved_continuation_corridor": preservation_record["preserved_continuation_corridor"],
    }

def judgment_witness_material(*, judgment_context: Dict[str, Any], standing_judgment: Dict[str, Any], continuation_judgment: Dict[str, Any], outcome_judgment: Dict[str, Any], preservation_record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_boundary_claim_hash": judgment_context["artifact_boundary_claim_hash"],
        "artifact_executable_act_hash": judgment_context["artifact_executable_act_hash"],
        "artifact_continuation_act_hash": judgment_context["artifact_continuation_act_hash"],
        "artifact_cross_binding_hash": judgment_context["artifact_cross_binding_hash"],
        "translation_witness_hash": judgment_context["translation_witness_hash"],
        "continuity_witness_hash": judgment_context["continuity_witness_hash"],
        "branch_witness_hash": judgment_context["branch_witness_hash"],
        "standing_result": standing_judgment["standing_result"],
        "standing_after": standing_judgment["standing_after"],
        "standing_witness_hash": standing_judgment["standing_witness_hash"],
        "continuation_result": continuation_judgment["continuation_result"],
        "continuation_intent": continuation_judgment["continuation_intent"],
        "expected_continuation_result": continuation_judgment["expected_continuation_result"],
        "carry_directive": continuation_judgment["carry_directive"],
        "carry_reason_codes": list(continuation_judgment["carry_reason_codes"]),
        "debt_action": continuation_judgment["debt_action"],
        "continuation_witness_hash": continuation_judgment["continuation_witness_hash"],
        "carry_forward_hash": continuation_judgment["carry_forward_hash"],
        "parent_continuity_verified": continuation_judgment["parent_continuity_verified"],
        "outcome": outcome_judgment["outcome"],
        "burden_result": outcome_judgment["burden_result"],
        "outcome_witness_hash": outcome_judgment["outcome_witness_hash"],
        "preservation_result": preservation_record["preservation_result"],
        "preservation_reason_codes": list(preservation_record["preservation_reason_codes"]),
        "continuation_disposition": preservation_record["continuation_disposition"],
        "preservation_witness_hash": preservation_record["preservation_witness_hash"],
    }

@dataclass(frozen=True)
class ReceiptSectionIntegrity:
    section: str
    section_hash: str
    section_signature: str
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ReceiptIntegrity:
    judgment_context: ReceiptSectionIntegrity
    standing_judgment: ReceiptSectionIntegrity
    continuation_judgment: ReceiptSectionIntegrity
    outcome_judgment: ReceiptSectionIntegrity
    preservation_record: ReceiptSectionIntegrity
    lawful_context_proof: str
    judgment_witness_hash: str
    judgment_act_hash: str
    judgment_against_boundary_hash: str
    continuation_preservation_binding_hash: str
    judgment_cross_binding_hash: str
    receipt_binding_hash: str
    judgment_surface_hash: str
    proof_surface_hash: str
    receipt_hash: str
    receipt_signature: str
    def judgment_surface(self) -> Dict[str, Any]:
        return {
            "judgment_context_hash": self.judgment_context.section_hash,
            "standing_judgment_hash": self.standing_judgment.section_hash,
            "continuation_judgment_hash": self.continuation_judgment.section_hash,
            "outcome_judgment_hash": self.outcome_judgment.section_hash,
            "preservation_record_hash": self.preservation_record.section_hash,
            "lawful_context_proof": self.lawful_context_proof,
            "judgment_witness_hash": self.judgment_witness_hash,
            "judgment_act_hash": self.judgment_act_hash,
            "judgment_against_boundary_hash": self.judgment_against_boundary_hash,
            "continuation_preservation_binding_hash": self.continuation_preservation_binding_hash,
            "judgment_cross_binding_hash": self.judgment_cross_binding_hash,
        }
    def proof_surface(self) -> Dict[str, Any]:
        return {
            "receipt_binding_hash": self.receipt_binding_hash,
            "judgment_surface_hash": self.judgment_surface_hash,
        }
    def to_dict(self) -> Dict[str, Any]:
        return {
            "judgment_context": self.judgment_context.to_dict(),
            "standing_judgment": self.standing_judgment.to_dict(),
            "continuation_judgment": self.continuation_judgment.to_dict(),
            "outcome_judgment": self.outcome_judgment.to_dict(),
            "preservation_record": self.preservation_record.to_dict(),
            "lawful_context_proof": self.lawful_context_proof,
            "judgment_witness_hash": self.judgment_witness_hash,
            "judgment_act_hash": self.judgment_act_hash,
            "judgment_against_boundary_hash": self.judgment_against_boundary_hash,
            "continuation_preservation_binding_hash": self.continuation_preservation_binding_hash,
            "judgment_cross_binding_hash": self.judgment_cross_binding_hash,
            "receipt_binding_hash": self.receipt_binding_hash,
            "judgment_surface_hash": self.judgment_surface_hash,
            "proof_surface_hash": self.proof_surface_hash,
            "receipt_hash": self.receipt_hash,
            "receipt_signature": self.receipt_signature,
        }


@dataclass(frozen=True)
class ReceiptJudgment:
    judgment_context: JudgmentContext
    standing_judgment: StandingJudgment
    continuation_judgment: ContinuationJudgment
    outcome_judgment: OutcomeJudgment
    preservation_record: PreservationRecord

    def to_dict(self) -> Dict[str, Any]:
        return {
            "judgment_context": self.judgment_context.to_dict(),
            "standing_judgment": self.standing_judgment.to_dict(),
            "continuation_judgment": self.continuation_judgment.to_dict(),
            "outcome_judgment": self.outcome_judgment.to_dict(),
            "preservation_record": self.preservation_record.to_dict(),
        }

@dataclass(frozen=True)
class ReceiptProof:
    integrity: ReceiptIntegrity

    def to_dict(self) -> Dict[str, Any]:
        return self.integrity.to_dict()

@dataclass(frozen=True)
class DecisionReceipt:
    receipt_id: str
    artifact_id: str
    judgment_context: JudgmentContext
    standing_judgment: StandingJudgment
    continuation_judgment: ContinuationJudgment
    outcome_judgment: OutcomeJudgment
    preservation_record: PreservationRecord
    integrity: ReceiptIntegrity
    created_at: str

    def __post_init__(self) -> None:
        for name, cls in [
            ("judgment_context", JudgmentContext),
            ("standing_judgment", StandingJudgment),
            ("continuation_judgment", ContinuationJudgment),
            ("outcome_judgment", OutcomeJudgment),
            ("preservation_record", PreservationRecord),
        ]:
            value = getattr(self, name)
            if isinstance(value, dict):
                if name == "outcome_judgment" and "judgment_mode" not in value:
                    value = {**value, "judgment_mode": ("REFUSE_PRESERVE" if value.get("outcome") == "REFUSE_BLOCK" else value.get("outcome"))}
                object.__setattr__(self, name, cls(**value))
        if isinstance(self.integrity, dict):
            i = self.integrity
            object.__setattr__(self, "integrity", ReceiptIntegrity(
                judgment_context=ReceiptSectionIntegrity(**i["judgment_context"]),
                standing_judgment=ReceiptSectionIntegrity(**i["standing_judgment"]),
                continuation_judgment=ReceiptSectionIntegrity(**i["continuation_judgment"]),
                outcome_judgment=ReceiptSectionIntegrity(**i["outcome_judgment"]),
                preservation_record=ReceiptSectionIntegrity(**i["preservation_record"]),
                lawful_context_proof=i["lawful_context_proof"],
                judgment_witness_hash=i["judgment_witness_hash"],
                judgment_act_hash=i.get("judgment_act_hash",""),
                judgment_against_boundary_hash=i.get("judgment_against_boundary_hash",""),
                continuation_preservation_binding_hash=i.get("continuation_preservation_binding_hash",""),
                judgment_cross_binding_hash=i["judgment_cross_binding_hash"],
                receipt_binding_hash=i["receipt_binding_hash"],
                judgment_surface_hash=i.get("judgment_surface_hash",""),
                proof_surface_hash=i.get("proof_surface_hash",""),
                receipt_hash=i["receipt_hash"],
                receipt_signature=i["receipt_signature"],
            ))

    @property
    def judgment(self) -> ReceiptJudgment:
        return ReceiptJudgment(
            judgment_context=self.judgment_context,
            standing_judgment=self.standing_judgment,
            continuation_judgment=self.continuation_judgment,
            outcome_judgment=self.outcome_judgment,
            preservation_record=self.preservation_record,
        )

    @property
    def proof(self) -> ReceiptProof:
        return ReceiptProof(integrity=self.integrity)

    @property
    def lawful_context_proof(self) -> str: return self.integrity.lawful_context_proof
    @property
    def receipt_signature(self) -> str: return self.integrity.receipt_signature
    @property
    def outcome(self) -> str: return self.outcome_judgment.outcome
    @property
    def reason_codes(self) -> List[str]: return self.outcome_judgment.reason_codes
    @property
    def standing_result(self) -> str: return self.standing_judgment.standing_result
    @property
    def burden_result(self) -> str: return self.outcome_judgment.burden_result
    @property
    def continuation_result(self) -> str: return self.continuation_judgment.continuation_result
    @property
    def escalation_target(self) -> Optional[str]: return self.outcome_judgment.escalation_target
    @property
    def branch_id(self) -> str: return self.judgment_context.execution_branch_id
    @property
    def branch_derivation(self) -> str: return self.judgment_context.branch_derivation

    def judgment_act_material(self) -> Dict[str, Any]:
        return judgment_act_material(
            judgment_context=self.judgment_context.to_dict(),
            continuation_judgment=self.continuation_judgment.to_dict(),
            outcome_judgment=self.outcome_judgment.to_dict(),
            preservation_record=self.preservation_record.to_dict(),
        )

    def binding_material(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "artifact_id": self.artifact_id,
            "judgment_context_hash": self.integrity.judgment_context.section_hash,
            "standing_judgment_hash": self.integrity.standing_judgment.section_hash,
            "continuation_judgment_hash": self.integrity.continuation_judgment.section_hash,
            "outcome_judgment_hash": self.integrity.outcome_judgment.section_hash,
            "preservation_record_hash": self.integrity.preservation_record.section_hash,
            "lawful_context_proof": self.integrity.lawful_context_proof,
            "artifact_cross_binding_hash": self.judgment_context.artifact_cross_binding_hash,
            "artifact_boundary_claim_hash": self.judgment_context.artifact_boundary_claim_hash,
            "translation_witness_hash": self.judgment_context.translation_witness_hash,
            "continuity_witness_hash": self.judgment_context.continuity_witness_hash,
            "branch_witness_hash": self.judgment_context.branch_witness_hash,
            "continuation_witness_hash": self.continuation_judgment.continuation_witness_hash,
            "carry_forward_hash": self.continuation_judgment.carry_forward_hash,
            "preservation_witness_hash": self.preservation_record.preservation_witness_hash,
            "judgment_cross_binding_hash": self.integrity.judgment_cross_binding_hash,
            "lawful_context_proof": self.integrity.lawful_context_proof,
        }

    def judgment_surface_material(self) -> Dict[str, Any]:
        return self.integrity.judgment_surface()

    def proof_surface_material(self) -> Dict[str, Any]:
        return {
            "receipt_binding_hash": self.integrity.receipt_binding_hash,
            "judgment_surface_hash": self.integrity.judgment_surface_hash,
            "receipt_hash": self.integrity.receipt_hash,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "artifact_id": self.artifact_id,
            "judgment": {
                "judgment_context": self.judgment_context.to_dict(),
                "standing_judgment": self.standing_judgment.to_dict(),
                "continuation_judgment": self.continuation_judgment.to_dict(),
                "outcome_judgment": self.outcome_judgment.to_dict(),
                "preservation_record": self.preservation_record.to_dict(),
            },
            "proof": self.integrity.to_dict(),
            "created_at": self.created_at,
        }

    def signable_dict(self) -> Dict[str, Any]:
        data = self.to_dict()
        data["proof"] = dict(data["proof"])
        data["proof"]["receipt_signature"] = ""
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionReceipt":
        if "judgment" not in data or "proof" not in data:
            raise ValueError("decision receipt must use explicit judgment/proof surfaces")
        judgment = data["judgment"]
        normalized = {
            "receipt_id": data["receipt_id"],
            "artifact_id": data["artifact_id"],
            "judgment_context": judgment["judgment_context"],
            "standing_judgment": judgment["standing_judgment"],
            "continuation_judgment": judgment["continuation_judgment"],
            "outcome_judgment": judgment["outcome_judgment"],
            "preservation_record": judgment["preservation_record"],
            "integrity": data["proof"],
            "created_at": data["created_at"],
        }
        return cls(**normalized)

@dataclass(frozen=True)
class CommitRequest:
    artifact: ExecutionArtifact

@dataclass(frozen=True)
class CommitResult:
    allowed: bool
    receipt: DecisionReceipt
    pre_state_hash: str
    post_state_hash: Optional[str]
    committed_status: Optional[str]
    message: str

def build_artifact(**kwargs: Any) -> ExecutionArtifact:
    timestamp = kwargs.pop("timestamp", None) or utcnow_iso()
    payload = dict(kwargs["payload"])
    intent = ArtifactIntentSurface(
        workflow_id=kwargs["workflow_id"],
        workflow_step=kwargs["workflow_step"],
        requested_transition=kwargs["requested_transition"],
        actor_id=kwargs["actor_id"],
        authority_scope=list(kwargs["authority_scope"]),
        schema_id=kwargs["schema_id"],
        schema_version=kwargs["schema_version"],
        constraint_bundle_hash=kwargs["constraint_bundle_hash"],
    )
    law = ArtifactLawBinding(
        contract_version=ARTIFACT_CONTRACT_VERSION,
        artifact_kind=ARTIFACT_KIND,
        governing_basis_id=kwargs["governing_basis_id"],
        governing_basis_version=kwargs["governing_basis_version"],
        governing_basis_hash=kwargs["governing_basis_hash"],
        basis_lineage_hash=kwargs["basis_lineage_hash"],
        basis_signature=kwargs["basis_signature"],
        logic_version=kwargs["logic_version"],
    )
    translation_base = {
        "source_intent": kwargs["source_intent"],
        "executable_claim": kwargs["executable_claim"],
        "translation_constraints": list(kwargs["translation_constraints"]),
        "translation_outcome": kwargs["translation_outcome"],
        "steward_lane": kwargs["steward_lane"],
        "visible_surface": kwargs["visible_surface"],
        "translation_digest": kwargs["translation_digest"],
        "translation_narrowing": list(kwargs["translation_narrowing"]),
        "preserved_claims": list(kwargs["preserved_claims"]),
    }
    translation = ArtifactTranslationRecord(
        **translation_base,
        translation_witness_hash=sha256_obj(translation_witness_material(
            payload=payload, intent=intent.to_dict(), translation=translation_base, law=law.to_dict()
        )),
    )
    continuity_base = {
        "state_ref": kwargs["state_ref"],
        "declared_state_hash": kwargs["declared_state_hash"],
        "declared_entity_id": kwargs["declared_entity_id"],
        "declared_current_status": kwargs["declared_current_status"],
        "declared_open_burden_codes": list(kwargs["declared_open_burden_codes"]),
        "parent_receipt_id": kwargs["parent_receipt_id"],
        "parent_receipt_signature": kwargs["parent_receipt_signature"],
        "parent_receipt_witness_hash": kwargs["parent_receipt_witness_hash"],
        "continuity_chain_head": kwargs["continuity_chain_head"],
        "continuity_mode": kwargs["continuity_mode"],
        "continuation_intent": kwargs["continuation_intent"],
        "continuation_constraints": list(kwargs["continuation_constraints"]),
        "expected_continuation_result": kwargs["expected_continuation_result"],
        "continuity_debt_in": list(kwargs["continuity_debt_in"]),
        "inherited_burden_codes": list(kwargs["inherited_burden_codes"]),
    }
    continuity = ArtifactContinuityEntry(
        **continuity_base,
        continuity_witness_hash=sha256_obj(continuity_witness_material(continuity=continuity_base)),
    )
    branch_base = {
        "execution_branch_id": kwargs["execution_branch_id"],
        "branch_derivation": kwargs["branch_derivation"],
        "branch_role": kwargs["branch_role"],
        "claims_sovereign_authority": kwargs["claims_sovereign_authority"],
        "declared_escalation_target": kwargs["declared_escalation_target"],
        "surface_steward": kwargs["surface_steward"],
    }
    branch = ArtifactBranchPosture(
        **branch_base,
        branch_witness_hash=sha256_obj(branch_witness_material(branch=branch_base, translation=translation.to_dict())),
    )
    empty = ArtifactSectionIntegrity(section="empty", section_hash="", section_signature="")
    return ExecutionArtifact(
        artifact_id=kwargs["artifact_id"],
        payload=payload,
        intent_surface=intent,
        translation_record=translation,
        law_binding=law,
        continuity_entry=continuity,
        branch_posture=branch,
        integrity=ArtifactIntegrity(
            payload_hash=sha256_obj(payload),
            intent=empty, translation=empty, law=empty, continuity=empty, branch=empty,
            bridge_hash="", witness_hash="", executable_act_hash="", continuation_act_hash="", boundary_act_hash="", cross_binding_hash="", boundary_claim_hash="", claim_surface_hash="", proof_surface_hash="", artifact_signature=None,
        ),
        timestamp=timestamp,
    )
