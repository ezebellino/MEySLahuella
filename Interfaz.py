import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import shutil

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

def find_and_move_files(source_path, destination_path):
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"La ruta de origen no existe: {source_path}")

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

    return final_destination


# Crear la ventana principal
root = tk.Tk()
root.title("Mover Archivos .dat")
root.geometry("500x300")
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

# Títulos
ttk.Label(root, text="Ruta de Origen:").pack(pady=(20, 5))
source_entry = ttk.Entry(root, textvariable=source_path_var, width=50)
source_entry.pack(pady=5)
ttk.Button(root, text="Seleccionar Carpeta", command=select_source).pack(pady=5)

ttk.Label(root, text="Ruta de Destino:").pack(pady=(20, 5))
destination_entry = ttk.Entry(root, textvariable=destination_path_var, width=50)
destination_entry.pack(pady=5)
ttk.Button(root, text="Seleccionar Carpeta", command=select_destination).pack(pady=5)

# Botón de mover archivos
ttk.Button(root, text="Mover Archivos", command=move_files).pack(pady=(20, 10))

# Ejecutar la aplicación
root.mainloop()
