# Veritas Aegis — Execution Boundary System

Nothing becomes real unless it proves admissibility at commit.

---

## 🚀 60-Second Proof

Start the system:
./run_api_stdlib.sh

Health check:
curl http://127.0.0.1:8001/health

Run admissible case (Healthcare):
curl -X POST http://127.0.0.1:8001/evaluate/proof -H "Content-Type: application/json" -d @demo_healthcare.json

Expected:
- decision: EXECUTE
- commit_result: COMMITTED
- proof_replay_equivalent: true

Run constrained case (Maritime):
curl -X POST http://127.0.0.1:8001/evaluate/proof -H "Content-Type: application/json" -d @demo_maritime.json

Expected:
- decision: ESCALATE
- commit_result: ESCALATED
- proof_replay_equivalent: true

---

## What This Proves

Execution is not allowed by default.

Every state transition must:
- satisfy admissibility
- produce a deterministic receipt
- replay to the same decision

This is pre-execution enforcement at the commit boundary.

---

## System Overview

Veritas Aegis evaluates whether a proposed state transition is allowed to become real.

Execution Flow:
SDC Payload → Boundary Gate → Veritas Judgment → State Mutation

- SDC Payload: Structured, schema-valid intent entering the system
- Boundary Gate: Commit boundary where admissibility is enforced
- Veritas Judgment: Deterministic evaluation against invariants and state
- State Mutation: Only occurs if the transition is proven admissible

---

## Key Properties

- Deterministic decision engine (EXECUTE / ESCALATE / REFUSE / HALT)
- Commit-time enforcement (not post-execution validation)
- Cryptographic receipt generation
- Replay verification (same input → same outcome)
- Fail-closed behavior under invalid conditions

---

## Proof Artifacts

Each execution produces:
- decision
- reason
- checks (admissibility vector)
- state_hash
- transition_hash
- receipt_id

All outputs are:
- reproducible
- verifiable
- replay-safe

---

## Positioning

This is not:
- a wrapper
- a monitoring layer
- a policy engine

This is the execution boundary where actions must prove they are allowed to exist.

---

## Repository Structure

- app/ — core runtime (admissibility, commit gate, receipts, replay)
- corridors/ — domain-specific enforcement logic (healthcare, maritime, etc.)
- cases/ — executable test scenarios
- run_api_stdlib.sh — API entrypoint
- demo_*.json — proof inputs

---

## Authors

Samantha Revita  
Terry Snyder  

Veritas Aegis
