# Public Proof Access

This repository can be deployed as a public proof surface.

## Endpoints
- GET /health
- POST /evaluate
- POST /evaluate/proof

## Example payloads
- demo_healthcare.json
- demo_maritime.json

## Expected proof behavior
- Healthcare -> EXECUTE / COMMITTED / proof_replay_equivalent = true
- Maritime -> ESCALATE / ESCALATED / proof_replay_equivalent = true
