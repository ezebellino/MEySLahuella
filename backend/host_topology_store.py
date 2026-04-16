import json
import threading
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TOPOLOGY_FILE = DATA_DIR / "host_topologies.json"
LOCK = threading.Lock()

DEVICE_TEMPLATES = [
    {"key": "antenna", "label": "Antena TelePASE"},
    {"key": "pc", "label": "PC de vía"},
    {"key": "printer", "label": "Impresora"},
    {"key": "camera_surveillance", "label": "Cámara vigilancia"},
    {"key": "camera_ocr", "label": "Cámara OCR"}
]


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not TOPOLOGY_FILE.exists():
        TOPOLOGY_FILE.write_text("{}", encoding="utf-8")


def _read_all() -> dict[str, Any]:
    _ensure_store()
    raw = TOPOLOGY_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _write_all(data: dict[str, Any]) -> None:
    _ensure_store()
    TOPOLOGY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _normalize_devices(devices: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    by_key = {}
    for item in devices or []:
        key = str(item.get("key", "")).strip()
        if not key:
            continue
        by_key[key] = {
            "key": key,
            "label": str(item.get("label", "")).strip() or key,
            "port": str(item.get("port", "")).strip(),
            "ip": str(item.get("ip", "")).strip(),
            "hostname": str(item.get("hostname", "")).strip(),
            "status": str(item.get("status", "unknown")).strip() or "unknown",
            "notes": str(item.get("notes", "")).strip(),
        }

    normalized: list[dict[str, Any]] = []
    for template in DEVICE_TEMPLATES:
        key = template["key"]
        existing = by_key.get(key)
        if existing:
            existing["label"] = existing["label"] or template["label"]
            normalized.append(existing)
        else:
            normalized.append(
                {
                    "key": key,
                    "label": template["label"],
                    "port": "",
                    "ip": "",
                    "hostname": "",
                    "status": "unknown",
                    "notes": "",
                }
            )
    return normalized


def _default_topology(host_name: str = "") -> dict[str, Any]:
    switch_name = "Switch principal"
    if host_name:
        switch_name = f"Switch {host_name}"
    return {
        "switch_name": switch_name,
        "switch_ip": "",
        "switch_model": "",
        "switch_location": "",
        "notes": "",
        "devices": _normalize_devices([]),
    }


def get_host_topology(host_id: str, host_name: str = "") -> dict[str, Any]:
    with LOCK:
        all_data = _read_all()
        current = all_data.get(host_id)
        if not isinstance(current, dict):
            return _default_topology(host_name)
        return {
            "switch_name": str(current.get("switch_name", "")).strip() or _default_topology(host_name)["switch_name"],
            "switch_ip": str(current.get("switch_ip", "")).strip(),
            "switch_model": str(current.get("switch_model", "")).strip(),
            "switch_location": str(current.get("switch_location", "")).strip(),
            "notes": str(current.get("notes", "")).strip(),
            "devices": _normalize_devices(current.get("devices")),
        }


def update_host_topology(host_id: str, payload: dict[str, Any], host_name: str = "") -> dict[str, Any]:
    with LOCK:
        all_data = _read_all()
        normalized = {
            "switch_name": str(payload.get("switch_name", "")).strip() or _default_topology(host_name)["switch_name"],
            "switch_ip": str(payload.get("switch_ip", "")).strip(),
            "switch_model": str(payload.get("switch_model", "")).strip(),
            "switch_location": str(payload.get("switch_location", "")).strip(),
            "notes": str(payload.get("notes", "")).strip(),
            "devices": _normalize_devices(payload.get("devices")),
        }
        all_data[host_id] = normalized
        _write_all(all_data)
        return normalized


def delete_host_topology(host_id: str) -> None:
    with LOCK:
        all_data = _read_all()
        if host_id in all_data:
            all_data.pop(host_id, None)
            _write_all(all_data)
