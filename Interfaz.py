import os
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox
from app import buscar_archivo_ini, leer_configuracion, find_and_move_files, editar_potencia

# -----------------------------
# Función para abrir el programa de testeo
# -----------------------------
def abrir_testeo():
    ruta_programa = "C:\\Via\\Aplicacion\\"
    
    if not os.path.exists(ruta_programa):
        messagebox.showerror("Error", "El programa de testeo no se encuentra en la ubicación especificada.")
        print(f"no se encuentra la {ruta_programa}")
        return

    try:
        subprocess.run(["runas", "/user:administrator", ruta_programa], input="+-*AUMARadmin", text=True)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el programa: {e}")

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

        label_host.configure(text=f"REMOTE_HOST: {remote_host}")
        label_potencia.configure(text=f"POTENCIA: {potencia}")

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
# Configuración de la interfaz gráfica con CustomTkinter
# -----------------------------
ctk.set_appearance_mode("dark")  # Tema oscuro moderno
ctk.set_default_color_theme("blue")  # Paleta de colores

root = ctk.CTk()
root.title("Gestión de Archivos y Configuración - Sistemas La Huella")
root.geometry("600x500")

# -----------------------------
# Sección: Mover Archivos
# -----------------------------
frame_archivos = ctk.CTkFrame(root)
frame_archivos.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(frame_archivos, text="Mover Archivos .dat", font=("Arial", 14, "bold")).pack(pady=10)

source_path_var = ctk.StringVar()
destination_path_var = ctk.StringVar()

ctk.CTkEntry(frame_archivos, textvariable=source_path_var, width=350).pack(pady=5)
ctk.CTkButton(frame_archivos, text="Seleccionar Origen", command=select_source).pack(pady=5)

ctk.CTkEntry(frame_archivos, textvariable=destination_path_var, width=350).pack(pady=5)
ctk.CTkButton(frame_archivos, text="Seleccionar Destino", command=select_destination).pack(pady=5)

ctk.CTkButton(frame_archivos, text="Mover Archivos", command=move_files, fg_color="green").pack(pady=10)

# -----------------------------
# Sección: Configuración de Antena
# -----------------------------
frame_antena = ctk.CTkFrame(root)
frame_antena.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(frame_antena, text="Configuración de Antena", font=("Arial", 14, "bold")).pack(pady=10)

label_host = ctk.CTkLabel(frame_antena, text="REMOTE_HOST: Cargando...")
label_host.pack()

label_potencia = ctk.CTkLabel(frame_antena, text="POTENCIA: Cargando...")
label_potencia.pack()

potencia_entry = ctk.CTkEntry(frame_antena, width=100)
potencia_entry.pack(pady=5)

ctk.CTkButton(frame_antena, text="Actualizar Potencia", command=actualizar_potencia).pack(pady=5)
ctk.CTkButton(frame_antena, text="Mostrar Datos", command=mostrar_datos_antena).pack(pady=5)

# -----------------------------
# Sección: Acceso Directo a Testeo
# -----------------------------
frame_testeo = ctk.CTkFrame(root)
frame_testeo.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(frame_testeo, text="Acceso a Testeo de Aplicación", font=("Arial", 14, "bold")).pack(pady=10)
ctk.CTkButton(frame_testeo, text="Abrir Testeo", command=abrir_testeo, fg_color="orange").pack(pady=10)

# Ejecutar la aplicación
root.mainloop()
