import shutil
from datetime import datetime
from pathlib import Path


def find_and_move_files(source_path, destination_path):
    """Mueve todos los archivos .dat de la carpeta de origen a una subcarpeta con fecha."""
    source = Path(source_path)
    destination = Path(destination_path)

    if not source.exists():
        return None

    today = datetime.now().strftime("%d.%m.%y")
    folder_name = today
    counter = 1

    while (destination / folder_name).exists():
        folder_name = f"{today}-{counter}"
        counter += 1

    final_destination = destination / folder_name
    final_destination.mkdir(parents=True, exist_ok=True)

    files_moved = 0
    for file in source.rglob("*.dat"):
        shutil.move(str(file), str(final_destination / file.name))
        files_moved += 1

    return final_destination if files_moved > 0 else None
