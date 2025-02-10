import configparser
import os


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
    """Lee los valores de REMOTE_HOST y POTENCIA desde la sección [ANTENA_UIP]."""
    config = configparser.ConfigParser()
    config.optionxform = str  # Mantiene las claves con mayúsculas/minúsculas exactas

    try:
        with open(archivo_ini, "r", encoding="utf-8") as f:
            config.read_file(f)  # Leer el archivo INI forzando UTF-8

        print(f"Secciones detectadas: {config.sections()}")  # Debugging

        if "ANTENA_UIP" not in config:
            raise KeyError("La sección [ANTENA_UIP] no se encuentra en el archivo.")

        remote_host = config["ANTENA_UIP"].get("REMOTE_HOST", "No definido")
        potencia = config["ANTENA_UIP"].get("POTENCIA", "No definida")

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

        if "ANTENA_UIP" not in config:
            raise KeyError("La sección [ANTENA_UIP] no se encuentra en el archivo.")

        config["ANTENA_UIP"]["POTENCIA"] = str(nueva_potencia)

        with open(archivo_ini, "w", encoding="utf-8") as configfile:
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
        archivo_ini = buscar_archivo_ini(
            "C:\\Windows\\"
        )  # Cambia a la ruta donde está tu archivo

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
