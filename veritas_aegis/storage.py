
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from .util import sha256_obj


class JsonStore:
    """
    Small append-only JSON store.

    Regular objects live as one file per key.
    Ledgers live as:
      namespace/_index.json            -> ordered metadata only
      namespace/records/<hash>.json    -> one record per entry

    This avoids rewriting one giant ledger file on every append and lets
    callers deduplicate by a stable unique key when needed.
    """

    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _ns(self, namespace: str) -> Path:
        path = self.root / namespace
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _ledger_index_path(self, namespace: str) -> Path:
        return self._ns(namespace) / "_index.json"

    def _ledger_records_dir(self, namespace: str) -> Path:
        path = self._ns(namespace) / "records"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        return json.loads(path.read_text())

    def put(self, namespace: str, key: str, value: Dict[str, Any]) -> None:
        (self._ns(namespace) / f"{key}.json").write_text(json.dumps(value, indent=2, sort_keys=True))

    def get(self, namespace: str, key: str) -> Optional[Dict[str, Any]]:
        path = self._ns(namespace) / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def append(self, namespace: str, value: Dict[str, Any], *, unique_key: Optional[str] = None) -> Dict[str, Any]:
        index_path = self._ledger_index_path(namespace)
        index: List[Dict[str, Any]] = self._read_json(index_path, [])

        if unique_key is not None:
            for meta in index:
                if meta.get("unique_key") == unique_key:
                    record_path = self._ledger_records_dir(namespace) / f"{meta['record_hash']}.json"
                    return self._read_json(record_path, {})

        previous_record_hash = index[-1]["record_hash"] if index else None
        entry = dict(value)
        entry["previous_record_hash"] = previous_record_hash
        entry["record_hash"] = sha256_obj({"previous_record_hash": previous_record_hash, "value": value})

        record_path = self._ledger_records_dir(namespace) / f"{entry['record_hash']}.json"
        record_path.write_text(json.dumps(entry, indent=2, sort_keys=True))

        index.append({
            "record_hash": entry["record_hash"],
            "previous_record_hash": previous_record_hash,
            "unique_key": unique_key,
        })
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True))
        return entry

    def ledger(self, namespace: str) -> List[Dict[str, Any]]:
        index = self._read_json(self._ledger_index_path(namespace), [])
        records_dir = self._ledger_records_dir(namespace)
        result: List[Dict[str, Any]] = []
        for meta in index:
            record_path = records_dir / f"{meta['record_hash']}.json"
            if record_path.exists():
                result.append(json.loads(record_path.read_text()))
        return result
