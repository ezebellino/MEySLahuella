import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.app.antena_services import (
    buscar_archivo_ini,
    editar_potencia,
    leer_configuracion,
)
from src.app.mover_services import find_and_move_files
from src.app.tag_services import (
    obtener_info_tags,
)
from backend.audit_event_store import append_audit_event, list_audit_events
from backend.host_store import create_host, delete_host, find_host, list_hosts, sanitize_host, update_host
from backend.host_topology_store import delete_host_topology, get_host_topology, update_host_topology
from backend.rotation_history_store import append_rotation_event, list_rotation_events
from backend.ssh_client import SSHDependencyError, SSHHostClient
from backend.windows_client import WindowsHostClient


class MoveFilesPayload(BaseModel):
    source_path: str
    destination_path: str


class PotenciaPayload(BaseModel):
    potencia: int = Field(ge=0, le=30)


class HostPayload(BaseModel):
    name: str
    address: str
    port: int = 445
    username: str
    password: str
    host_type: str = "windows"
    winrm_port: int = 5985
    base_path: str = r"C:\\"
    restart_command: str = "shutdown /r /t 5 /f"


class DiscoverPayload(BaseModel):
    subnet: str = "10.95.25.0/24"
    port: int = 445
    timeout: float = 0.35


class PathPayload(BaseModel):
    path: str


class UploadPayload(BaseModel):
    remote_path: str
    content: str


class DownloadPayload(BaseModel):
    remote_path: str


class CommandPayload(BaseModel):
    command: str


class CredentialCandidate(BaseModel):
    username: str
    password: str


class CredentialTestPayload(BaseModel):
    candidates: list[CredentialCandidate] = Field(default_factory=list)


class QuickCheckPayload(BaseModel):
    include_auth: bool = True


class CredentialRotatePayload(BaseModel):
    username: str
    password: str
    verify: bool = True
    rollback_on_fail: bool = True


class RotationHistoryQuery(BaseModel):
    host_id: str | None = None
    limit: int = 100


class TopologyDevicePayload(BaseModel):
    key: str
    label: str
    port: str = ""
    ip: str = ""
    hostname: str = ""
    status: str = "unknown"
    notes: str = ""


class HostTopologyPayload(BaseModel):
    switch_name: str = "Switch principal"
    switch_ip: str = ""
    switch_model: str = ""
    switch_location: str = ""
    notes: str = ""
    devices: list[TopologyDevicePayload] = Field(default_factory=list)


app = FastAPI(title="Sistemas La Huella API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_local_ip() -> str:
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except OSError:
        return "No disponible"


def _is_port_open(ip: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def _append_audit(
    event_type: str,
    status: str,
    message: str,
    host: dict[str, Any] | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    event: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "status": status,
        "message": message,
    }
    if host:
        event["host_id"] = host.get("id")
        event["host_name"] = host.get("name")
        event["host_address"] = host.get("address")
    if details:
        event["details"] = details
    append_audit_event(event)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/system/info")
def system_info() -> dict[str, str]:
    hostname = socket.gethostname()
    return {
        "hostname": hostname,
        "ip": get_local_ip(),
        "target_server_dns": "srvlahuella.lahuella.local",
        "target_server_ip": "192.168.2.10",
        "updated_subnet": "10.95.25.0/24",
    }


@app.get("/api/antenna")
def antenna_data() -> dict[str, str]:
    try:
        archivo_ini = buscar_archivo_ini()
        remote_host, potencia = leer_configuracion(archivo_ini)
        return {"remote_host": remote_host, "potencia": potencia}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.put("/api/antenna/potencia")
def antenna_update(payload: PotenciaPayload) -> dict[str, str]:
    try:
        archivo_ini = buscar_archivo_ini()
        editar_potencia(archivo_ini, str(payload.potencia))
        _append_audit(
            event_type="antenna_potencia_update",
            status="ok",
            message=f"Potencia actualizada a {payload.potencia}",
            details={"potencia": payload.potencia},
        )
        return {"status": "ok", "potencia": str(payload.potencia)}
    except Exception as exc:
        _append_audit(
            event_type="antenna_potencia_update",
            status="error",
            message="Error al actualizar potencia",
            details={"error": str(exc)},
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/files/move")
def files_move(payload: MoveFilesPayload) -> dict[str, Any]:
    try:
        final_folder = find_and_move_files(payload.source_path, payload.destination_path)
        _append_audit(
            event_type="files_move",
            status="ok" if bool(final_folder) else "warning",
            message="Movimiento de archivos .dat ejecutado",
            details={
                "source_path": payload.source_path,
                "destination_path": payload.destination_path,
                "final_folder": str(final_folder) if final_folder else None,
                "moved": bool(final_folder),
            },
        )
        return {"moved": bool(final_folder), "final_folder": str(final_folder) if final_folder else None}
    except Exception as exc:
        _append_audit(
            event_type="files_move",
            status="error",
            message="Error al mover archivos .dat",
            details={"error": str(exc)},
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/tags")
def tags_data() -> dict[str, Any]:
    return {"items": obtener_info_tags()}


@app.get("/api/hosts")
def hosts_list() -> dict[str, Any]:
    return {"items": [sanitize_host(host) for host in list_hosts()]}


@app.post("/api/hosts")
def hosts_create(payload: HostPayload) -> dict[str, Any]:
    host = create_host(payload.model_dump())
    _append_audit(
        event_type="host_create",
        status="ok",
        message="Host agregado",
        host=host,
        details={"host_type": host.get("host_type")},
    )
    return {"item": sanitize_host(host)}


@app.put("/api/hosts/{host_id}")
def hosts_update(host_id: str, payload: HostPayload) -> dict[str, Any]:
    host = update_host(host_id, payload.model_dump())
    if not host:
        raise HTTPException(status_code=404, detail="Host no encontrado")
    _append_audit(
        event_type="host_update",
        status="ok",
        message="Host actualizado",
        host=host,
        details={"host_type": host.get("host_type")},
    )
    return {"item": sanitize_host(host)}


@app.delete("/api/hosts/{host_id}")
def hosts_delete(host_id: str) -> dict[str, Any]:
    host = find_host(host_id)
    deleted = delete_host(host_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Host no encontrado")
    delete_host_topology(host_id)
    _append_audit(
        event_type="host_delete",
        status="ok",
        message="Host eliminado",
        host=host,
    )
    return {"deleted": True}


@app.get("/api/hosts/{host_id}/topology")
def host_topology_get(host_id: str) -> dict[str, Any]:
    host = _get_host_or_404(host_id)
    topology = get_host_topology(host_id, host_name=host.get("name", ""))
    return {"item": topology}


@app.put("/api/hosts/{host_id}/topology")
def host_topology_put(host_id: str, payload: HostTopologyPayload) -> dict[str, Any]:
    host = _get_host_or_404(host_id)
    item = update_host_topology(host_id, payload.model_dump(), host_name=host.get("name", ""))
    _append_audit(
        event_type="topology_update",
        status="ok",
        message="Topología de host actualizada",
        host=host,
    )
    return {"item": item}


@app.post("/api/hosts/discover")
def hosts_discover(payload: DiscoverPayload) -> dict[str, Any]:
    try:
        network = ipaddress.ip_network(payload.subnet, strict=False)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Subred inválida: {exc}") from exc

    discovered: list[dict[str, Any]] = []
    ips = [str(ip) for ip in network.hosts()]
    workers = min(128, max(16, len(ips)))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_is_port_open, ip, payload.port, payload.timeout): ip for ip in ips}
        for future in as_completed(futures):
            ip = futures[future]
            if future.result():
                discovered.append({"address": ip, "port": payload.port})

    known_addresses = {host["address"] for host in list_hosts()}
    for item in discovered:
        item["already_saved"] = item["address"] in known_addresses

    discovered.sort(key=lambda item: tuple(int(part) for part in item["address"].split(".")))
    _append_audit(
        event_type="hosts_discover",
        status="ok",
        message="Escaneo de red ejecutado",
        details={"subnet": payload.subnet, "port": payload.port, "count": len(discovered)},
    )
    return {"items": discovered, "count": len(discovered)}


def _get_host_or_404(host_id: str) -> dict[str, Any]:
    host = find_host(host_id)
    if not host:
        raise HTTPException(status_code=404, detail="Host no encontrado")
    return host


def _with_host_client(host_id: str, handler, event_type: str | None = None, success_message: str | None = None):
    host = _get_host_or_404(host_id)
    try:
        host_type = (host.get("host_type") or "linux").lower()
        client_cls = WindowsHostClient if host_type == "windows" else SSHHostClient
        with client_cls(host) as client:
            result = handler(client, host)
        if event_type:
            _append_audit(
                event_type=event_type,
                status="ok",
                message=success_message or event_type,
                host=host,
            )
        return result
    except SSHDependencyError as exc:
        if event_type:
            _append_audit(
                event_type=event_type,
                status="error",
                message=str(exc),
                host=host,
                details={"error": str(exc)},
            )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        if event_type:
            _append_audit(
                event_type=event_type,
                status="error",
                message=str(exc),
                host=host,
                details={"error": str(exc)},
            )
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _probe_credentials(host: dict[str, Any]) -> dict[str, Any]:
    try:
        host_type = (host.get("host_type") or "linux").lower()
        client_cls = WindowsHostClient if host_type == "windows" else SSHHostClient
        with client_cls(host):
            pass
        return {"success": True, "error": None}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _probe_tcp(address: str, port: int, timeout: float = 1.2) -> bool:
    try:
        with socket.create_connection((address, port), timeout=timeout):
            return True
    except OSError:
        return False


@app.post("/api/hosts/{host_id}/files/list")
def host_files_list(host_id: str, payload: PathPayload) -> dict[str, Any]:
    return _with_host_client(
        host_id,
        lambda client, _host: {"items": client.list_dir(payload.path)},
        event_type="host_files_list",
        success_message=f"Listado de archivos en {payload.path}",
    )


@app.post("/api/hosts/{host_id}/terminal/restart")
def host_terminal_restart(host_id: str) -> dict[str, Any]:
    def _restart(client: SSHHostClient, host: dict[str, Any]):
        result = client.restart_terminal(host.get("restart_command") or "echo 'No restart command configured'")
        return {"result": result}

    return _with_host_client(
        host_id,
        _restart,
        event_type="host_terminal_restart",
        success_message="Reinicio remoto solicitado",
    )


@app.post("/api/hosts/{host_id}/command")
def host_command(host_id: str, payload: CommandPayload) -> dict[str, Any]:
    return _with_host_client(
        host_id,
        lambda client, _host: {"result": client.run_command(payload.command)},
        event_type="host_command",
        success_message=f"Comando ejecutado: {payload.command[:80]}",
    )


@app.post("/api/hosts/{host_id}/transfer/upload-text")
def host_upload_text(host_id: str, payload: UploadPayload) -> dict[str, Any]:
    return _with_host_client(
        host_id,
        lambda client, _host: {"result": client.upload_text(payload.remote_path, payload.content)},
        event_type="host_upload_text",
        success_message=f"Texto enviado a {payload.remote_path}",
    )


@app.post("/api/hosts/{host_id}/transfer/download-text")
def host_download_text(host_id: str, payload: DownloadPayload) -> dict[str, Any]:
    return _with_host_client(
        host_id,
        lambda client, _host: {"result": client.download_text(payload.remote_path)},
        event_type="host_download_text",
        success_message=f"Texto descargado desde {payload.remote_path}",
    )


@app.post("/api/hosts/{host_id}/credentials/test")
def host_test_credentials(host_id: str, payload: CredentialTestPayload) -> dict[str, Any]:
    host = _get_host_or_404(host_id)
    candidates = payload.candidates or [
        CredentialCandidate(username=host["username"], password=host["password"])
    ]

    results: list[dict[str, Any]] = []
    for candidate in candidates:
        probe_host = dict(host)
        probe_host["username"] = candidate.username
        probe_host["password"] = candidate.password
        probe = _probe_credentials(probe_host)
        results.append(
            {
                "username": candidate.username,
                "success": probe["success"],
                "error": probe["error"],
            }
        )

    any_success = any(item["success"] for item in results)
    if any_success:
        winner = next(item for item in results if item["success"])
        winner_candidate = next(candidate for candidate in candidates if candidate.username == winner["username"])
        patch = dict(host)
        patch["username"] = winner["username"]
        patch["password"] = winner_candidate.password
        update_host(host_id, patch)

    _append_audit(
        event_type="host_credentials_test",
        status="ok" if any_success else "warning",
        message="Prueba de credenciales ejecutada",
        host=host,
        details={"tested": len(candidates), "any_success": any_success},
    )

    return {"items": results, "any_success": any_success}


@app.post("/api/hosts/{host_id}/quick-check")
def host_quick_check(host_id: str, payload: QuickCheckPayload) -> dict[str, Any]:
    host = _get_host_or_404(host_id)
    host_type = (host.get("host_type") or "linux").lower()

    smb_port = int(host.get("port", 445 if host_type == "windows" else 22))
    smb_open = _probe_tcp(host["address"], smb_port)
    winrm_port = int(host.get("winrm_port", 5985))
    winrm_open = _probe_tcp(host["address"], winrm_port) if host_type == "windows" else False

    auth_success = None
    auth_error = None
    if payload.include_auth:
        probe = _probe_credentials(host)
        auth_success = probe["success"]
        auth_error = probe["error"]

    return {
        "host_id": host_id,
        "address": host["address"],
        "host_type": host_type,
        "smb_port": smb_port,
        "smb_open": smb_open,
        "winrm_port": winrm_port,
        "winrm_open": winrm_open,
        "reachable": smb_open or winrm_open,
        "auth_success": auth_success,
        "auth_error": auth_error,
        "ready": bool((smb_open or winrm_open) and (auth_success is not False)),
    }


@app.post("/api/hosts/{host_id}/credentials/rotate")
def host_rotate_credentials(host_id: str, payload: CredentialRotatePayload) -> dict[str, Any]:
    host = _get_host_or_404(host_id)
    old_username = host.get("username", "")
    old_password = host.get("password", "")

    patch = dict(host)
    patch["username"] = payload.username
    patch["password"] = payload.password
    updated = update_host(host_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Host no encontrado")

    if not payload.verify:
        _append_audit(
            event_type="host_credentials_rotate",
            status="ok",
            message="Rotación de credenciales sin verificación",
            host=host,
            details={"new_username": payload.username, "verify": False},
        )
        append_rotation_event(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "host_id": host_id,
                "host_name": host.get("name"),
                "host_address": host.get("address"),
                "old_username": old_username,
                "new_username": payload.username,
                "success": True,
                "verified": False,
                "rolled_back": False,
                "error": None,
                "source": "dashboard",
            }
        )
        return {"updated": True, "verified": None, "success": True}

    probe = _probe_credentials(updated)
    if probe["success"]:
        _append_audit(
            event_type="host_credentials_rotate",
            status="ok",
            message="Rotación de credenciales verificada",
            host=host,
            details={"new_username": payload.username, "verify": True},
        )
        append_rotation_event(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "host_id": host_id,
                "host_name": host.get("name"),
                "host_address": host.get("address"),
                "old_username": old_username,
                "new_username": payload.username,
                "success": True,
                "verified": True,
                "rolled_back": False,
                "error": None,
                "source": "dashboard",
            }
        )
        return {"updated": True, "verified": True, "success": True, "error": None}

    if payload.rollback_on_fail:
        _append_audit(
            event_type="host_credentials_rotate",
            status="error",
            message="Rotación fallida con rollback",
            host=host,
            details={"new_username": payload.username, "error": probe["error"], "rolled_back": True},
        )
        rollback = dict(updated)
        rollback["username"] = old_username
        rollback["password"] = old_password
        update_host(host_id, rollback)
        append_rotation_event(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "host_id": host_id,
                "host_name": host.get("name"),
                "host_address": host.get("address"),
                "old_username": old_username,
                "new_username": payload.username,
                "success": False,
                "verified": True,
                "rolled_back": True,
                "error": probe["error"],
                "source": "dashboard",
            }
        )
        return {
            "updated": False,
            "verified": False,
            "success": False,
            "rolled_back": True,
            "error": probe["error"],
        }

    _append_audit(
        event_type="host_credentials_rotate",
        status="error",
        message="Rotación fallida sin rollback",
        host=host,
        details={"new_username": payload.username, "error": probe["error"], "rolled_back": False},
    )
    append_rotation_event(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "host_id": host_id,
            "host_name": host.get("name"),
            "host_address": host.get("address"),
            "old_username": old_username,
            "new_username": payload.username,
            "success": False,
            "verified": True,
            "rolled_back": False,
            "error": probe["error"],
            "source": "dashboard",
        }
    )
    return {
        "updated": True,
        "verified": False,
        "success": False,
        "rolled_back": False,
        "error": probe["error"],
    }


@app.get("/api/credentials/rotation-history")
def get_rotation_history(host_id: str | None = None, limit: int = 100) -> dict[str, Any]:
    items = list_rotation_events(host_id=host_id, limit=limit)
    return {"items": items}


@app.get("/api/audit/events")
def get_audit_events(
    host_id: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 200,
) -> dict[str, Any]:
    items = list_audit_events(
        host_id=host_id,
        event_type=event_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )
    return {"items": items}
