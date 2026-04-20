# Veritas Aegis — Execution Boundary Demo

**Authors:** Samantha Revita, Terry Snyder
**Organization:** Veritas Aegis

# Semantic Integrity to Execution Boundary

> Semantic integrity preserves meaning. This layer determines whether that meaning is allowed to bind into action.

## Core Idea

Modern systems fail in two places:

### Gate 1 — Semantic Gate
Is the input meaningful and trustworthy?

### Gate 2 — Execution Gate
Even if meaning is correct, is execution still admissible under current state, authority, policy, and risk?

This repo shows why both gates are required.

---

## Run the demo

```bash
git clone https://github.com/Kamanaka5502/semantic-integrity-to-execution-boundary.git
cd semantic-integrity-to-execution-boundary
python example_run.py

