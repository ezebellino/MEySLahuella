import configparser
import os

from src.config.settings import load_settings


def buscar_archivo_ini(ruta=None, nombre_archivo=None):
    """Busca el archivo TciNumero.ini en la ruta configurada."""
    path_settings = load_settings()["paths"]
    ruta = ruta or path_settings["antenna_ini_dir"]
    nombre_archivo = nombre_archivo or path_settings["antenna_ini_name"]
    archivo = os.path.join(ruta, nombre_archivo)
    if os.path.exists(archivo):
        return archivo
    raise FileNotFoundError(f"No se encontro el archivo {nombre_archivo} en {ruta}")


def leer_configuracion(archivo_ini):
    """Lee los valores de REMOTE_HOST y POTENCIA desde la seccion [ANTENA_UIP]."""
    config = configparser.ConfigParser()
    config.optionxform = str

    try:
        with open(archivo_ini, "r", encoding="utf-8") as file_handle:
            config.read_file(file_handle)

        if "ANTENA_UIP" not in config:
            raise KeyError("La seccion [ANTENA_UIP] no se encuentra en el archivo.")

        remote_host = config["ANTENA_UIP"].get("REMOTE_HOST", "No definido")
        potencia = config["ANTENA_UIP"].get("POTENCIA", "No definida")
        return remote_host, potencia
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"No se encontro el archivo {archivo_ini}") from exc
    except Exception as exc:
        raise Exception(f"Error al leer el archivo: {exc}") from exc


def editar_potencia(archivo_ini, nueva_potencia):
    """Edita el valor de POTENCIA en la seccion [ANTENA_UIP]."""
    config = configparser.ConfigParser()
    config.optionxform = str

    if int(nueva_potencia) > 30 or int(nueva_potencia) < 0:
        raise ValueError("El valor de POTENCIA debe estar entre 0 y 30.")

    try:
        with open(archivo_ini, "r", encoding="utf-8") as file_handle:
            config.read_file(file_handle)

        if "ANTENA_UIP" not in config:
            raise KeyError("La seccion [ANTENA_UIP] no se encuentra en el archivo.")

        config["ANTENA_UIP"]["POTENCIA"] = str(nueva_potencia)

        with open(archivo_ini, "w", encoding="utf-8") as configfile:
            config.write(configfile)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"No se encontro el archivo {archivo_ini}") from exc
    except Exception as exc:
        raise Exception(f"Error al editar el archivo: {exc}") from exc
