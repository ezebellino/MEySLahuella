import os
import shutil
import configparser
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

# -----------------------------
# Funcionalidades de antena
# -----------------------------

def buscar_archivo_ini(ruta="C:\\Windows\\", nombre_archivo="TciNumero.ini"):
    """Busca el archivo TciNumero.ini en la ruta especificada."""
    archivo = os.path.join(ruta, nombre_archivo)
    if os.path.exists(archivo):
        return archivo
    else:
        raise FileNotFoundError(f"No se encontró el archivo {nombre_archivo} en {ruta}")
    
def leer_configuracion(archivo_ini):
    """Lee la configuración de la sección [ANTENA_UIP] del archivo .ini."""
    config = configparser.ConfigParser()
    config.read(archivo_ini)

    if 'ANTENA_UIP' not in config:
        raise KeyError("La sección [ANTENA_UIP] no se encuentra en el archivo.")

    remote_host = config['ANTENA_UIP'].get('REMOTE_HOST', 'No definido')
    potencia = config['ANTENA_UIP'].get('POTENCIA', 'No definida')

    return remote_host, potencia

def editar_potencia(archivo_ini, nueva_potencia):
    """Edita el valor de POTENCIA en la sección [ANTENA_UIP]."""
    config = configparser.ConfigParser()
    config.read(archivo_ini)

    if 'ANTENA_UIP' not in config:
        raise KeyError("La sección [ANTENA_UIP] no se encuentra en el archivo.")

    config['ANTENA_UIP']['POTENCIA'] = str(nueva_potencia)

    with open(archivo_ini, 'w') as configfile:
        config.write(configfile)

    print(f"El valor de POTENCIA se actualizó a {nueva_potencia}.")
    
# Main
try:
    archivo_ini = buscar_archivo_ini()

    # Leer los valores actuales
    remote_host, potencia = leer_configuracion(archivo_ini)
    print(f"REMOTE_HOST: {remote_host}")
    print(f"POTENCIA: {potencia}")

    # Editar la potencia
    nueva_potencia = input("Ingrese el nuevo valor para POTENCIA: ")
    editar_potencia(archivo_ini, nueva_potencia)

except FileNotFoundError as e:
    print(e)
except KeyError as e:
    print(e)
except Exception as e:
    print(f"Error inesperado: {e}")