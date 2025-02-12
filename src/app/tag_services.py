from datetime import datetime
from pathlib import Path

TAG_FILES = [
    "C:\\Via\\Aplicacion\\LMTAGS_AUBASA.DAT",
    "C:\\Via\\Aplicacion\\LMTAGSPAT_AUBASA.DAT",
]


def obtener_info_tags():
    """Obtiene información de los archivos de tags (nombre, tamaño y última modificación)."""
    info_archivos = []

    for file_path in TAG_FILES:
        file = Path(file_path)
        if file.exists():
            file_size_mb = round(
                file.stat().st_size / (1024 * 1024), 2
            )  # Convertir bytes a MB
            last_modified = datetime.fromtimestamp(file.stat().st_mtime).strftime(
                "%d-%m-%Y %H:%M:%S"
            )
            info_archivos.append(
                {
                    "nombre": file.name,
                    "tamano": file_size_mb,
                    "ultima_mod": last_modified,
                }
            )
        else:
            info_archivos.append(
                {
                    "nombre": file.name,
                    "tamano": "No encontrado",
                    "ultima_mod": "No disponible",
                }
            )

    return info_archivos
