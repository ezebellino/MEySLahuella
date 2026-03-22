from datetime import datetime
from pathlib import Path

from src.config.settings import load_settings


def obtener_info_tags(tag_files=None):
    """Obtiene informacion de los archivos de tags configurados."""
    info_archivos = []
    configured_files = tag_files or load_settings()["tags"]["files"]

    for file_path in configured_files:
        file = Path(file_path)
        if file.exists():
            file_size_mb = round(file.stat().st_size / (1024 * 1024), 2)
            last_modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%d-%m-%Y %H:%M:%S")
            info_archivos.append({"nombre": file.name, "tamano": file_size_mb, "ultima_mod": last_modified})
        else:
            info_archivos.append({"nombre": file.name, "tamano": "No encontrado", "ultima_mod": "No disponible"})

    return info_archivos
