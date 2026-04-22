# Veritas CordovaOS Demo — 60 Second Run

## 1. Start API
./run_api_stdlib.sh

## 2. Health check
curl http://127.0.0.1:8001/health

## 3. Allowed execution (Healthcare)
curl -X POST http://127.0.0.1:8001/evaluate/proof \
  -H "Content-Type: application/json" \
  -d @demo_healthcare.json

Expected:
- decision: EXECUTE
- commit_result: COMMITTED
- proof_replay_equivalent: true

## 4. Constrained execution (Maritime)
curl -X POST http://127.0.0.1:8001/evaluate/proof \
  -H "Content-Type: application/json" \
  -d @demo_maritime.json

Expected:
- decision: ESCALATE
- commit_result: ESCALATED
- proof_replay_equivalent: true

## What this proves

Execution is not allowed by default.

Each state transition must:
- satisfy admissibility
- produce a deterministic receipt
- replay to the same decision
