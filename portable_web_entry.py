import argparse
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


def resolve_root(cli_root: str | None) -> Path:
    if cli_root:
        return Path(cli_root).resolve()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


class SpaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        relative = parsed.path.lstrip("/")
        requested = Path(self.directory, relative)

        if parsed.path in ("", "/") or requested.exists():
            super().do_GET()
            return

        self.path = "/index.html"
        super().do_GET()

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5173)
    args = parser.parse_args()

    root = resolve_root(args.root)
    frontend_dir = root / "frontend"
    if not frontend_dir.exists():
        raise FileNotFoundError(f"No se encontro la carpeta frontend en {root}")

    os.chdir(root)
    server = ThreadingHTTPServer(
        (args.host, args.port),
        lambda *handler_args, **handler_kwargs: SpaHandler(
            *handler_args,
            directory=str(frontend_dir),
            **handler_kwargs,
        ),
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
