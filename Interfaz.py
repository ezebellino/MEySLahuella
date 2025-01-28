
from datetime import datetime
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app import buscar_archivo_ini, leer_configuracion, find_and_move_files, editar_potencia

# -----------------------------
# Funciones para mover archivos
# -----------------------------
def select_source():
    path = filedialog.askdirectory()
    if path:
        source_path_var.set(path)

def select_destination():
    path = filedialog.askdirectory()
    if path:
        destination_path_var.set(path)

def move_files():
    source_path = source_path_var.get()
    destination_path = destination_path_var.get()

    if not source_path or not destination_path:
        messagebox.showerror("Error", "Por favor selecciona ambas rutas.")
        return

    try:
        final_folder = find_and_move_files(source_path, destination_path)
        messagebox.showinfo("Éxito", f"Archivos movidos a: {final_folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error: {e}")

# -----------------------------
# Funciones para configuración de antena
# -----------------------------
def mostrar_datos_antena():
    try:
        archivo_ini = buscar_archivo_ini()
        remote_host, potencia = leer_configuracion(archivo_ini)

        # Mostrar los datos en la interfaz
        label_host.config(text=f"REMOTE_HOST: {remote_host}")
        label_potencia.config(text=f"POTENCIA: {potencia}")

    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el archivo: {e}")

def actualizar_potencia():
    try:
        archivo_ini = buscar_archivo_ini()
        nueva_potencia = potencia_entry.get()

        if not nueva_potencia.isdigit():
            messagebox.showerror("Error", "La potencia debe ser un número.")
            return

        editar_potencia(archivo_ini, nueva_potencia)
        messagebox.showinfo("Éxito", "POTENCIA actualizada correctamente")
        mostrar_datos_antena()
    except Exception as e:
        messagebox.showerror("Error", f"Error al actualizar la potencia: {e}")

# -----------------------------
# Configuración de la interfaz gráfica
# -----------------------------
root = tk.Tk()
root.title("Configuración y Mover Archivos")
root.geometry("500x600")
root.resizable(False, False)

# Variables
source_path_var = tk.StringVar()
destination_path_var = tk.StringVar()

# Estilos modernos
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", background="#1d3557", foreground="white", font=("Arial", 10, "bold"))
style.configure("TLabel", font=("Arial", 10))
style.configure("TEntry", font=("Arial", 10))

# -----------------------------
# Sección: Mover Archivos
# -----------------------------
ttk.Label(root, text="Mover Archivos .dat").pack(pady=(20, 5))

ttk.Label(root, text="Ruta de Origen:").pack(pady=(10, 5))
source_entry = ttk.Entry(root, textvariable=source_path_var, width=50)
source_entry.pack(pady=5)
ttk.Button(root, text="Seleccionar Carpeta", command=select_source).pack(pady=5)

ttk.Label(root, text="Ruta de Destino:").pack(pady=(10, 5))
destination_entry = ttk.Entry(root, textvariable=destination_path_var, width=50)
destination_entry.pack(pady=5)
ttk.Button(root, text="Seleccionar Carpeta", command=select_destination).pack(pady=5)

ttk.Button(root, text="Mover Archivos", command=move_files).pack(pady=(20, 10))

# -----------------------------
# Sección: Configuración de Antena
# -----------------------------
ttk.Label(root, text="Configuración de Antena").pack(pady=(30, 5))

label_host = ttk.Label(root, text="REMOTE_HOST: Cargando...")
label_host.pack()

label_potencia = ttk.Label(root, text="POTENCIA: Cargando...")
label_potencia.pack()

ttk.Button(root, text="Mostrar Datos", command=mostrar_datos_antena).pack(pady=(10, 5))

potencia_entry = ttk.Entry(root, width=20)
potencia_entry.pack(pady=(5, 5))
ttk.Button(root, text="Actualizar Potencia", command=actualizar_potencia).pack(pady=(10, 10))

# Ejecutar la aplicación
root.mainloop()
