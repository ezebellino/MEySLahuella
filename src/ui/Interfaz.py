import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import subprocess
import socket
import serial.tools.list_ports
import customtkinter as ctk
from tkinter import messagebox, filedialog
from src.app.tag_services import obtener_info_tags
from src.app.antena_services import (
    buscar_archivo_ini,
    leer_configuracion,
    editar_potencia
)
from src.app.mover_services import find_and_move_files
from src.ui.login import LoginWindow

DEFAULT_SOURCE_PATH = "C:\\Via\\Aplicacion"

# --- Funciones de lógica UI/UX ---
def obtener_info_sistema():
    try:
        nombre_equipo = socket.gethostname()
        ip_local = socket.gethostbyname(nombre_equipo)
        ip_split = ip_local.split(".")
        via = f"Vía {ip_split[3][-2:]} - La Huella" if len(ip_split) == 4 else "Vía Desconocida"
        label_equipo.configure(text=f"Equipo: {nombre_equipo}")
        label_ip.configure(text=f"IP: {ip_local}")
        label_via.configure(text=via)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la información de red: {e}")

def move_files():
    source_path = source_var.get().strip()
    destination_path = dest_var.get().strip()

    if not os.path.exists(source_path):
        messagebox.showwarning("Advertencia", "Ruta de origen inválida.")
        source_path = filedialog.askdirectory(title="Seleccionar carpeta origen")

    if not os.path.exists(destination_path):
        messagebox.showerror("Error", "Seleccione una carpeta de destino válida.")
        return

    try:
        final_folder = find_and_move_files(source_path, destination_path)
        if final_folder:
            messagebox.showinfo("Éxito", f"Archivos movidos a: {final_folder}")
        else:
            messagebox.showinfo("Sin cambios", "No se encontraron archivos .dat.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def detectar_puertos_com():
    puertos = serial.tools.list_ports.comports()
    disponibles = [p.device for p in puertos]
    label_puertos.configure(text=f"Puertos COM: {', '.join(disponibles) if disponibles else 'Ninguno'}")

def actualizar_datos_antena():
    try:
        archivo_ini = buscar_archivo_ini()
        remote_host, potencia = leer_configuracion(archivo_ini)
        label_antena_ip.configure(text=f"IP Antena: {remote_host}")
        label_potencia.configure(text=f"POTENCIA: {potencia}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def modificar_potencia():
    try:
        archivo_ini = buscar_archivo_ini()
        nueva_potencia = potencia_entry.get()
        if not nueva_potencia.isdigit():
            messagebox.showerror("Error", "La potencia debe ser un número.")
            return
        editar_potencia(archivo_ini, nueva_potencia)
        messagebox.showinfo("Éxito", "POTENCIA actualizada.")
        actualizar_datos_antena()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def abrir_testeo():
    ruta_programa = r"C:\\Via\\Testeo\\Testeo.exe"
    if not os.path.exists(ruta_programa):
        messagebox.showerror("Error", "No se encuentra Testeo.exe")
        return
    try:
        subprocess.run([ruta_programa], check=True)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def actualizar_info_tags():
    info_tags = obtener_info_tags()
    label_tag1_info.configure(text=f"{info_tags[0]['tamano']} MB - {info_tags[0]['ultima_mod']}")
    label_tag2_info.configure(text=f"{info_tags[1]['tamano']} MB - {info_tags[1]['ultima_mod']}")

# --- Constructor de UI modular ---
def build_dashboard_page1(root, show_page):
    global label_equipo, label_ip, label_via, label_puertos

    page1 = ctk.CTkFrame(root, fg_color="#0f172a")

    def section(title, fg="#1e293b", text_color="#f1f5f9"):
        frame = ctk.CTkFrame(page1, fg_color=fg, corner_radius=15)
        frame.pack(pady=15, padx=20, fill="x")
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont("Poppins", 18, "bold"), text_color=text_color, anchor="w").pack(anchor="w", padx=10, pady=(10, 5))
        return frame

    # --- Sistema ---
    frame_info = section("📡 Información del Sistema")
    label_equipo = ctk.CTkLabel(frame_info, text="Equipo: ...", font=("Poppins", 14), text_color="#f1f5f9", anchor="w")
    label_equipo.pack(anchor="w", padx=10)
    label_ip = ctk.CTkLabel(frame_info, text="IP: ...", font=("Poppins", 14), text_color="#f1f5f9", anchor="w")
    label_ip.pack(anchor="w", padx=10)
    label_via = ctk.CTkLabel(frame_info, text="Vía: ...", font=("Poppins", 14), text_color="#f1f5f9", anchor="w")
    label_via.pack(anchor="w", padx=10)

    ctk.CTkButton(frame_info, text="🔄 Actualizar", command=obtener_info_sistema,
                  font=("Poppins", 14), fg_color="#3b82f6", hover_color="#2563eb", corner_radius=10).pack(pady=10)

    # --- COM ---
    frame_puertos = section("🔌 Puertos COM", fg="#334155")
    label_puertos = ctk.CTkLabel(frame_puertos, text="Cargando...", font=("Poppins", 14), text_color="#f1f5f9", anchor="w")
    label_puertos.pack(anchor="w", padx=10)
    ctk.CTkButton(frame_puertos, text="📡 Detectar Puertos", command=detectar_puertos_com,
                  font=("Poppins", 14), fg_color="#3b82f6", hover_color="#2563eb", corner_radius=10).pack(pady=10)

    # --- Testeo ---
    frame_testeo = section("🧪 Modo Testeo", fg="#475569")
    ctk.CTkButton(frame_testeo, text="▶ Ejecutar Testeo", command=abrir_testeo,
                  font=("Poppins", 14), fg_color="#f97316", hover_color="#ea580c", corner_radius=10).pack(pady=20)

    # --- Navegación ---
    ctk.CTkButton(page1, text="Siguiente →", command=lambda: show_page(1),
                  font=("Poppins", 14), fg_color="#3b82f6", hover_color="#2563eb", corner_radius=10).pack(pady=20)

    return page1

# --- App Entrypoint ---
def run_app():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("src/ui/theme.json")  # Ruta correcta

    global root, label_tag1_info, label_tag2_info, label_antena_ip, label_potencia
    global potencia_entry, source_var, dest_var

    root = ctk.CTk()
    root.title("Dashboard - MEyS Lahuella")
    screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
    win_w, win_h = int(screen_w * 0.85), int(screen_h * 0.85)
    root.geometry(f"{win_w}x{win_h}+{(screen_w - win_w)//2}+{(screen_h - win_h)//2}")
    root.resizable(False, False)

    pages = {}
    current_page = 0

    def show_page(index):
        nonlocal current_page
        current_page = index
        for page in pages.values():
            page.pack_forget()
        pages[index].pack(fill="both", expand=True)

    # --- Construcción modular ---
    page1 = build_dashboard_page1(root, show_page)
    pages[0] = page1

    # TODO: agregar página 2 rediseñada también
    show_page(0)

    # --- Inicialización de datos ---
    root.after(500, obtener_info_sistema)
    root.after(500, detectar_puertos_com)

    root.mainloop()

# --- Lanzador desde Login ---
def iniciar_dashboard():
    run_app()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("src/ui/theme.json")
    login = LoginWindow(on_success_callback=iniciar_dashboard)
    login.mainloop()
