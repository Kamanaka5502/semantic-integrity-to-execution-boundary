
from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from veritas_aegis.contracts import (
    build_artifact,
    CommitRequest,
    DecisionReceipt,
    ExecutionArtifact,
    judgment_act_material,
)
from veritas_aegis.engine import VeritasAegisEngine
from veritas_aegis.storage import JsonStore
from veritas_aegis.receipts import verify_lawful_context
from veritas_aegis.util import sha256_obj

def demo_basis():
    rules = {
        "schema": {
            "schema_id": "sdc.encounter",
            "schema_version": "1.0.0",
            "constraint_bundle_hash": sha256_obj({"bundle": "encounter-v1"}),
            "required_payload_fields": ["entity_id", "summary", "risk_level"],
        },
        "actors": {
            "operator.sam": ["commit.review", "commit.approve"],
            "operator.jules": ["commit.review"],
        },
        "require_parent_receipt_for_statuses": ["reviewed"],
        "transitions": {
            "submit_for_review": {"from": ["draft"], "to": "reviewed", "required_scope": ["commit.review"], "required_payload_matches": ["summary"], "max_risk": 5},
            "approve": {"from": ["reviewed"], "to": "approved", "required_scope": ["commit.approve"], "required_payload_matches": ["summary"], "max_risk": 2},
        },
        "branch_policy": {
            "allowed_branch_id": "ai.branch.sam",
            "required_derivation": "DERIVATIVE",
            "required_branch_role": "EXECUTION_BOUNDARY_STEWARD",
            "forbid_sovereign_claim": True,
            "require_translation_digest": True,
            "require_source_intent": True,
            "required_steward_lane": "VISIBLE_EXECUTION_BRANCH",
            "required_visible_surface": "commit_boundary",
            "allowed_workflows": ["workflow.intake", "workflow.review"],
        },
        "escalation_corridors": {
            "submit_for_review": "oversight.review",
            "approve": "oversight.approval",
        },
    }
    return {"basis_id": "basis.core", "version": "2026.03.30", "rules": rules}


class ArtifactReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.engine = VeritasAegisEngine(store_root=self.tmp.name)
        self.basis = self.engine.put_basis(demo_basis())
        self.engine.put_state("state.case.1", {
            "entity_id": "case-1",
            "current_status": "draft",
            "attributes": {},
            "open_burdens": [],
            "continuity_chain_head": None,
            "continuity_debt": [],
        })

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, **overrides):
        snap = self.engine.resolve_state("state.case.1")
        data = dict(
            artifact_id="artifact-1",
            payload={"entity_id": "case-1", "summary": "ready", "risk_level": 1},
            schema_id="sdc.encounter",
            schema_version="1.0.0",
            constraint_bundle_hash=self.basis.rules["schema"]["constraint_bundle_hash"],
            workflow_id="workflow.intake",
            workflow_step="submit",
            requested_transition="submit_for_review",
            actor_id="operator.sam",
            authority_scope=["commit.review"],
            state_ref="state.case.1",
            declared_state_hash=snap.state_hash,
            declared_entity_id=snap.entity_id,
            declared_current_status=snap.current_status,
            declared_open_burden_codes=list(snap.open_burdens),
            parent_receipt_id=None,
            parent_receipt_signature=None,
            parent_receipt_witness_hash=None,
            continuity_chain_head=snap.continuity_chain_head,
            continuity_mode="self",
            continuation_intent="continue self through commit boundary",
            continuation_constraints=["preserve parent continuity", "carry debt honestly"],
            expected_continuation_result="ALLOW",
            continuity_debt_in=list(snap.continuity_debt),
            inherited_burden_codes=list(snap.open_burdens),
            governing_basis_id=self.basis.basis_id,
            governing_basis_version=self.basis.version,
            governing_basis_hash=self.basis.basis_hash,
            basis_lineage_hash=self.basis.lineage_hash,
            basis_signature=self.basis.signature,
            logic_version="1.0.0",
            execution_branch_id="ai.branch.sam",
            branch_derivation="DERIVATIVE",
            branch_role="EXECUTION_BOUNDARY_STEWARD",
            claims_sovereign_authority=False,
            source_intent="submit case for review",
            executable_claim="submit_for_review",
            translation_constraints=["preserve basis"],
            translation_outcome="PRESERVE",
            steward_lane="VISIBLE_EXECUTION_BRANCH",
            visible_surface="commit_boundary",
            translation_digest=sha256_obj({"step": "submit", "intent": "review"}),
            translation_narrowing=[],
            preserved_claims=["requested_transition"],
            declared_escalation_target=None,
            surface_steward="samantha",
        )
        data.update(overrides)
        return self.engine.sign_artifact(build_artifact(**data))

    def test_safe_commit_and_receipt_verifies(self):
        result = self.engine.commit(CommitRequest(self.build()))
        self.assertTrue(result.allowed)
        self.assertEqual(result.committed_status, "reviewed")
        self.assertTrue(self.engine.verify_receipt(result.receipt.to_dict()))
        self.assertTrue(verify_lawful_context(result.receipt))

    def test_artifact_uses_claim_and_proof_surfaces(self):
        artifact = self.build().to_dict()
        self.assertIn("claim", artifact)
        self.assertIn("proof", artifact)
        self.assertNotIn("intent_surface", artifact)
        self.assertNotIn("integrity", artifact)

    def test_receipt_uses_judgment_and_proof_surfaces(self):
        receipt = self.engine.evaluate(CommitRequest(self.build())).to_dict()
        self.assertIn("judgment", receipt)
        self.assertIn("proof", receipt)
        self.assertNotIn("judgment_context", receipt)
        self.assertNotIn("integrity", receipt)

    def test_artifact_translation_tamper_refuses(self):
        data = self.build().to_dict()
        data["claim"]["translation_record"]["source_intent"] = "tampered"
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(data)))
        self.assertIn("TRANSLATION_SECTION_HASH_MISMATCH", receipt.reason_codes)

    def test_artifact_boundary_act_tamper_refuses(self):
        data = self.build().to_dict()
        data["proof"]["boundary_act_hash"] = "bad"
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(data)))
        self.assertIn("ARTIFACT_BOUNDARY_ACT_HASH_MISMATCH", receipt.reason_codes)

    def test_declared_state_hash_mismatch_refuses(self):
        receipt = self.engine.evaluate(CommitRequest(self.build(declared_state_hash="bad")))
        self.assertIn("DECLARED_STATE_HASH_MISMATCH", receipt.reason_codes)

    def test_receipt_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["judgment"]["outcome_judgment"]["reason_codes"] = ["tampered"]
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_judgment_against_boundary_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["proof"]["judgment_against_boundary_hash"] = "bad"
        self.assertFalse(self.engine.verify_receipt(data))

    def test_parent_witness_required_and_verified(self):
        first = self.engine.commit(CommitRequest(self.build()))
        snap = self.engine.resolve_state("state.case.1")
        approve = self.build(
            artifact_id="artifact-2",
            requested_transition="approve",
            workflow_id="workflow.review",
            workflow_step="approve",
            authority_scope=["commit.approve"],
            source_intent="approve case",
            executable_claim="approve",
            translation_digest=sha256_obj({"step": "approve", "intent": "approve"}),
            parent_receipt_id=first.receipt.receipt_id,
            parent_receipt_signature=first.receipt.receipt_signature,
            parent_receipt_witness_hash=first.receipt.lawful_context_proof,
            continuity_chain_head=first.receipt.receipt_id,
            continuity_mode="parent",
            declared_state_hash=snap.state_hash,
            declared_current_status="reviewed",
        )
        result = self.engine.commit(CommitRequest(approve))
        self.assertTrue(result.allowed)
        self.assertEqual(result.committed_status, "approved")

    def test_parent_witness_mismatch_refuses(self):
        first = self.engine.commit(CommitRequest(self.build()))
        snap = self.engine.resolve_state("state.case.1")
        approve = self.build(
            artifact_id="artifact-2",
            requested_transition="approve",
            workflow_id="workflow.review",
            workflow_step="approve",
            authority_scope=["commit.approve"],
            source_intent="approve case",
            executable_claim="approve",
            translation_digest=sha256_obj({"step": "approve", "intent": "approve"}),
            parent_receipt_id=first.receipt.receipt_id,
            parent_receipt_signature=first.receipt.receipt_signature,
            parent_receipt_witness_hash="bad",
            continuity_chain_head=first.receipt.receipt_id,
            continuity_mode="parent",
            declared_state_hash=snap.state_hash,
            declared_current_status="reviewed",
        )
        receipt = self.engine.evaluate(CommitRequest(approve))
        self.assertIn("PARENT_RECEIPT_WITNESS_MISMATCH", receipt.reason_codes)

    def test_partial_standing_escalates(self):
        receipt = self.engine.evaluate(CommitRequest(self.build(actor_id="operator.jules", authority_scope=["commit.approve"])))
        self.assertEqual(receipt.standing_result, "PARTIAL")
        self.assertEqual(receipt.outcome, "ESCALATE")

    def test_open_burden_tightens(self):
        self.engine.put_state("state.case.1", {
            "entity_id": "case-1",
            "current_status": "draft",
            "attributes": {},
            "open_burdens": ["needs-human-check"],
            "continuity_chain_head": None,
            "continuity_debt": [],
        })
        receipt = self.engine.evaluate(CommitRequest(self.build(
            declared_open_burden_codes=["needs-human-check"],
            inherited_burden_codes=["needs-human-check"],
        )))
        self.assertEqual(receipt.burden_result, "TIGHTENED")
        self.assertEqual(receipt.outcome, "ESCALATE")

    def test_translation_narrowing_must_be_declared(self):
        receipt = self.engine.evaluate(CommitRequest(self.build(translation_outcome="NARROW", translation_narrowing=[])))
        self.assertIn("TRANSLATION_NARROWING_UNDECLARED", receipt.reason_codes)

    def test_replay_matches(self):
        artifact = self.build()
        result = self.engine.commit(CommitRequest(artifact))
        replay = self.engine.replay(result.receipt.receipt_id, artifact)
        self.assertTrue(replay["matches"])

    def test_replay_revalidates_boundary_judgment_relationship(self):
        artifact = self.build()
        receipt = self.engine.evaluate(CommitRequest(artifact))
        self.engine.store.put("receipts", receipt.receipt_id, receipt.to_dict())
        changed = self.build(continuation_intent="continue through a different corridor")
        replay = self.engine.replay(receipt.receipt_id, changed)
        self.assertFalse(replay["matches"])
        self.assertNotEqual(
            replay["stored"]["proof"]["judgment_against_boundary_hash"],
            replay["fresh"]["proof"]["judgment_against_boundary_hash"],
        )

    def test_ledgers_chain(self):
        self.engine.commit(CommitRequest(self.build()))
        evals = self.engine.store.ledger("evaluations")
        receipts = self.engine.store.ledger("receipt_judgments")
        self.assertEqual(len(evals), 1)
        self.assertEqual(len(receipts), 1)
        self.assertIsNone(evals[0]["previous_record_hash"])
        self.assertIsNone(receipts[0]["previous_record_hash"])

    def test_translation_witness_tamper_refuses(self):
        data = self.build().to_dict()
        data["claim"]["translation_record"]["translation_witness_hash"] = "bad"
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(data)))
        self.assertIn("TRANSLATION_WITNESS_HASH_MISMATCH", receipt.reason_codes)

    def test_artifact_cross_binding_tamper_refuses(self):
        data = self.build().to_dict()
        data["proof"]["cross_binding_hash"] = "bad"
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(data)))
        self.assertIn("ARTIFACT_CROSS_BINDING_HASH_MISMATCH", receipt.reason_codes)

    def test_artifact_executable_act_tamper_refuses(self):
        data = self.build().to_dict()
        data["proof"]["executable_act_hash"] = "bad"
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(data)))
        self.assertIn("ARTIFACT_EXECUTABLE_ACT_HASH_MISMATCH", receipt.reason_codes)

    def test_artifact_continuation_act_tamper_refuses(self):
        data = self.build().to_dict()
        data["proof"]["continuation_act_hash"] = "bad"
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(data)))
        self.assertIn("ARTIFACT_CONTINUATION_ACT_HASH_MISMATCH", receipt.reason_codes)

    def test_artifact_claim_surface_tamper_refuses(self):
        data = self.build().to_dict()
        data["proof"]["claim_surface_hash"] = "bad"
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(data)))
        self.assertIn("ARTIFACT_CLAIM_SURFACE_HASH_MISMATCH", receipt.reason_codes)

    def test_receipt_judgment_witness_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["proof"]["judgment_witness_hash"] = "bad"
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_binding_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["proof"]["receipt_binding_hash"] = "bad"
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_standing_witness_tamper_fails_verification(self):
        data = self.engine.evaluate(CommitRequest(self.build())).to_dict()
        data["judgment"]["standing_judgment"]["standing_witness_hash"] = "0" * 64
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_outcome_witness_tamper_fails_verification(self):
        data = self.engine.evaluate(CommitRequest(self.build())).to_dict()
        data["judgment"]["outcome_judgment"]["outcome_witness_hash"] = "f" * 64
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_judgment_surface_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["proof"]["judgment_surface_hash"] = "bad"
        self.assertFalse(self.engine.verify_receipt(data))

    def test_artifact_from_dict_requires_claim_and_proof(self):
        artifact = self.build().to_dict()
        flat = {
            "artifact_id": artifact["artifact_id"],
            "payload": artifact["payload"],
            "intent_surface": artifact["claim"]["intent_surface"],
            "translation_record": artifact["claim"]["translation_record"],
            "law_binding": artifact["claim"]["law_binding"],
            "continuity_entry": artifact["claim"]["continuity_entry"],
            "branch_posture": artifact["claim"]["branch_posture"],
            "integrity": artifact["proof"],
            "timestamp": artifact["timestamp"],
        }
        with self.assertRaises(ValueError):
            ExecutionArtifact.from_dict(flat)

    def test_receipt_from_dict_requires_judgment_and_proof(self):
        receipt = self.engine.evaluate(CommitRequest(self.build())).to_dict()
        flat = {
            "receipt_id": receipt["receipt_id"],
            "artifact_id": receipt["artifact_id"],
            "judgment_context": receipt["judgment"]["judgment_context"],
            "standing_judgment": receipt["judgment"]["standing_judgment"],
            "continuation_judgment": receipt["judgment"]["continuation_judgment"],
            "outcome_judgment": receipt["judgment"]["outcome_judgment"],
            "preservation_record": receipt["judgment"]["preservation_record"],
            "integrity": receipt["proof"],
            "created_at": receipt["created_at"],
        }
        with self.assertRaises(ValueError):
            DecisionReceipt.from_dict(flat)

    def test_translation_preserve_requires_preserved_claims(self):
        artifact = self.build(preserved_claims=[]).to_dict()
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(artifact)))
        self.assertEqual(receipt.outcome, "REFUSE_BLOCK")
        self.assertIn("PRESERVE_REQUIRES_PRESERVED_CLAIMS", receipt.reason_codes)

    def test_translation_redirect_requires_declared_target(self):
        artifact = self.build(translation_outcome="REDIRECT", declared_escalation_target=None).to_dict()
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(artifact)))
        self.assertEqual(receipt.outcome, "REFUSE_BLOCK")
        self.assertIn("REDIRECT_REQUIRES_DECLARED_TARGET", receipt.reason_codes)

    def test_refuse_preserve_is_first_class_judgment_mode(self):
        artifact = self.build(preserved_claims=[])
        receipt = self.engine.evaluate(CommitRequest(artifact))
        self.assertEqual(receipt.outcome, "REFUSE_BLOCK")
        material = judgment_act_material(
            judgment_context=receipt.judgment_context.to_dict(),
            continuation_judgment=receipt.continuation_judgment.to_dict(),
            outcome_judgment=receipt.outcome_judgment.to_dict(),
            preservation_record=receipt.preservation_record.to_dict(),
        )
        self.assertEqual(material["judgment_mode"], "REFUSE_PRESERVE")
        self.assertEqual(receipt.preservation_record.blocked_transition, artifact.requested_transition)
        self.assertTrue(receipt.preservation_record.refusal_preserves_manifold)
        self.assertTrue(receipt.preservation_record.self_continuation_terminated)

    def test_ledger_storage_is_index_plus_record_files_not_one_giant_array(self):
        store = JsonStore(self.tmp.name)
        first = store.append("demo_ledger", {"n": 1}, unique_key="one")
        second = store.append("demo_ledger", {"n": 2}, unique_key="two")
        index_path = Path(self.tmp.name) / "demo_ledger" / "_index.json"
        records_dir = Path(self.tmp.name) / "demo_ledger" / "records"
        self.assertTrue(index_path.exists())
        self.assertTrue((records_dir / f"{first['record_hash']}.json").exists())
        self.assertTrue((records_dir / f"{second['record_hash']}.json").exists())
        self.assertEqual(len(store.ledger("demo_ledger")), 2)

    def test_unique_key_prevents_duplicate_ledger_entries(self):
        store = JsonStore(self.tmp.name)
        first = store.append("demo_dedupe", {"n": 1}, unique_key="same")
        second = store.append("demo_dedupe", {"n": 999}, unique_key="same")
        ledger = store.ledger("demo_dedupe")
        self.assertEqual(first["record_hash"], second["record_hash"])
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]["n"], 1)


    def test_receipt_judgment_act_tamper_fails_verification(self):
        receipt = self.engine.commit(CommitRequest(self.build())).receipt
        data = receipt.to_dict()
        data["judgment"]["preservation_record"]["continuation_disposition"] = "DRIFTED"
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_continuation_preservation_binding_tamper_fails_verification(self):
        receipt = self.engine.commit(CommitRequest(self.build())).receipt
        data = receipt.to_dict()
        data["proof"]["continuation_preservation_binding_hash"] = "tampered"
        self.assertFalse(self.engine.verify_receipt(data))


    def test_receipt_continuation_witness_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["judgment"]["continuation_judgment"]["continuation_witness_hash"] = "1" * 64
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_carry_forward_hash_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["judgment"]["continuation_judgment"]["carry_forward_hash"] = "2" * 64
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_preservation_witness_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["judgment"]["preservation_record"]["preservation_witness_hash"] = "3" * 64
        self.assertFalse(self.engine.verify_receipt(data))

    def test_receipt_lawful_context_proof_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["proof"]["lawful_context_proof"] = "4" * 64
        self.assertFalse(self.engine.verify_receipt(data))

    def test_artifact_proof_surface_hash_tamper_refuses(self):
        data = self.build().to_dict()
        data["proof"]["proof_surface_hash"] = "bad"
        receipt = self.engine.evaluate(CommitRequest(ExecutionArtifact.from_dict(data)))
        self.assertIn("ARTIFACT_PROOF_SURFACE_HASH_MISMATCH", receipt.reason_codes)

    def test_receipt_proof_surface_hash_tamper_fails_verification(self):
        data = self.engine.commit(CommitRequest(self.build())).receipt.to_dict()
        data["proof"]["proof_surface_hash"] = "bad"
        self.assertFalse(self.engine.verify_receipt(data))

    def test_refuse_preserve_runtime_sets_judgment_mode(self):
        receipt = self.engine.evaluate(CommitRequest(self.build(preserved_claims=[])))
        self.assertEqual(receipt.outcome, "REFUSE_BLOCK")
        self.assertEqual(receipt.outcome_judgment.judgment_mode, "REFUSE_PRESERVE")

    def test_replay_reports_precise_continuation_preservation_mismatch_reason(self):
        from dataclasses import replace

        commit = self.engine.commit(CommitRequest(self.build()))
        replay_artifact = self.build()
        replay_artifact = replace(
            replay_artifact,
            continuity_entry=replace(
                replay_artifact.continuity_entry,
                continuation_intent="drifted intent",
            ),
        )
        replay_artifact = self.engine.sign_artifact(replay_artifact)
        replay = self.engine.replay(commit.receipt.receipt_id, replay_artifact)
        self.assertFalse(replay["matches"])
        self.assertIn("JUDGMENT_AGAINST_BOUNDARY_HASH_MISMATCH", replay["mismatches"])
        self.assertIn("CONTINUATION_PRESERVATION_BINDING_HASH_MISMATCH", replay["mismatches"])

    def test_preservation_ledger_records_refuse_preserve_binding(self):
        result = self.engine.commit(CommitRequest(self.build(preserved_claims=[])))
        self.assertEqual(result.receipt.outcome_judgment.judgment_mode, "REFUSE_PRESERVE")
        records = self.engine.store.ledger("preservations")
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["judgment_mode"], "REFUSE_PRESERVE")
        self.assertEqual(
            record["judgment_against_boundary_hash"],
            result.receipt.integrity.judgment_against_boundary_hash,
        )
        self.assertEqual(
            record["continuation_preservation_binding_hash"],
            result.receipt.integrity.continuation_preservation_binding_hash,
        )

    def test_receipt_judgment_against_boundary_hash_binds_carry_and_preservation(self):
        from dataclasses import replace

        commit = self.engine.commit(CommitRequest(self.build()))
        receipt = DecisionReceipt.from_dict(commit.receipt.to_dict())
        original = receipt.integrity.judgment_against_boundary_hash
        tampered = replace(
            receipt,
            continuation_judgment=replace(
                receipt.continuation_judgment,
                carry_reason_codes=receipt.continuation_judgment.carry_reason_codes + ["EXTRA_REASON"],
            ),
        )
        self.assertFalse(self.engine.verify_receipt(tampered.to_dict()))
        self.assertEqual(original, receipt.integrity.judgment_against_boundary_hash)


if __name__ == "__main__":
    unittest.main()

def test_run_proof_script_outputs_positive_and_negative_cases(tmp_path):
    import subprocess, sys
    root = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [sys.executable, "run_proof.py"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    out = proc.stdout
    assert "VERITAS AEGIS — PROOF RUN" in out
    assert "Positive case" in out
    assert "Negative case (wrong branch id)" in out
    assert "Replay Match: True" in out
    assert "Replay Match: False" in out



class ProofRunnerTests(unittest.TestCase):
    def test_proof_runner_json_has_positive_negative_and_stress(self):
        import json
        import subprocess
        import tempfile
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "proof.json"
            proc = subprocess.run(
                [sys.executable, str(root / "run_proof.py"), "--output", str(output_path), "--quiet", "--stress", "3"],
                cwd=str(root),
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.stdout, "")
            report = json.loads(output_path.read_text())

        positive = report["proof"]["positive"]
        negative = report["proof"]["negative"]
        stress = report["stress"]

        self.assertTrue(positive["allowed"])
        self.assertEqual(positive["outcome"], "SAFE_COMMIT")
        self.assertTrue(positive["replay"]["matches"])
        self.assertFalse(negative["replay"]["matches"])
        self.assertIn("JUDGMENT_AGAINST_BOUNDARY_HASH_MISMATCH", negative["replay"]["mismatches"])
        self.assertTrue(stress["deterministic"])
        self.assertEqual(stress["unique_outcomes"], ["SAFE_COMMIT"])
        self.assertEqual(stress["unique_judgment_against_boundary_hash_count"], 1)
        self.assertEqual(stress["unique_judgment_cross_binding_hash_count"], 1)
