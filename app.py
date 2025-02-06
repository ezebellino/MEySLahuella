import os
import shutil
import configparser
from datetime import datetime
from pathlib import Path

TAG_FILES = [
    "C:\\Via\\Aplicacion\\LMTAGS_AUBASA.DAT",
    "C:\\Via\\Aplicacion\\LMTAGSPAT_AUBASA.DAT"
]

def obtener_info_tags():
    """Obtiene información de los archivos de tags (nombre, tamaño y última modificación)."""
    info_archivos = []

    for file_path in TAG_FILES:
        file = Path(file_path)
        if file.exists():
            file_size_mb = round(file.stat().st_size / (1024 * 1024), 2)  # Convertir bytes a MB
            last_modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%d-%m-%Y %H:%M:%S")
            info_archivos.append({"nombre": file.name, "tamano": file_size_mb, "ultima_mod": last_modified})
        else:
            info_archivos.append({"nombre": file.name, "tamano": "No encontrado", "ultima_mod": "No disponible"})

    return info_archivos

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
    for file in source.rglob("*.dat"):  # Busca archivos .dat en todos los subdirectorios
        shutil.move(str(file), str(final_destination / file.name))
        files_moved += 1

    print(f"{files_moved} archivos .dat movidos a: {final_destination}")
    return final_destination if files_moved > 0 else None

# -----------------------------
# Funcionalidades de antena
# -----------------------------

def buscar_archivo_ini(ruta="C:\\Windows\\", nombre_archivo="TciNumero.ini.txt"):
    """Busca el archivo TciNumero.ini en la ruta especificada."""
    archivo = os.path.join(ruta, nombre_archivo)
    if os.path.exists(archivo):
        return archivo
    else:
        raise FileNotFoundError(f"No se encontró el archivo {nombre_archivo} en {ruta}")
    
def leer_configuracion(archivo_ini):
    """Lee los valores de REMOTE_HOST y POTENCIA desde la sección [ANTENA_UIP]."""
    config = configparser.ConfigParser()
    config.optionxform = str  # Mantiene las claves con mayúsculas/minúsculas exactas

    try:
        with open(archivo_ini, "r", encoding="utf-8") as f:
            config.read_file(f)  # Leer el archivo INI forzando UTF-8

        print(f"Secciones detectadas: {config.sections()}")  # Debugging

        if 'ANTENA_UIP' not in config:
            raise KeyError("La sección [ANTENA_UIP] no se encuentra en el archivo.")

        remote_host = config['ANTENA_UIP'].get('REMOTE_HOST', 'No definido')
        potencia = config['ANTENA_UIP'].get('POTENCIA', 'No definida')

        return remote_host, potencia

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo {archivo_ini}")
    except Exception as e:
        raise Exception(f"Error al leer el archivo: {e}")

def editar_potencia(archivo_ini, nueva_potencia):
    """Edita el valor de POTENCIA en la sección [ANTENA_UIP]."""
    config = configparser.ConfigParser()
    config.optionxform = str  # Mantiene el formato de las claves
    # valor máximo de potencia es 30 y mínimo 0
    if int(nueva_potencia) > 30 or int(nueva_potencia) < 0:
        raise ValueError("El valor de POTENCIA debe estar entre 0 y 30.")
    
    
    try:
        with open(archivo_ini, "r", encoding="utf-8") as f:
            config.read_file(f)  # Leer el archivo con UTF-8

        print(f"Secciones detectadas antes de editar: {config.sections()}")  # Debugging

        if 'ANTENA_UIP' not in config:
            raise KeyError("La sección [ANTENA_UIP] no se encuentra en el archivo.")

        config['ANTENA_UIP']['POTENCIA'] = str(nueva_potencia)

        with open(archivo_ini, 'w', encoding="utf-8") as configfile:
            config.write(configfile)

        print(f"El valor de POTENCIA se actualizó a {nueva_potencia}.")

    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo {archivo_ini}")
    except Exception as e:
        raise Exception(f"Error al editar el archivo: {e}")

# -----------------------------
# Función para probar manualmente (opcional)
# -----------------------------
if __name__ == "__main__":
    try:
        archivo_ini = buscar_archivo_ini("C:\\Windows\\")  # Cambia a la ruta donde está tu archivo

        # Leer los valores actuales
        remote_host, potencia = leer_configuracion(archivo_ini)
        print(f"REMOTE_HOST: {remote_host}")
        print(f"POTENCIA: {potencia}")

        # Preguntar si desea actualizar la potencia manualmente
        opcion = input("¿Desea actualizar la potencia? (s/n): ").strip().lower()
        if opcion == "s":
            nueva_potencia = input("Ingrese el nuevo valor para POTENCIA: ")
            editar_potencia(archivo_ini, nueva_potencia)

    except FileNotFoundError as e:
        print(e)
    except KeyError as e:
        print(e)
    except Exception as e:
        print(f"Error inesperado: {e}")
