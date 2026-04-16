import json
import threading
import uuid
from pathlib import Path
from typing import Any

from backend.secret_store import protect_text, unprotect_text


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HOST_FILE = DATA_DIR / "hosts.json"
LOCK = threading.Lock()


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HOST_FILE.exists():
        HOST_FILE.write_text("[]", encoding="utf-8")


def _read_hosts() -> list[dict[str, Any]]:
    _ensure_store()
    raw = HOST_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        hosts = data if isinstance(data, list) else []
        changed = False
        normalized: list[dict[str, Any]] = []
        for host in hosts:
            item = dict(host)
            if "password_enc" not in item:
                legacy_password = item.get("password", "")
                item["password_enc"] = protect_text(str(legacy_password))
                item.pop("password", None)
                changed = True
            if "host_type" not in item:
                inferred_port = int(item.get("port", 22))
                item["host_type"] = "windows" if inferred_port == 445 else "linux"
                changed = True
            if "winrm_port" not in item:
                item["winrm_port"] = 5985
                changed = True
            normalized.append(item)
        if changed:
            _write_hosts(normalized)
        return normalized
    except json.JSONDecodeError:
        return []


def _write_hosts(hosts: list[dict[str, Any]]) -> None:
    _ensure_store()
    HOST_FILE.write_text(json.dumps(hosts, indent=2, ensure_ascii=False), encoding="utf-8")


def _materialize_host(host: dict[str, Any]) -> dict[str, Any]:
    item = dict(host)
    encrypted = item.get("password_enc", "")
    item["password"] = unprotect_text(str(encrypted))
    item.pop("password_enc", None)
    return item


def list_hosts() -> list[dict[str, Any]]:
    with LOCK:
        return [_materialize_host(host) for host in _read_hosts()]


def find_host(host_id: str) -> dict[str, Any] | None:
    hosts = list_hosts()
    for host in hosts:
        if host.get("id") == host_id:
            return host
    return None


def create_host(payload: dict[str, Any]) -> dict[str, Any]:
    with LOCK:
        hosts = _read_hosts()
        host_type = payload.get("host_type", "linux")
        default_base_path = r"C:\\" if host_type == "windows" else "/"
        default_restart = (
            "shutdown /r /t 5 /f"
            if host_type == "windows"
            else "sudo systemctl restart ssh || sudo service ssh restart"
        )
        host = {
            "id": str(uuid.uuid4()),
            "name": payload["name"],
            "address": payload["address"],
            "port": int(payload.get("port", 22)),
            "username": payload["username"],
            "password_enc": protect_text(str(payload["password"])),
            "host_type": host_type,
            "winrm_port": int(payload.get("winrm_port", 5985)),
            "base_path": payload.get("base_path", default_base_path),
            "restart_command": payload.get("restart_command", default_restart),
        }
        hosts.append(host)
        _write_hosts(hosts)
        return _materialize_host(host)


def update_host(host_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    with LOCK:
        hosts = _read_hosts()
        for host in hosts:
            if host.get("id") == host_id:
                host_type = payload.get("host_type", host.get("host_type", "linux"))
                default_base_path = r"C:\\" if host_type == "windows" else "/"
                default_restart = (
                    "shutdown /r /t 5 /f"
                    if host_type == "windows"
                    else "sudo systemctl restart ssh || sudo service ssh restart"
                )
                host["name"] = payload["name"]
                host["address"] = payload["address"]
                host["port"] = int(payload.get("port", 22))
                host["username"] = payload["username"]
                host["host_type"] = host_type
                host["winrm_port"] = int(payload.get("winrm_port", host.get("winrm_port", 5985)))
                incoming_password = payload.get("password")
                if incoming_password:
                    host["password_enc"] = protect_text(str(incoming_password))
                host["base_path"] = payload.get("base_path", default_base_path)
                host["restart_command"] = payload.get("restart_command", default_restart)
                _write_hosts(hosts)
                return _materialize_host(host)
    return None


def delete_host(host_id: str) -> bool:
    with LOCK:
        hosts = _read_hosts()
        original_len = len(hosts)
        hosts = [host for host in hosts if host.get("id") != host_id]
        if len(hosts) == original_len:
            return False
        _write_hosts(hosts)
        return True


def sanitize_host(host: dict[str, Any]) -> dict[str, Any]:
    masked = dict(host)
    masked["password"] = "********"
    return masked
