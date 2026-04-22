from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.adapter import from_sdc
from app.admissibility import evaluate_attempt
from app.commit_gate import enforce
from app.receipt import create_receipt, create_proof_receipt
from app.replay import replay


app = FastAPI(
    title="Veritas CordovaOS Execution API",
    version="0.1.0",
    description="Bounded execution boundary API with receipts and replay."
)


class EvaluateRequest(BaseModel):
    corridor: str = Field(..., description="healthcare | registry | maritime | education")
    action: str = Field(..., description="Corridor action")
    user: str = Field(..., description="Actor identifier")
    authority: int = Field(..., ge=0, description="Authority level")
    prior_state: str = Field(default="UNKNOWN", description="Prior workflow state")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Corridor-specific payload")


@app.get("/health")
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "veritas-cordovaos-api",
        "version": "0.1.0"
    }


@app.post("/evaluate")
def evaluate(req: EvaluateRequest) -> Dict[str, Any]:
    try:
        attempt = from_sdc(req.model_dump())
        result = evaluate_attempt(attempt)
        commit_result = enforce(result.decision)
        runtime_receipt = create_receipt(attempt, result)
        replay_result = replay(attempt)

        return {
            "attempt": {
                "corridor": attempt.corridor,
                "action": attempt.action,
                "user": attempt.user,
                "authority_level": attempt.authority_level,
                "prior_state": attempt.prior_state,
                "payload": attempt.payload,
            },
            "evaluation": {
                "decision": result.decision.value,
                "reason": result.reason,
                "checks": result.checks,
            },
            "commit_result": commit_result,
            "runtime_receipt": runtime_receipt.to_dict(),
            "replay": {
                "decision": replay_result.decision.value,
                "reason": replay_result.reason,
                "checks": replay_result.checks,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/evaluate/proof")
def evaluate_proof(req: EvaluateRequest) -> Dict[str, Any]:
    try:
        attempt = from_sdc(req.model_dump())
        result = evaluate_attempt(attempt)
        commit_result = enforce(result.decision)

        proof_receipt = create_proof_receipt(attempt, result)
        replay_result = replay(attempt)
        replay_proof_receipt = create_proof_receipt(attempt, replay_result)

        return {
            "attempt": {
                "corridor": attempt.corridor,
                "action": attempt.action,
                "user": attempt.user,
                "authority_level": attempt.authority_level,
                "prior_state": attempt.prior_state,
                "payload": attempt.payload,
            },
            "evaluation": {
                "decision": result.decision.value,
                "reason": result.reason,
                "checks": result.checks,
            },
            "commit_result": commit_result,
            "proof_receipt": proof_receipt.to_dict(),
            "replay": {
                "decision": replay_result.decision.value,
                "reason": replay_result.reason,
                "checks": replay_result.checks,
            },
            "proof_replay_equivalent": (
                proof_receipt.receipt_id == replay_proof_receipt.receipt_id
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
