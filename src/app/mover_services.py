from pathlib import Path
from datetime import datetime
import shutil


def find_and_move_files(source_path, destination_path):
    """Mueve todos los archivos .dat de la carpeta de origen a una subcarpeta con fecha en la carpeta de destino."""

    source = Path(source_path)
    destination = Path(destination_path)

    if not source.exists():
        print(f"La ruta de origen no existe: {source_path}")
        return None

    # Crear la carpeta de destino con la fecha actual
    today = datetime.now().strftime("%d.%m.%y")
    folder_name = today
    counter = 1

    while (destination / folder_name).exists():
        folder_name = f"{today}-{counter}"
        counter += 1

    final_destination = destination / folder_name
    final_destination.mkdir(parents=True, exist_ok=True)

    # Mover archivos .dat
    files_moved = 0
    for file in source.rglob(
        "*.dat"
    ):  # Busca archivos .dat en todos los subdirectorios
        shutil.move(str(file), str(final_destination / file.name))
        files_moved += 1

    print(f"{files_moved} archivos .dat movidos a: {final_destination}")
    return final_destination if files_moved > 0 else None
