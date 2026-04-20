# Veritas Execution Gate — Demo

> A thin layer that decides if an action is allowed to become real — before it executes.

## What this shows

Given:
- a proposed action
- current system state
- authority + policy conditions

The system decides:

- EXECUTE -> if admissible
- REDIRECT -> if a safer valid path exists
- ESCALATE -> if human input is required
- REFUSE -> if no lawful path exists

## Why this matters

Most systems log decisions after execution.

This enforces:

no execution unless conditions are valid at commit.

## Where this fits

This can sit in front of any system that produces actions:

- AI agents proposing actions
- workflow automation tools
- API-triggered operations
- internal decision engines

Instead of trusting the output, every action passes through a gate:

- validate current state
- validate authority
- validate constraints
- decide if execution is allowed

This makes execution fail-closed instead of fail-open.

## Demo Flow

Input -> Evaluation -> Decision -> Receipt -> Replay

Same input -> same result

## Example

### Input

action = "DEPLOY_CHANGE"

state = {
    "risk": 8,
    "ready": True
}

authority = {
    "valid": True
}

### Evaluation

def evaluate(action, state, authority):
    if not authority["valid"]:
        return "REFUSE"

    if state["risk"] > 7:
        return "ESCALATE"

    if not state["ready"]:
        return "REDIRECT"

    return "EXECUTE"

### Output

{
  "decision": "ESCALATE",
  "reason": "Risk threshold exceeded",
  "timestamp": "2026-04-20T12:00:00Z"
}

## Key Point

The system does not execute because it has a proposal.

It executes only if the proposal is valid at the moment of commit.
