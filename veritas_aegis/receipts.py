
from __future__ import annotations
from typing import Dict
from .contracts import DecisionReceipt
from .util import sha256_obj

def lawful_context_material(*, receipt: DecisionReceipt) -> Dict[str, object]:
    return {
        "judgment_context": receipt.judgment_context.to_dict(),
        "standing_judgment": receipt.standing_judgment.to_dict(),
        "continuation_judgment": receipt.continuation_judgment.to_dict(),
        "outcome_judgment": receipt.outcome_judgment.to_dict(),
        "preservation_record": receipt.preservation_record.to_dict(),
    }

def lawful_context_proof(material: Dict[str, object]) -> str:
    return sha256_obj(material)

def verify_lawful_context(receipt: DecisionReceipt) -> bool:
    return lawful_context_proof(lawful_context_material(receipt=receipt)) == receipt.lawful_context_proof
