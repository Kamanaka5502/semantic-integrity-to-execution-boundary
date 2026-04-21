from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
from .util import sha256_obj, sign_material

@dataclass(frozen=True)
class GoverningBasis:
    basis_id: str
    version: str
    rules: Dict[str, Any]
    basis_hash: str
    lineage_hash: str
    parent_basis_hash: Optional[str]
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def signature_material(*, basis_id: str, version: str, rules: Dict[str, Any], basis_hash: str, lineage_hash: str, parent_basis_hash: Optional[str]) -> Dict[str, Any]:
        return {
            "basis_id": basis_id,
            "version": version,
            "basis_hash": basis_hash,
            "lineage_hash": lineage_hash,
            "parent_basis_hash": parent_basis_hash,
            "rules": rules,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], secret: str) -> "GoverningBasis":
        basis_id = data["basis_id"]
        version = data["version"]
        rules = data["rules"]
        parent_basis_hash = data.get("parent_basis_hash")
        basis_hash = data.get("basis_hash") or sha256_obj({"basis_id": basis_id, "version": version, "rules": rules})
        lineage_hash = data.get("lineage_hash") or sha256_obj({"basis_hash": basis_hash, "parent_basis_hash": parent_basis_hash})
        signature = data.get("signature") or sign_material(secret, cls.signature_material(
            basis_id=basis_id, version=version, rules=rules,
            basis_hash=basis_hash, lineage_hash=lineage_hash, parent_basis_hash=parent_basis_hash,
        ))
        return cls(basis_id=basis_id, version=version, rules=rules, basis_hash=basis_hash, lineage_hash=lineage_hash, parent_basis_hash=parent_basis_hash, signature=signature)
