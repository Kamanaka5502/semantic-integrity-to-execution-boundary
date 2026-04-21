# Veritas Aegis — Semantic Integrity to Execution Boundary

A deterministic execution-boundary proof surface showing how a semantically valid instruction reaches the final gate before state change.

## Core Idea

SDC checks the instruction.  
Veritas decides whether it is allowed to become real.

---

## Execution Flow (End-to-End)

## Upstream System
*(LLM / Rules Engine / API / Workflow)*

↓

## Semantic Validation Layer (SDC)
- **structure**
- **completeness**
- **correctness**

↓

## Veritas Aegis — Execution Boundary
- **authority validation**
- **live state alignment**
- **constraint enforcement**
- **branch legitimacy**
- **risk / readiness**
- **continuation law**

↓

## Commit Boundary
*(database write / external action / real-world effect)*

↓

## Outcome + Receipt
- **SAFE_COMMIT**
- **REFUSE_BLOCK**
- **ESCALATE**
- **deterministic receipt + replay**

---

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

**Outcomes:**
- SAFE_COMMIT
- REFUSE_BLOCK
- ESCALATE

---

## Quick Run

```bash
python run_proof.py
python run_proof.py --stress 5
python run_proof.py --output proof_output.json --quiet
```

## Proof Output — What to Look For

### Positive Path (Valid Execution)
- `allowed: true`
- `outcome: SAFE_COMMIT`
- `replay: matches: true`

**This shows:**
- the transition is admissible  
- the commit boundary was satisfied  
- replay produces the same result  
- hashes remain stable → deterministic enforcement  

---

### Negative Path (Invalid Mutation)
- `allowed: false`
- `outcome: REFUSE_BLOCK`
- `replay: matches: false`
- mismatches are explicitly listed  

**This shows:**
- invalid transitions are blocked before execution  
- mutation is detected at the boundary  
- replay divergence is provable and explicit  

---

### Determinism Signal

Across repeated executions:

- `judgment_against_boundary_hash` remains identical  
- `judgment_cross_binding_hash` remains identical  

**This proves:**
- enforcement is not probabilistic  
- decisions are not influenced by runtime drift  
- the execution boundary is mathematically stable  

---

## Where This Installs

Veritas Aegis is not a replacement for your system.  
It is the **execution boundary layer** that installs directly before state change.

---

## What It Requires

- A proposed action (`transition`)  
- Current system state (`state`)  
- Authority context (`authority envelope`)  
- Optional constraints / policies  

That’s it.

- No retraining  
- No orchestration rewrite  
- No dependency on upstream model behavior  

---

## What It Guarantees

- No invalid execution can pass the boundary  
- Every decision is provable and replayable  
- Identical conditions → identical outcomes  
- Enforcement is independent of upstream system behavior  

---

## What It Replaces

- “best effort” validation layers  
- post-execution audit logs  
- non-deterministic decision paths  
- trust in upstream correctness alone  

---

## What It Does Not Do

- does not generate decisions  
- does not interpret meaning  
- does not rely on model alignment  

---

> **Is this allowed to become real — right now, under current conditions?**

---

## What This Demonstrates

**Deterministic execution control**  
Execution is governed by fixed admissibility rules — not runtime interpretation or drift.

**Fail-closed enforcement**  
Nothing executes by default. Every transition must prove admissibility at the commit boundary.

**Explicit refusal and escalation conditions**  
Invalid transitions are not logged — they are actively **blocked or escalated** with defined reasoning.

**Separation of meaning vs. execution authority**  
Semantic correctness (SDC) does not grant execution rights.  
Authority is resolved independently at the boundary.

**Receipt-based proof of every decision**  
Every outcome emits a verifiable, hash-linked receipt that can be independently validated and replayed.

**Deterministic replay guarantees**  
Identical inputs produce identical outcomes. Replay confirms decision integrity.

**Boundary-level invariance enforcement**  
Judgment-against-boundary and cross-binding hashes remain stable across executions, proving enforcement is **structurally invariant at the execution boundary**.

---

**This system does not observe execution.  
It determines whether execution is allowed to exist.**
