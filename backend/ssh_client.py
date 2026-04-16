import stat
from datetime import datetime
from typing import Any


class SSHDependencyError(RuntimeError):
    pass


class SSHHostClient:
    def __init__(self, host: dict[str, Any]):
        self.host = host
        self.client = None

    def __enter__(self):
        try:
            import paramiko
        except ImportError as exc:
            raise SSHDependencyError(
                "Falta dependencia 'paramiko'. Instalar con: pip install paramiko"
            ) from exc

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.host["address"],
            username=self.host["username"],
            password=self.host["password"],
            port=int(self.host.get("port", 22)),
            timeout=8,
            look_for_keys=False,
            allow_agent=False,
        )
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.client:
            self.client.close()

    def list_dir(self, path: str) -> list[dict[str, Any]]:
        with self.client.open_sftp() as sftp:
            entries = sftp.listdir_attr(path)
            items: list[dict[str, Any]] = []
            for entry in entries:
                is_dir = stat.S_ISDIR(entry.st_mode)
                items.append(
                    {
                        "name": entry.filename,
                        "type": "dir" if is_dir else "file",
                        "size": entry.st_size,
                        "modified": datetime.fromtimestamp(entry.st_mtime).isoformat(),
                    }
                )
            return sorted(items, key=lambda item: (item["type"] != "dir", item["name"].lower()))

    def run_command(self, command: str, timeout: int = 15) -> dict[str, Any]:
        _, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="ignore")
        err = stderr.read().decode("utf-8", errors="ignore")
        code = stdout.channel.recv_exit_status()
        return {"command": command, "exit_code": code, "stdout": out, "stderr": err}

    def restart_terminal(self, restart_command: str) -> dict[str, Any]:
        return self.run_command(restart_command, timeout=25)

    def upload_text(self, remote_path: str, content: str) -> dict[str, Any]:
        with self.client.open_sftp() as sftp:
            with sftp.open(remote_path, "w") as remote_file:
                remote_file.write(content)
        return {"remote_path": remote_path, "bytes": len(content.encode("utf-8"))}

    def download_text(self, remote_path: str, max_bytes: int = 300_000) -> dict[str, Any]:
        with self.client.open_sftp() as sftp:
            with sftp.open(remote_path, "r") as remote_file:
                content = remote_file.read(max_bytes).decode("utf-8", errors="ignore")
        return {"remote_path": remote_path, "content": content}

