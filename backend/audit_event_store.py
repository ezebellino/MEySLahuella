import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AUDIT_FILE = DATA_DIR / "audit_events.json"
LOCK = threading.Lock()


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not AUDIT_FILE.exists():
        AUDIT_FILE.write_text("[]", encoding="utf-8")


def _read() -> list[dict[str, Any]]:
    _ensure_store()
    raw = AUDIT_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _write(items: list[dict[str, Any]]) -> None:
    _ensure_store()
    AUDIT_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def append_audit_event(event: dict[str, Any], max_items: int = 10000) -> None:
    with LOCK:
        items = _read()
        items.append(event)
        if len(items) > max_items:
            items = items[-max_items:]
        _write(items)


def list_audit_events(
    host_id: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    with LOCK:
        items = _read()
        dt_from = _parse_iso(date_from)
        dt_to = _parse_iso(date_to)

        filtered: list[dict[str, Any]] = []
        for item in items:
            if host_id and item.get("host_id") != host_id:
                continue
            if event_type and item.get("event_type") != event_type:
                continue
            if status and item.get("status") != status:
                continue

            ts = _parse_iso(item.get("timestamp"))
            if dt_from and (not ts or ts < dt_from):
                continue
            if dt_to and (not ts or ts > dt_to):
                continue

            filtered.append(item)

        filtered = sorted(filtered, key=lambda x: x.get("timestamp", ""), reverse=True)
        return filtered[: max(1, min(limit, 2000))]
