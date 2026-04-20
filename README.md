# Semantic Integrity to Execution Boundary

> Semantic integrity preserves meaning. This layer determines whether that meaning is allowed to bind into action.

## Core Idea

Modern systems fail in two different places:

### Gate 1 — Semantic Gate
Is the input meaningful, complete, and trustworthy enough to reason from?

### Gate 2 — Execution Gate
Even if the meaning is correct, is execution still admissible under current state, authority, policy, and risk?

This repository demonstrates why both gates are required.

A system can preserve meaning and still fail operationally if it executes under the wrong conditions.

---

## Why this matters

Semantic integrity is necessary, but not sufficient.

A system may still produce inadmissible action because:

- state changed after interpretation
- authority is no longer valid
- policy or corridor constraints shifted
- risk exceeds threshold
- runtime conditions are no longer satisfied

That means the full chain has to be:

**meaning -> admissibility -> execution**

Without semantic integrity, systems reason from ambiguity.  
Without execution gating, systems act when they should not.

---

## What this demo shows

Given:
- a proposed action
- semantic context quality
- current system state
- authority conditions

the system decides, before execution:

- EXECUTE
- REDIRECT
- ESCALATE
- REFUSE

---

## Gate Model

### Semantic Gate
Checks whether the proposal is based on usable meaning.

Examples:
- context complete enough
- data not ambiguous
- relevant records present
- interpretation confidence acceptable

### Execution Gate
Checks whether the proposed action is still allowed to become real.

Examples:
- authority valid
- state valid
- risk within threshold
- execution readiness satisfied

---

## Why teams focused on semantic integrity still need this layer

Semantic integrity answers:

**"Is the system reasoning from correct meaning?"**

Execution gating answers:

**"Even if the meaning is correct, is execution still valid now?"**

This does not compete with semantic integrity.  
It completes it.

---

## Demo Flow

Input -> Semantic Gate -> Execution Gate -> Decision -> Receipt

Same input -> same result

---

## Example Logic

### Input

action = "APPROVE_PRODUCTION_DEPLOYMENT"

semantic = {
    "context_complete": True,
    "ambiguity_low": True,
    "confidence": 0.91
}

state = {
    "risk": 8,
    "ready": True
}

authority = {
    "valid": True
}

### Output

{
  "decision": "ESCALATE",
  "reason": "Execution risk threshold exceeded",
  "timestamp": "2026-04-20T12:00:00+00:00"
}

---

## Core Claim

This is not a logging layer.  
This is not post-hoc review.

This is a two-gate enforcement model.

The system does not execute because it has a proposal.

It executes only if:
1. the proposal is semantically trustworthy enough to reason from
2. the proposal remains admissible at commit
