
from __future__ import annotations
import hashlib, hmac, json
from typing import Any, Dict

def _stable(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(_stable(obj)).hexdigest()

def sign_material(secret: str, obj: Any) -> str:
    return hmac.new(secret.encode(), _stable(obj), hashlib.sha256).hexdigest()

def verify_signature(secret: str, obj: Any, signature: str) -> bool:
    return hmac.compare_digest(sign_material(secret, obj), signature)
