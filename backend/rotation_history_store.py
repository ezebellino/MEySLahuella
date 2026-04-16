import json
import threading
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "credential_rotation_history.json"
LOCK = threading.Lock()


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def _read() -> list[dict[str, Any]]:
    _ensure_store()
    raw = HISTORY_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _write(items: list[dict[str, Any]]) -> None:
    _ensure_store()
    HISTORY_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def append_rotation_event(event: dict[str, Any], max_items: int = 2000) -> None:
    with LOCK:
        items = _read()
        items.append(event)
        if len(items) > max_items:
            items = items[-max_items:]
        _write(items)


def list_rotation_events(host_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    with LOCK:
        items = _read()
        if host_id:
            items = [x for x in items if x.get("host_id") == host_id]
        items = sorted(items, key=lambda x: x.get("timestamp", ""), reverse=True)
        return items[: max(1, min(limit, 500))]

