# Veritas Aegis — Semantic Integrity to Execution Boundary

A deterministic execution-boundary proof surface showing how a semantically valid instruction reaches the final gate before state change.

## Core Idea

SDC validates the instruction.

Veritas decides whether it is allowed to become real.

## Two-Gate Model

Gate 1 — Semantic Gate (upstream)
- structure
- completeness
- correctness

Gate 2 — Execution Gate (Veritas)
- authority
- live state alignment
- constraints
- continuation law

Outcomes:
- SAFE_COMMIT
- REFUSE_BLOCK
- ESCALATE

## Quick Run

pip install -e .

python run_proof.py

## What You’ll See

- Positive path → SAFE_COMMIT
- Negative mutation → mismatch

This shows the boundary actually working.
