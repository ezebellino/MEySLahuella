import argparse
import os
import sys
from pathlib import Path

import uvicorn


def resolve_root(cli_root: str | None) -> Path:
    if cli_root:
        return Path(cli_root).resolve()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    root = resolve_root(args.root)
    os.chdir(root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from api_server import app

    uvicorn.run(app, host=args.host, port=args.port, access_log=False)


if __name__ == "__main__":
    main()
