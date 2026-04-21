# Veritas Aegis — Semantic Integrity to Execution Boundary

A deterministic execution-boundary proof surface showing how a semantically valid instruction reaches the final gate before state change.

## Core Idea

SDC checks the instruction.

Veritas decides whether it is allowed to become real.

## Two-Gate Model

### Gate 1 — Semantic Gate
- structure
- completeness
- correctness
- semantic validation

### Gate 2 — Execution Gate
- authority
- live state alignment
- constraint compliance
- branch legitimacy
- risk / readiness
- continuation law

Outcomes:
- SAFE_COMMIT
- REFUSE_BLOCK
- ESCALATE

## Quick Run

```bash
python run_proof.py
python run_proof.py --stress 5
python run_proof.py --output proof_output.json --quiet
