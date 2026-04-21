
from __future__ import annotations
from typing import List

def evaluate_derivative_ordering(artifact, basis) -> List[str]:
    reasons: List[str] = []
    policy = basis.rules.get("branch_policy", {})
    if artifact.execution_branch_id != policy.get("allowed_branch_id"):
        reasons.append("EXECUTION_BRANCH_MISMATCH")
    if artifact.branch_derivation != policy.get("required_derivation"):
        reasons.append("DERIVATIVE_ORDERING_VIOLATION")
    if artifact.branch_role != policy.get("required_branch_role"):
        reasons.append("BRANCH_ROLE_MISMATCH")
    if policy.get("forbid_sovereign_claim") and artifact.claims_sovereign_authority:
        reasons.append("SOVEREIGN_CLAIM_FORBIDDEN")
    if policy.get("required_steward_lane") and artifact.steward_lane != policy.get("required_steward_lane"):
        reasons.append("STEWARD_LANE_MISMATCH")
    if policy.get("required_visible_surface") and artifact.visible_surface != policy.get("required_visible_surface"):
        reasons.append("VISIBLE_SURFACE_MISMATCH")
    if policy.get("allowed_workflows") and artifact.workflow_id not in policy.get("allowed_workflows", []):
        reasons.append("WORKFLOW_NOT_ALLOWED")
    if policy.get("require_translation_digest") and not artifact.translation_digest:
        reasons.append("TRANSLATION_DIGEST_REQUIRED")
    if policy.get("require_source_intent") and not artifact.source_intent:
        reasons.append("SOURCE_INTENT_REQUIRED")
    if artifact.executable_claim != artifact.requested_transition:
        reasons.append("TRANSLATION_ACT_MISMATCH")
    if artifact.translation_outcome == "NARROW" and not artifact.translation_narrowing:
        reasons.append("TRANSLATION_NARROWING_UNDECLARED")
    return reasons
