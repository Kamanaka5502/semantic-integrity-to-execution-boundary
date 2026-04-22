
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from .util import sha256_obj

@dataclass(frozen=True)
class StateSnapshot:
    state_ref: str
    state_hash: str
    entity_id: str
    current_status: str
    attributes: Dict[str, Any]
    open_burdens: List[Dict[str, Any]]
    continuity_chain_head: Optional[str]
    continuity_debt: List[Dict[str, Any]]
    resolved_at: str
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def snapshot_from_record(state_ref: str, record: Dict[str, Any], resolved_at: str) -> StateSnapshot:
    normalized = {
        "entity_id": record["entity_id"],
        "current_status": record["current_status"],
        "attributes": record.get("attributes", {}),
        "open_burdens": list(record.get("open_burdens", [])),
        "continuity_chain_head": record.get("continuity_chain_head"),
        "continuity_debt": list(record.get("continuity_debt", [])),
    }
    return StateSnapshot(
        state_ref=state_ref,
        state_hash=sha256_obj(normalized),
        entity_id=normalized["entity_id"],
        current_status=normalized["current_status"],
        attributes=normalized["attributes"],
        open_burdens=normalized["open_burdens"],
        continuity_chain_head=normalized["continuity_chain_head"],
        continuity_debt=normalized["continuity_debt"],
        resolved_at=resolved_at,
    )
