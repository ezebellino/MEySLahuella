import os
import shutil
from datetime import datetime

def find_and_move_files(source_path, destination_path):
    if not os.path.exists(source_path):
        print(f"La ruta de origen no existe: {source_path}")
        return

    # Crear el nombre de la carpeta basada en la fecha
    today = datetime.now().strftime("%d.%m.%y")
    folder_name = today
    counter = 1

    # Asegurar que el nombre de la carpeta sea único
    while os.path.exists(os.path.join(destination_path, folder_name)):
        folder_name = f"{today}-{counter}"
        counter += 1

    # Crear la carpeta de destino
    final_destination = os.path.join(destination_path, folder_name)
    os.makedirs(final_destination)

    # Buscar y mover archivos .dat
    files_moved = 0
    for root, _, files in os.walk(source_path):
        for file in files:
            if file.lower().endswith(".dat"):
                src_file = os.path.join(root, file)
                dest_file = os.path.join(final_destination, file)
                shutil.move(src_file, dest_file)
                files_moved += 1

    print(f"{files_moved} archivos .dat movidos a: {final_destination}")
    return final_destination
