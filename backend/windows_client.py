import json
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


class WindowsHostClient:
    def __init__(self, host: dict[str, Any]):
        self.host = host
        self.ipc_path = rf"\\{self.host['address']}\IPC$"
        self.connected = False

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._disconnect()

    def _run(self, args: list[str], timeout: int = 20) -> subprocess.CompletedProcess:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)

    def _connect(self) -> None:
        result = self._run(
            ["net", "use", self.ipc_path, f"/user:{self.host['username']}", self.host["password"]],
            timeout=15,
        )
        if result.returncode != 0 and "ya se ha iniciado sesión" not in result.stdout.lower():
            raise RuntimeError((result.stderr or result.stdout or "No se pudo conectar a SMB").strip())
        self.connected = True

    def _disconnect(self) -> None:
        if not self.connected:
            return
        self._run(["net", "use", self.ipc_path, "/delete", "/y"], timeout=10)
        self.connected = False

    def _to_unc(self, path: str) -> str:
        raw = path.strip()
        if raw.startswith("\\\\"):
            return raw
        if len(raw) >= 3 and raw[1:3] == ":\\":
            drive = raw[0].upper()
            tail = raw[3:].replace("/", "\\")
            return rf"\\{self.host['address']}\{drive}$\{tail}" if tail else rf"\\{self.host['address']}\{drive}$"
        base = (self.host.get("base_path") or r"C:\\").strip()
        if len(base) >= 3 and base[1:3] == ":\\":
            if raw.startswith("\\"):
                return self._to_unc(base[0:2] + raw)
            return self._to_unc(base.rstrip("\\") + "\\" + raw)
        return rf"\\{self.host['address']}\C$\{raw.lstrip('\\')}"

    def list_dir(self, path: str) -> list[dict[str, Any]]:
        unc = self._to_unc(path)
        safe_unc = unc.replace("'", "''")
        script = (
            "$ErrorActionPreference='Stop';"
            f"$items=Get-ChildItem -Force -LiteralPath '{safe_unc}' | "
            "Select-Object Name,@{n='type';e={if($_.PSIsContainer){'dir'}else{'file'}}},"
            "Length,@{n='modified';e={$_.LastWriteTime.ToString('s')}};"
            "$items | ConvertTo-Json -Depth 3"
        )
        result = self._run(["powershell", "-NoProfile", "-Command", script], timeout=25)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "Error listando archivos").strip())
        payload = result.stdout.strip() or "[]"
        parsed = json.loads(payload)
        items = parsed if isinstance(parsed, list) else ([parsed] if parsed else [])
        normalized: list[dict[str, Any]] = []
        for item in items:
            normalized.append(
                {
                    "name": item.get("Name") or item.get("name"),
                    "type": item.get("type", "file"),
                    "size": item.get("Length", item.get("size", 0)) or 0,
                    "modified": item.get("modified", ""),
                }
            )
        return normalized

    def run_command(self, command: str, timeout: int = 20) -> dict[str, Any]:
        winrm_port = int(self.host.get("winrm_port", 5985))
        target = f"{self.host['address']}:{winrm_port}"
        result = self._run(
            ["winrs", f"-r:{target}", f"-u:{self.host['username']}", f"-p:{self.host['password']}", command],
            timeout=timeout,
        )
        return {
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def restart_terminal(self, restart_command: str) -> dict[str, Any]:
        return self.run_command(restart_command or "shutdown /r /t 5 /f", timeout=30)

    def upload_text(self, remote_path: str, content: str) -> dict[str, Any]:
        unc = self._to_unc(remote_path)
        with NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".txt") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        copy_result = self._run(["cmd", "/c", "copy", "/Y", temp_path, unc], timeout=20)
        Path(temp_path).unlink(missing_ok=True)
        if copy_result.returncode != 0:
            raise RuntimeError((copy_result.stderr or copy_result.stdout or "Error subiendo archivo").strip())
        return {"remote_path": remote_path, "bytes": len(content.encode("utf-8"))}

    def download_text(self, remote_path: str, max_bytes: int = 300_000) -> dict[str, Any]:
        unc = self._to_unc(remote_path)
        safe_unc = unc.replace("'", "''")
        script = (
            "$ErrorActionPreference='Stop';"
            f"$raw=Get-Content -Raw -LiteralPath '{safe_unc}';"
            f"if($raw.Length -gt {max_bytes}){{$raw=$raw.Substring(0,{max_bytes})}};"
            "Write-Output $raw"
        )
        result = self._run(["powershell", "-NoProfile", "-Command", script], timeout=20)
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "Error descargando archivo").strip())
        return {"remote_path": remote_path, "content": result.stdout}

