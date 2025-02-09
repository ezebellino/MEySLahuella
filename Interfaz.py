import os
import subprocess
import shutil
import socket
import serial.tools.list_ports
import customtkinter as ctk
from tkinter import messagebox, filedialog
from app import buscar_archivo_ini, leer_configuracion, find_and_move_files, editar_potencia, obtener_info_tags

# -----------------------------
# Variables Globales
# -----------------------------
DEFAULT_SOURCE_PATH = "C:\\Via\\Aplicacion"

# -----------------------------
# Funciones existentes (NO SE ELIMINAN)
# -----------------------------
def obtener_info_sistema():
    try:
        nombre_equipo = socket.gethostname()
        ip_local = socket.gethostbyname(nombre_equipo)
        ip_split = ip_local.split(".")
        if len(ip_split) == 4:
            via = f"Vía {ip_split[3][-2:]} - La Huella"
        else:
            via = "Vía Desconocida o Sin IP"

        # Actualizar UI
        label_equipo.configure(text=f"Equipo: {nombre_equipo}")
        label_ip.configure(text=f"IP: {ip_local}")
        label_via.configure(text=via)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la información de la red: {e}")

def move_files():
    source_path = source_var.get().strip()
    destination_path = dest_var.get().strip()

    if not os.path.exists(source_path):
        messagebox.showwarning("Advertencia", f"La ruta de origen '{source_path}' no existe. Seleccione una manualmente.")
        source_path = filedialog.askdirectory(title="Seleccionar carpeta origen")

    if not os.path.exists(destination_path):
        messagebox.showerror("Error", "Debe seleccionar una carpeta de destino.")
        return

    try:
        final_folder = find_and_move_files(source_path, destination_path)
        if final_folder:
            messagebox.showinfo("Éxito", f"Archivos .dat movidos a: {final_folder}")
        else:
            messagebox.showinfo("Sin cambios", "No se encontraron archivos .dat para mover.")
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error: {e}")

def detectar_puertos_com():
    puertos = serial.tools.list_ports.comports()
    puertos_disponibles = [p.device for p in puertos]
    label_puertos.configure(
        text=f"Puertos COM Activos: {', '.join(puertos_disponibles) if puertos_disponibles else 'No se detectaron puertos COM'}"
    )

def actualizar_datos_antena():
    try:
        archivo_ini = buscar_archivo_ini()
        remote_host, potencia = leer_configuracion(archivo_ini)
        label_antena_ip.configure(text=f"IP Antena: {remote_host}")
        label_potencia.configure(text=f"POTENCIA: {potencia}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer la antena: {e}")

def modificar_potencia():
    try:
        archivo_ini = buscar_archivo_ini()
        nueva_potencia = potencia_entry.get()
        if not nueva_potencia.isdigit():
            messagebox.showerror("Error", "La potencia debe ser un número.")
            return
        editar_potencia(archivo_ini, nueva_potencia)
        messagebox.showinfo("Éxito", "POTENCIA actualizada correctamente")
        actualizar_datos_antena()
    except Exception as e:
        messagebox.showerror("Error", f"Error al actualizar la potencia: {e}")

def abrir_testeo():
    ruta_programa = "C:\\Via\\Aplicación\\"
    if not os.path.exists(ruta_programa):
        messagebox.showerror("Error", "El programa de testeo no se encuentra en la ubicación especificada.")
        return
    try:
        subprocess.run(["runas", "/user:administrator", ruta_programa], input="+-*AUMARadmin", text=True)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el programa: {e}")

def actualizar_info_tags():
    info_tags = obtener_info_tags()
    label_tag1_info.configure(text=f"{info_tags[0]['tamano']} MB - {info_tags[0]['ultima_mod']}")
    label_tag2_info.configure(text=f"{info_tags[1]['tamano']} MB - {info_tags[1]['ultima_mod']}")

# -----------------------------
# Configuración de la interfaz gráfica estilo Dashboard
# -----------------------------
ctk.set_appearance_mode("dark")  # Tema oscuro
ctk.set_default_color_theme("blue")  # Tema moderno

root = ctk.CTk()
root.title("Dashboard - Gestión de Peaje")
root.geometry("800x600")
root.resizable(False, False)

# Contenedor de páginas
pages = {}
current_page = 0

# -----------------------------
# Función para cambiar de página
# -----------------------------
def show_page(page_number):
    global current_page
    current_page = page_number
    for page in pages.values():
        page.pack_forget()
    pages[page_number].pack(fill="both", expand=True)

# -----------------------------
# Página 1: Información del Sistema, Puertos COM, Testeo
# -----------------------------
page1 = ctk.CTkFrame(root)
pages[0] = page1

# Panel: Información del Sistema
frame_info = ctk.CTkFrame(page1, fg_color="#6A0DAD", corner_radius=10)
frame_info.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(frame_info, text="Información del Sistema", font=("Arial", 14, "bold"), text_color="white").pack(pady=5)
label_equipo = ctk.CTkLabel(frame_info, text="Equipo: Cargando...", anchor="w", text_color="white")
label_equipo.pack()
label_ip = ctk.CTkLabel(frame_info, text="IP: Cargando...", anchor="w", text_color="white")
label_ip.pack()
label_via = ctk.CTkLabel(frame_info, text="Vía: Cargando...", anchor="w", text_color="white")
label_via.pack()
ctk.CTkButton(frame_info, text="Actualizar Info", command=obtener_info_sistema, fg_color="#9B30FF").pack(pady=10)

# Panel: Detección de Puertos COM
frame_puertos = ctk.CTkFrame(page1, fg_color="#00CED1", corner_radius=10)
frame_puertos.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(frame_puertos, text="Puertos COM Activos", font=("Arial", 14, "bold"), text_color="black").pack(pady=5)
label_puertos = ctk.CTkLabel(frame_puertos, text="Cargando...", anchor="w", text_color="black")
label_puertos.pack()
ctk.CTkButton(frame_puertos, text="Detectar Puertos", command=detectar_puertos_com, fg_color="darkblue").pack(pady=10)

# Panel: Acceso a Testeo
frame_testeo = ctk.CTkFrame(page1, fg_color="#FF4500", corner_radius=10)
frame_testeo.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(frame_testeo, text="Ingrese al Testeo", font=("Arial", 14, "bold"), text_color="white").pack(pady=5)
ctk.CTkButton(frame_testeo, text="Abrir Testeo", command=abrir_testeo, fg_color="darkorange").pack(expand=True, pady=20)

# Botón para ir a la segunda página
ctk.CTkButton(page1, text="Siguiente →", command=lambda: show_page(1)).pack(pady=10)

# -----------------------------
# Página 2: Mover Archivos, Configuración Antena, Última Actualización
# -----------------------------
page2 = ctk.CTkScrollableFrame(root, label_text="Página 2", width=800, height=600)
pages[1] = page2

# Panel: Mover Archivos .dat
frame_archivos = ctk.CTkFrame(page2, fg_color="#32CD32", corner_radius=10)
frame_archivos.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(frame_archivos, text="Mover Archivos .dat", font=("Arial", 14, "bold"), text_color="black").pack(pady=5)
source_var = ctk.StringVar(value=DEFAULT_SOURCE_PATH)
dest_var = ctk.StringVar()

ctk.CTkEntry(frame_archivos, textvariable=source_var, width=300).pack(pady=5)
ctk.CTkButton(frame_archivos, text="Seleccionar Origen", command=lambda: source_var.set(filedialog.askdirectory())).pack(pady=5)

ctk.CTkEntry(frame_archivos, textvariable=dest_var, width=300).pack(pady=5)
ctk.CTkButton(frame_archivos, text="Seleccionar Destino", command=lambda: dest_var.set(filedialog.askdirectory())).pack(pady=5)
ctk.CTkButton(frame_archivos, text="Mover Archivos", command=move_files, fg_color="darkgreen").pack(pady=10)

# Panel: Configuración de Antena
frame_antena = ctk.CTkFrame(page2, fg_color="#1E90FF", corner_radius=10)
frame_antena.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(frame_antena, text="Configuración de Antena", font=("Arial", 14, "bold"), text_color="white").pack(pady=5)
label_antena_ip = ctk.CTkLabel(frame_antena, text="IP Antena: Cargando...", anchor="w", text_color="white")
label_antena_ip.pack()
label_potencia = ctk.CTkLabel(frame_antena, text="POTENCIA: Cargando...", anchor="w", text_color="white")
label_potencia.pack()
potencia_entry = ctk.CTkEntry(frame_antena, width=100)
potencia_entry.pack(pady=5)
ctk.CTkButton(frame_antena, text="Actualizar Potencia", command=modificar_potencia, fg_color="#4682B4").pack(pady=5)
ctk.CTkButton(frame_antena, text="Mostrar Datos", command=actualizar_datos_antena, fg_color="#4169E1").pack(pady=5)

# Panel: Última Actualización de Listas de Tags
frame_tags = ctk.CTkFrame(page2, fg_color="#FFD700", corner_radius=10, border_width=2, border_color="black")
frame_tags.pack(pady=10, padx=10, fill="x")

title_label = ctk.CTkLabel(frame_tags, text="Última Actualización de Tags", font=("Arial", 14, "bold"), text_color="black")
title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="n")

label_tag1_name = ctk.CTkLabel(frame_tags, text="LMTAGS_AUBASA.DAT:", font=("Arial", 12, "bold"), text_color="black", anchor="w")
label_tag1_name.grid(row=1, column=0, sticky="w", padx=5, pady=5)

label_tag1_info = ctk.CTkLabel(frame_tags, text="Archivo no encontrado", anchor="w", text_color="black")
label_tag1_info.grid(row=2, column=0, sticky="w", padx=5, pady=5)

label_tag2_name = ctk.CTkLabel(frame_tags, text="LMTAGSPAT_AUBASA.DAT:", font=("Arial", 12, "bold"), text_color="black", anchor="w")
label_tag2_name.grid(row=3, column=0, sticky="w", padx=5, pady=5)

label_tag2_info = ctk.CTkLabel(frame_tags, text="Archivo no encontrado", anchor="w", text_color="black")
label_tag2_info.grid(row=4, column=0, sticky="w", padx=10, pady=5)

ctk.CTkButton(frame_tags, text="Actualizar", command=actualizar_info_tags).grid(row=5, column=0, columnspan=2, pady=10)

# Botón para regresar a la primera página
ctk.CTkButton(page2, text="← Atrás", command=lambda: show_page(0)).pack(pady=10)

# -----------------------------
# Cargar datos iniciales
# -----------------------------
show_page(0)

root.after(500, obtener_info_sistema)
root.after(500, detectar_puertos_com)
root.after(500, actualizar_datos_antena)
root.after(500, actualizar_info_tags)

# Ejecutar la aplicación
root.mainloop()
