import json
from pathlib import Path


APP_CONFIG_DIR = Path.home() / ".meys_lahuella"
APP_CONFIG_FILE = APP_CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "source_path": "C:\\Via\\Aplicacion",
    "destination_path": "",
    "last_page": 0,
    "last_username": "admin",
}


def load_settings():
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not APP_CONFIG_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        data = json.loads(APP_CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()

    settings = DEFAULT_SETTINGS.copy()
    settings.update({key: value for key, value in data.items() if key in settings})
    return settings


def save_settings(settings):
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = DEFAULT_SETTINGS.copy()
    data.update({key: value for key, value in settings.items() if key in DEFAULT_SETTINGS})
    APP_CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
