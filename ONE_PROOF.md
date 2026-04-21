# One Proof

## What this shows

A validated instruction reaches the execution boundary.

Veritas decides whether it is allowed to become real.

---

## Run

    python run_proof.py

---

## Result

### Valid case
- SAFE_COMMIT
- replay matches

### Mutated case
- REFUSE_BLOCK
- replay mismatch

---

## Why it matters

- Same input → same result
- Mutation → provable failure
- Boundary is enforced, not described

---

This is execution control at the point where reality changes.
