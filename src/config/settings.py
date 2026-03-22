import json
from copy import deepcopy
from pathlib import Path


APP_CONFIG_DIR = Path.home() / ".meys_lahuella"
APP_CONFIG_FILE = APP_CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "ui": {
        "last_page": 0,
        "last_username": "admin",
    },
    "auth": {
        "username": "admin",
        "password": "1234",
    },
    "paths": {
        "source_path": "C:\\Via\\Aplicacion",
        "destination_path": "",
        "testeo_path": "C:\\Via\\Testeo\\Testeo.exe",
        "reader_test_path": "C:\\APPS\\ReaderTest.exe",
        "uip_reader_path": "C:\\Teste Antena\\UipReader01demomain.exe",
        "antenna_ini_dir": "C:\\Windows\\",
        "antenna_ini_name": "TciNumero.ini",
    },
    "tags": {
        "files": [
            "C:\\Via\\Aplicacion\\LMTAGS_AUBASA.DAT",
            "C:\\Via\\Aplicacion\\LMTAGSPAT_AUBASA.DAT",
        ],
    },
    "antenna": {
        "reader_test_vias": [51, 52, 53, 9, 10, 11],
        "uip_reader_vias": [54, 55, 7, 8],
    },
}


def _merge_dicts(base, overrides):
    merged = deepcopy(base)
    for key, value in overrides.items():
        if key not in merged:
            continue
        if isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_settings():
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not APP_CONFIG_FILE.exists():
        return deepcopy(DEFAULT_SETTINGS)

    try:
        data = json.loads(APP_CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return deepcopy(DEFAULT_SETTINGS)

    return _merge_dicts(DEFAULT_SETTINGS, data)


def save_settings(settings):
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = _merge_dicts(DEFAULT_SETTINGS, settings)
    APP_CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
