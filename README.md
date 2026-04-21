<<<<<<< HEAD
# Veritas Aegis — Execution Boundary Demo

**Authors:** Samantha Revita, Terry Snyder  
**Organization:** Veritas Aegis  

---

## Semantic Integrity → Execution Boundary

Most systems today fail in a predictable way:

They preserve *structure*  
They attempt to preserve *meaning*  
But they do **not control whether that meaning is allowed to become real**

---

## The Problem

Modern AI + data systems break in two critical places:

### 1. Semantic Failure
- Context is incomplete  
- Meaning is ambiguous  
- Confidence is unclear  
- Systems still proceed anyway  

### 2. Execution Failure
- Actions are taken under invalid state  
- Authority is assumed, not verified  
- Risk is evaluated *after* execution  
- Systems fail **open instead of closed**

---

## The Missing Layer

There is no enforced boundary between:

**“This makes sense”**  
and  
**“This is allowed to happen”**

---

## The Veritas Model

We introduce a **dual-gate system** that enforces reality at the point of execution.

### Gate 1 — Semantic Gate  
> *Is the meaning valid, complete, and trustworthy?*

Checks:
- Context completeness  
- Ambiguity level  
- Confidence threshold  

Outcomes:
- PASS  
- REDIRECT  
- ESCALATE  

---

### Gate 2 — Execution Gate  
> *Even if meaning is correct — is execution allowed right now?*

Checks:
- Authority validity  
- State alignment  
- Risk thresholds  
- Execution readiness  

Outcomes:
- EXECUTE  
- REDIRECT  
- ESCALATE  
- REFUSE  

---

## The Core Principle

**The system does not execute because it has a proposal.**

**It executes only if the proposal remains admissible at the moment of commit.**

---

## Why This Matters

If you solve semantic integrity, you still face:

- Valid meaning applied under invalid conditions  
- Clean data triggering unsafe execution  
- Correct interpretation without enforceable action boundaries  

**Semantic correctness alone does not guarantee safe or lawful execution.**

---

## What This Repo Demonstrates

A minimal, deterministic runtime that shows:

1. Semantic evaluation (Gate 1)  
2. Execution admissibility (Gate 2)  
3. Final decision at the boundary  
4. Receipt generation with:
   - decision  
   - reason  
   - state hash  
   - timestamp  

---

## Example Output

{
  "action": "APPROVE_PRODUCTION_DEPLOYMENT",
  "semantic_gate": "PASS",
  "execution_gate": "ESCALATE",
  "decision": "ESCALATE",
  "reason": "Execution risk threshold exceeded",
  "state_hash": "...",
  "timestamp": "..."
}

---

## Key Insight

Even when:
- meaning is correct  
- data is clean  
- semantics are preserved  

execution can still be **blocked or escalated**  

Because:

**truth ≠ permission**

---

## Where This Fits

This layer sits directly between:

- AI systems (LLMs, agents, decision engines)  
- and real-world execution (APIs, workflows, systems)

It enforces:

→ no execution without admissibility  
→ no assumption of authority  
→ no silent risk acceptance  

---

## Run the Demo

git clone https://github.com/Kamanaka5502/semantic-integrity-to-execution-boundary.git  
cd semantic-integrity-to-execution-boundary  
python example_run.py  

---

## Final Position

This is not a wrapper.  
This is not observability.  
This is not post-hoc governance.  

This is **execution control at the boundary of reality.**

---

## Bottom Line

If your system guarantees meaning…

but does not control execution…

**you are still exposed.**

Veritas Aegis closes that gap.


---

## Status

This repository includes a runnable proof demonstrating lawful commit, replay stability, and mutation-visible refusal at the execution boundary.

The full runtime includes additional receipt integrity, lineage, and invariant enforcement layers.
=======
# Veritas Aegis v21.1

Deterministic execution-boundary artifact and receipt engine.

## Install
```bash
pip install -e .
```

## Run tests
```bash
python -m pytest -q
```

## Run the proof
```bash
python run_proof.py
```

This produces:
- one frozen basis
- one frozen state
- one signed artifact
- one commit result
- one replay check
- one negative replay check with a single-field mutation

## Package layout
- `veritas_aegis/engine.py` — evaluation and commit engine
- `veritas_aegis/contracts.py` — dataclasses and contract builders
- `veritas_aegis/storage.py` — append-only JSON storage
- `veritas_aegis/receipts.py` — lawful-context proof helpers
- `run_proof.py` — one-command deterministic proof runner

## Status
The package passes its shipped test suite and includes a runnable proof path.


## Stress determinism
```bash
python run_proof.py --stress 25
```

This runs the same locked corridor repeatedly and confirms:
- one stable judgment-against-boundary hash
- one stable cross-binding hash
- one stable outcome
- positive replay always matches

Note: receipt identity may vary per run if receipt IDs are generated per commit. The stress gate measures stable judgment binding, not accidental UUID reuse.

## Machine-readable report
```bash
python run_proof.py --output proof_output.json --quiet
```

This writes a structured proof report for automation and release checks.
>>>>>>> b875dc8 (Integrate Terry full runtime build into execution boundary repo)
