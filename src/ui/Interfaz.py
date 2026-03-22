import os
import socket
import subprocess
import sys

import customtkinter as ctk
import serial.tools.list_ports
from tkinter import filedialog, messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.app.antena_services import buscar_archivo_ini, editar_potencia, leer_configuracion
from src.app.mover_services import find_and_move_files
from src.app.tag_services import obtener_info_tags
from src.config.settings import load_settings, save_settings
from src.ui.login import LoginFrame
from src.ui.theme_utils import apply_theme

APP_BG = "#09111f"
SURFACE = "#0f172a"
CARD = "#162033"
CARD_ALT = "#1c2940"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
PRIMARY = "#3b82f6"
PRIMARY_HOVER = "#2563eb"
SUCCESS = "#22c55e"
SUCCESS_HOVER = "#16a34a"
WARNING = "#f97316"
WARNING_HOVER = "#ea580c"
NEUTRAL = "#334155"
NEUTRAL_HOVER = "#475569"
BORDER = "#23314d"
INFO = "#38bdf8"
INFO_HOVER = "#0ea5e9"

apply_theme()


class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.settings = load_settings()
        self.pages = {}
        self.page_titles = {
            0: "Panel Operativo",
            1: "Archivos y Antena",
        }
        self.page_subtitles = {
            0: "Monitoreo rapido del puesto y accesos directos a tareas frecuentes.",
            1: "Gestion de tags, potencia de antena y movimiento de archivos DAT.",
        }
        self.nav_buttons = {}
        self.current_page = 0
        self.current_via_number = None
        self.source_var = ctk.StringVar(value=self.settings["paths"]["source_path"])
        self.dest_var = ctk.StringVar(value=self.settings["paths"]["destination_path"])
        self.widgets = {}
        self.toast_counter = 0
        self.toasts = {}

        self._configure_window()
        self._build_layout()
        self._build_pages()
        self._build_login()

    def _configure_window(self):
        self.title("Dashboard - MEyS Lahuella")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = int(screen_w * 0.9)
        win_h = int(screen_h * 0.88)
        self.geometry(f"{win_w}x{win_h}+{(screen_w - win_w)//2}+{(screen_h - win_h)//2}")
        self.minsize(1180, 760)
        self.configure(fg_color=APP_BG)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.bind("<Escape>", lambda _event: self.close_window())

    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color="#08101d", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(6, weight=1)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 18))
        ctk.CTkLabel(
            brand,
            text="MEyS",
            font=ctk.CTkFont("Poppins", 28, "bold"),
            text_color=TEXT,
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand,
            text="Centro de control de via",
            font=ctk.CTkFont("Poppins", 13),
            text_color=MUTED,
        ).pack(anchor="w", pady=(2, 0))

        self.nav_buttons[0] = self._create_nav_button("Resumen del sistema", 0, 1)
        self.nav_buttons[1] = self._create_nav_button("Operacion y archivos", 1, 2)

        info_box = ctk.CTkFrame(self.sidebar, fg_color="#101b30", corner_radius=18, border_width=1, border_color=BORDER)
        info_box.grid(row=5, column=0, sticky="ew", padx=20, pady=12)
        ctk.CTkLabel(
            info_box,
            text="Consejo",
            font=ctk.CTkFont("Poppins", 14, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=14, pady=(14, 4))
        ctk.CTkLabel(
            info_box,
            text="Usa el panel izquierdo para moverte entre vistas sin perder contexto operativo.",
            font=ctk.CTkFont("Poppins", 12),
            text_color=MUTED,
            justify="left",
            wraplength=200,
        ).pack(anchor="w", padx=14, pady=(0, 14))

        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 24))
        ctk.CTkLabel(
            footer,
            text="Version interna",
            font=ctk.CTkFont("Poppins", 12),
            text_color=MUTED,
        ).pack(anchor="w")
        ctk.CTkLabel(
            footer,
            text="CustomTkinter UI",
            font=ctk.CTkFont("Poppins", 12, "bold"),
            text_color=TEXT,
        ).pack(anchor="w")

        self.content = ctk.CTkFrame(self, fg_color=APP_BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(self.content, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=28, pady=(26, 12))
        self.header.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(
            self.header,
            text="Panel Operativo",
            font=ctk.CTkFont("Poppins", 28, "bold"),
            text_color=TEXT,
        )
        self.header_title.grid(row=0, column=0, sticky="w")
        self.header_subtitle = ctk.CTkLabel(
            self.header,
            text="Monitoreo rapido del puesto y accesos directos a tareas frecuentes.",
            font=ctk.CTkFont("Poppins", 13),
            text_color=MUTED,
        )
        self.header_subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.status_banner = ctk.CTkFrame(
            self.header,
            fg_color="#0f1b31",
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
        )
        self.status_banner.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        self.status_banner.grid_columnconfigure(1, weight=1)

        self.status_dot = ctk.CTkFrame(self.status_banner, width=12, height=12, corner_radius=999, fg_color=INFO)
        self.status_dot.grid(row=0, column=0, padx=(16, 10), pady=14)

        self.status_label = ctk.CTkLabel(
            self.status_banner,
            text="Inicia sesion para acceder al panel operativo.",
            font=ctk.CTkFont("Poppins", 13, "bold"),
            text_color=TEXT,
        )
        self.status_label.grid(row=0, column=1, sticky="w", pady=14)

        self.pages_container = ctk.CTkFrame(self.content, fg_color="transparent")
        self.pages_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.pages_container.grid_columnconfigure(0, weight=1)
        self.pages_container.grid_rowconfigure(0, weight=1)
        self._set_dashboard_visibility(False)
        self.toast_host = ctk.CTkFrame(self.content, fg_color="transparent")
        self.toast_host.place(relx=1.0, y=28, anchor="ne", x=-28)

    def _build_login(self):
        self.login_overlay = ctk.CTkFrame(self, fg_color=APP_BG, corner_radius=0)
        self.login_overlay.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.login_overlay.grid_columnconfigure(0, weight=1)
        self.login_overlay.grid_rowconfigure(0, weight=1)
        self.login_frame = LoginFrame(
            self.login_overlay,
            on_login_callback=self.handle_login,
            on_cancel_callback=self.close_window,
            initial_username=self.settings["ui"]["last_username"],
        )

    def _create_nav_button(self, text, index, row):
        button = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=lambda idx=index: self.show_page(idx),
            anchor="w",
            height=48,
            corner_radius=14,
            fg_color="transparent",
            hover_color="#12213a",
            text_color=TEXT,
            font=ctk.CTkFont("Poppins", 14, "bold"),
        )
        button.grid(row=row, column=0, sticky="ew", padx=16, pady=6)
        return button

    def _build_pages(self):
        self.pages[0] = self._build_system_page()
        self.pages[1] = self._build_operations_page()

    def _build_page_shell(self):
        page = ctk.CTkScrollableFrame(
            self.pages_container,
            fg_color="transparent",
            scrollbar_fg_color="#101b30",
            scrollbar_button_color=NEUTRAL,
            scrollbar_button_hover_color=PRIMARY_HOVER,
        )
        page.grid(row=0, column=0, sticky="nsew")
        return page

    def _build_section(self, parent, title, subtitle=None):
        frame = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=22, border_width=1, border_color=BORDER)
        frame.pack(fill="x", pady=(0, 18))
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont("Poppins", 19, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=20, pady=(18, 2))
        if subtitle:
            ctk.CTkLabel(
                frame,
                text=subtitle,
                font=ctk.CTkFont("Poppins", 12),
                text_color=MUTED,
                justify="left",
                wraplength=920,
            ).pack(anchor="w", padx=20, pady=(0, 14))
        return frame

    def _create_stat_card(self, parent, title, value_key, accent):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
        card.pack(side="left", fill="both", expand=True, padx=6)
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont("Poppins", 12, "bold"),
            text_color=MUTED,
        ).pack(anchor="w", padx=16, pady=(16, 6))
        value_label = ctk.CTkLabel(
            card,
            text="Cargando...",
            font=ctk.CTkFont("Poppins", 20, "bold"),
            text_color=TEXT,
            justify="left",
            wraplength=220,
        )
        value_label.pack(anchor="w", padx=16, pady=(0, 8))
        indicator = ctk.CTkFrame(card, height=4, fg_color=accent, corner_radius=10)
        indicator.pack(fill="x", padx=16, pady=(0, 16))
        self.widgets[value_key] = value_label

    def _build_system_page(self):
        page = self._build_page_shell()

        hero = ctk.CTkFrame(page, fg_color="#0d1628", corner_radius=24, border_width=1, border_color=BORDER)
        hero.pack(fill="x", pady=(0, 18))
        ctk.CTkLabel(
            hero,
            text="Vista general del puesto",
            font=ctk.CTkFont("Poppins", 24, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=22, pady=(20, 4))
        ctk.CTkLabel(
            hero,
            text="Esta pantalla resume conectividad, identificacion del equipo y accesos rapidos para validaciones diarias.",
            font=ctk.CTkFont("Poppins", 13),
            text_color=MUTED,
            wraplength=920,
            justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 16))

        stats_row = ctk.CTkFrame(hero, fg_color="transparent")
        stats_row.pack(fill="x", padx=16, pady=(0, 16))
        self._create_stat_card(stats_row, "Equipo", "label_equipo", PRIMARY)
        self._create_stat_card(stats_row, "IP local", "label_ip", SUCCESS)
        self._create_stat_card(stats_row, "Via detectada", "label_via", WARNING)

        status_section = self._build_section(
            page,
            "Estado tecnico",
            "Informacion de conectividad y chequeos rapidos del entorno local.",
        )
        com_card = ctk.CTkFrame(status_section, fg_color=CARD_ALT, corner_radius=18)
        com_card.pack(fill="x", padx=18, pady=(0, 18))
        ctk.CTkLabel(
            com_card,
            text="Puertos COM disponibles",
            font=ctk.CTkFont("Poppins", 15, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=18, pady=(18, 4))
        self.widgets["label_puertos"] = ctk.CTkLabel(
            com_card,
            text="Cargando...",
            font=ctk.CTkFont("Poppins", 14),
            text_color=MUTED,
            wraplength=880,
            justify="left",
        )
        self.widgets["label_puertos"].pack(anchor="w", padx=18, pady=(0, 14))
        ctk.CTkButton(
            com_card,
            text="Actualizar puertos",
            command=self.detectar_puertos_com,
            font=("Poppins", 14),
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            corner_radius=12,
            height=40,
        ).pack(anchor="w", padx=18, pady=(0, 18))

        action_section = self._build_section(
            page,
            "Acciones frecuentes",
            "Atajos para tareas de diagnostico y navegacion operativa.",
        )
        actions_row = ctk.CTkFrame(action_section, fg_color="transparent")
        actions_row.pack(fill="x", padx=18, pady=(0, 18))

        testeo_card = ctk.CTkFrame(actions_row, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
        testeo_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(
            testeo_card,
            text="Modo Testeo",
            font=ctk.CTkFont("Poppins", 17, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=18, pady=(18, 4))
        ctk.CTkLabel(
            testeo_card,
            text="Abre la herramienta externa de testeo del puesto si esta instalada en la ruta esperada.",
            font=ctk.CTkFont("Poppins", 12),
            text_color=MUTED,
            wraplength=360,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))
        ctk.CTkButton(
            testeo_card,
            text="Ejecutar Testeo",
            command=self.abrir_testeo,
            font=("Poppins", 14),
            fg_color=WARNING,
            hover_color=WARNING_HOVER,
            corner_radius=12,
            height=40,
        ).pack(anchor="w", padx=18, pady=(0, 18))

        nav_card = ctk.CTkFrame(actions_row, fg_color=CARD_ALT, corner_radius=18, border_width=1, border_color=BORDER)
        nav_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        ctk.CTkLabel(
            nav_card,
            text="Continuar con operacion",
            font=ctk.CTkFont("Poppins", 17, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=18, pady=(18, 4))
        ctk.CTkLabel(
            nav_card,
            text="Accede al panel de tags, potencia de antena y movimiento de archivos DAT.",
            font=ctk.CTkFont("Poppins", 12),
            text_color=MUTED,
            wraplength=360,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))
        ctk.CTkButton(
            nav_card,
            text="Ir a operacion y archivos",
            command=lambda: self.show_page(1),
            font=("Poppins", 14),
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            corner_radius=12,
            height=40,
        ).pack(anchor="w", padx=18, pady=(0, 18))

        return page

    def _build_operations_page(self):
        page = self._build_page_shell()

        tags_section = self._build_section(
            page,
            "Estado de tags",
            "Control rapido de tamano y fecha de modificacion de los archivos de tags principales.",
        )
        tags_row = ctk.CTkFrame(tags_section, fg_color="transparent")
        tags_row.pack(fill="x", padx=18, pady=(0, 12))
        self._create_file_card(tags_row, "LMTAGS_AUBASA.DAT", "label_tag1_info")
        self._create_file_card(tags_row, "LMTAGSPAT_AUBASA.DAT", "label_tag2_info")
        ctk.CTkButton(
            tags_section,
            text="Actualizar estado de tags",
            command=self.actualizar_info_tags,
            font=("Poppins", 14),
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            corner_radius=12,
            height=40,
        ).pack(anchor="w", padx=18, pady=(0, 18))

        antenna_section = self._build_section(
            page,
            "Configuracion de antena",
            "Lectura de IP remota y actualizacion controlada del nivel de potencia.",
        )
        info_row = ctk.CTkFrame(antenna_section, fg_color="transparent")
        info_row.pack(fill="x", padx=18, pady=(0, 12))
        self._create_info_tile(info_row, "IP antena", "label_antena_ip")
        self._create_info_tile(info_row, "Potencia actual", "label_potencia")

        form = ctk.CTkFrame(antenna_section, fg_color=CARD_ALT, corner_radius=18)
        form.pack(fill="x", padx=18, pady=(0, 18))
        ctk.CTkLabel(
            form,
            text="Nueva potencia",
            font=ctk.CTkFont("Poppins", 14, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=18, pady=(18, 8))
        self.widgets["potencia_entry"] = ctk.CTkEntry(
            form,
            placeholder_text="Valor entre 0 y 30",
            font=("Poppins", 14),
            height=40,
        )
        self.widgets["potencia_entry"].pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkLabel(
            form,
            text="Solo se aceptan numeros enteros entre 0 y 30.",
            font=ctk.CTkFont("Poppins", 12),
            text_color=MUTED,
        ).pack(anchor="w", padx=18, pady=(0, 14))
        buttons_row = ctk.CTkFrame(form, fg_color="transparent")
        buttons_row.pack(fill="x", padx=18, pady=(0, 18))
        ctk.CTkButton(
            buttons_row,
            text="Leer configuracion",
            command=self.actualizar_datos_antena,
            font=("Poppins", 14),
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            corner_radius=12,
            height=40,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            buttons_row,
            text="Guardar potencia",
            command=self.modificar_potencia,
            font=("Poppins", 14),
            fg_color=SUCCESS,
            hover_color=SUCCESS_HOVER,
            corner_radius=12,
            height=40,
        ).pack(side="left")
        ctk.CTkButton(
            buttons_row,
            text="Abrir configurador de antena",
            command=self.abrir_configurador_antena,
            font=("Poppins", 14),
            fg_color=INFO,
            hover_color=INFO_HOVER,
            corner_radius=12,
            height=40,
        ).pack(side="left", padx=(10, 0))

        files_section = self._build_section(
            page,
            "Movimiento de archivos DAT",
            "Permite seleccionar origen y destino para mover archivos y agruparlos en carpetas fechadas.",
        )
        form_card = ctk.CTkFrame(files_section, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
        form_card.pack(fill="x", padx=18, pady=(0, 18))
        ctk.CTkLabel(
            form_card,
            text="Ruta de origen",
            font=ctk.CTkFont("Poppins", 13, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=18, pady=(18, 6))
        ctk.CTkEntry(
            form_card,
            textvariable=self.source_var,
            font=("Poppins", 14),
            height=40,
        ).pack(fill="x", padx=18, pady=(0, 12))
        ctk.CTkLabel(
            form_card,
            text="Ruta de destino",
            font=ctk.CTkFont("Poppins", 13, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=18, pady=(0, 6))
        ctk.CTkEntry(
            form_card,
            textvariable=self.dest_var,
            placeholder_text="Selecciona una carpeta de destino",
            font=("Poppins", 14),
            height=40,
        ).pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkLabel(
            form_card,
            text="El sistema crea una carpeta con fecha y mueve todos los .dat encontrados en el origen.",
            font=ctk.CTkFont("Poppins", 12),
            text_color=MUTED,
            wraplength=880,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 14))
        files_actions = ctk.CTkFrame(form_card, fg_color="transparent")
        files_actions.pack(fill="x", padx=18, pady=(0, 18))
        ctk.CTkButton(
            files_actions,
            text="Seleccionar destino",
            command=self.seleccionar_destino,
            font=("Poppins", 14),
            fg_color=NEUTRAL,
            hover_color=NEUTRAL_HOVER,
            corner_radius=12,
            height=40,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            files_actions,
            text="Mover archivos DAT",
            command=self.move_files,
            font=("Poppins", 14),
            fg_color=WARNING,
            hover_color=WARNING_HOVER,
            corner_radius=12,
            height=40,
        ).pack(side="left")

        return page

    def _create_file_card(self, parent, title, value_key):
        card = ctk.CTkFrame(parent, fg_color=CARD_ALT, corner_radius=18, border_width=1, border_color=BORDER)
        card.pack(side="left", fill="both", expand=True, padx=6, pady=(0, 6))
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont("Poppins", 14, "bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=16, pady=(16, 8))
        label = ctk.CTkLabel(
            card,
            text="Cargando...",
            font=ctk.CTkFont("Poppins", 13),
            text_color=MUTED,
            wraplength=400,
            justify="left",
        )
        label.pack(anchor="w", padx=16, pady=(0, 16))
        self.widgets[value_key] = label

    def _create_info_tile(self, parent, title, value_key):
        card = ctk.CTkFrame(parent, fg_color=CARD_ALT, corner_radius=18)
        card.pack(side="left", fill="both", expand=True, padx=6, pady=(0, 6))
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont("Poppins", 13, "bold"),
            text_color=MUTED,
        ).pack(anchor="w", padx=16, pady=(16, 6))
        label = ctk.CTkLabel(
            card,
            text="Cargando...",
            font=ctk.CTkFont("Poppins", 18, "bold"),
            text_color=TEXT,
            wraplength=360,
            justify="left",
        )
        label.pack(anchor="w", padx=16, pady=(0, 16))
        self.widgets[value_key] = label

    def _schedule_initial_load(self):
        self.after(300, self.obtener_info_sistema)
        self.after(400, self.detectar_puertos_com)
        self.after(500, self.actualizar_info_tags)
        self.after(600, self.actualizar_datos_antena)

    def show_page(self, index):
        self.current_page = index
        for page in self.pages.values():
            page.grid_remove()
        self.pages[index].grid()
        self.header_title.configure(text=self.page_titles[index])
        self.header_subtitle.configure(text=self.page_subtitles[index])

        for button_index, button in self.nav_buttons.items():
            is_active = button_index == index
            button.configure(
                fg_color="#12213a" if is_active else "transparent",
                text_color=TEXT if is_active else "#dbe4f0",
                border_width=1 if is_active else 0,
                border_color=BORDER,
            )
        self.persist_settings()

    def _set_dashboard_visibility(self, visible):
        if visible:
            self.sidebar.grid()
            self.content.grid()
        else:
            self.sidebar.grid_remove()
            self.content.grid_remove()

    def handle_login(self, username, password):
        configured_username = self.settings["auth"]["username"]
        configured_password = self.settings["auth"]["password"]
        if username != configured_username or password != configured_password:
            self.notify("Intento de acceso invalido.", "error")
            return False, "Credenciales invalidas"

        self.handle_login_success(username)
        return True, None

    def handle_login_success(self, username):
        self.authenticated = True
        self.settings["ui"]["last_username"] = username
        self.login_overlay.destroy()
        self._set_dashboard_visibility(True)
        self.show_page(self.settings["ui"]["last_page"])
        self.set_status("Sesion iniciada correctamente. Cargando estado del puesto...", "info")
        self.notify("Sesion iniciada correctamente.", "success")
        self._schedule_initial_load()

    def set_status(self, message, status_type="info"):
        color_map = {
            "info": ("#0f1b31", INFO),
            "success": ("#10261b", SUCCESS),
            "warning": ("#2b1b0f", WARNING),
            "error": ("#2d1320", "#ef4444"),
        }
        bg_color, dot_color = color_map.get(status_type, color_map["info"])
        self.status_banner.configure(fg_color=bg_color)
        self.status_dot.configure(fg_color=dot_color)
        self.status_label.configure(text=message)
        self.update_idletasks()

    def set_busy(self, message):
        self.configure(cursor="watch")
        self.set_status(message, "info")
        self.update_idletasks()

    def clear_busy(self):
        self.configure(cursor="")
        self.update_idletasks()

    def notify(self, message, level="info", duration_ms=3200):
        color_map = {
            "info": ("#0f1b31", INFO),
            "success": ("#10261b", SUCCESS),
            "warning": ("#2b1b0f", WARNING),
            "error": ("#2d1320", "#ef4444"),
        }
        bg_color, dot_color = color_map.get(level, color_map["info"])
        toast = ctk.CTkFrame(
            self.toast_host,
            fg_color=bg_color,
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
        )
        toast.pack(anchor="e", pady=(0, 10))
        dot = ctk.CTkFrame(toast, width=10, height=10, corner_radius=999, fg_color=dot_color)
        dot.pack(side="left", padx=(14, 10), pady=14)
        ctk.CTkLabel(
            toast,
            text=message,
            font=ctk.CTkFont("Poppins", 12, "bold"),
            text_color=TEXT,
            wraplength=300,
            justify="left",
        ).pack(side="left", padx=(0, 14), pady=12)

        self.toast_counter += 1
        toast_id = self.toast_counter
        after_id = self.after(duration_ms, lambda: self._dismiss_toast(toast_id))
        self.toasts[toast_id] = (toast, after_id)

    def _dismiss_toast(self, toast_id):
        toast_data = self.toasts.pop(toast_id, None)
        if not toast_data:
            return
        toast, _after_id = toast_data
        if toast.winfo_exists():
            toast.destroy()

    def persist_settings(self):
        self.settings["paths"]["source_path"] = self.source_var.get().strip()
        self.settings["paths"]["destination_path"] = self.dest_var.get().strip()
        self.settings["ui"]["last_page"] = self.current_page
        save_settings(self.settings)

    def seleccionar_destino(self):
        selected_dir = filedialog.askdirectory(title="Seleccionar carpeta destino")
        if selected_dir:
            self.dest_var.set(selected_dir)
            self.persist_settings()
            self.set_status(f"Destino seleccionado: {selected_dir}", "info")
            self.notify("Carpeta de destino actualizada.", "info")

    def obtener_info_sistema(self):
        try:
            self.set_busy("Actualizando informacion del sistema...")
            nombre_equipo = socket.gethostname()
            ip_local = socket.gethostbyname(nombre_equipo)
            ip_split = ip_local.split(".")
            self.current_via_number = self._parse_via_number(ip_local)
            via = (
                f"Via {self.current_via_number} - La Huella"
                if self.current_via_number is not None
                else "Via Desconocida"
            )
            self.widgets["label_equipo"].configure(text=nombre_equipo)
            self.widgets["label_ip"].configure(text=ip_local)
            self.widgets["label_via"].configure(text=via)
            self.set_status("Informacion del sistema actualizada.", "success")
            self.notify("Informacion del sistema actualizada.", "success")
        except Exception as exc:
            self.set_status(f"No se pudo actualizar la informacion del sistema: {exc}", "error")
            messagebox.showerror("Error", f"No se pudo obtener la informacion de red: {exc}")
        finally:
            self.clear_busy()

    def detectar_puertos_com(self):
        try:
            self.set_busy("Buscando puertos COM disponibles...")
            puertos = serial.tools.list_ports.comports()
            disponibles = [puerto.device for puerto in puertos]
            texto = ", ".join(disponibles) if disponibles else "Ninguno"
            self.widgets["label_puertos"].configure(text=texto)
            status_type = "success" if disponibles else "warning"
            self.set_status(f"Puertos detectados: {texto}.", status_type)
            self.notify(f"Puertos detectados: {texto}.", status_type)
        finally:
            self.clear_busy()

    def actualizar_datos_antena(self):
        try:
            self.set_busy("Leyendo configuracion de antena...")
            archivo_ini = buscar_archivo_ini()
            remote_host, potencia = leer_configuracion(archivo_ini)
            self.widgets["label_antena_ip"].configure(text=remote_host)
            self.widgets["label_potencia"].configure(text=potencia)
            self.set_status("Configuracion de antena actualizada.", "success")
            self.notify("Configuracion de antena actualizada.", "success")
        except Exception as exc:
            self.set_status(f"No se pudo leer la configuracion de antena: {exc}", "error")
            messagebox.showerror("Error", str(exc))
        finally:
            self.clear_busy()

    def modificar_potencia(self):
        try:
            archivo_ini = buscar_archivo_ini()
            nueva_potencia = self.widgets["potencia_entry"].get().strip()
            if not nueva_potencia:
                self.set_status("Ingresa un valor de potencia antes de guardar.", "warning")
                self.notify("Ingresa un valor de potencia antes de guardar.", "warning")
                self.widgets["potencia_entry"].focus()
                return
            if not nueva_potencia.isdigit():
                self.set_status("La potencia ingresada no es valida. Debe ser un numero entero.", "error")
                self.notify("La potencia debe ser un numero entero.", "error")
                self.widgets["potencia_entry"].focus()
                return
            if not messagebox.askyesno("Confirmar", f"Se actualizara la potencia a {nueva_potencia}. Deseas continuar?"):
                self.set_status("Actualizacion de potencia cancelada por el usuario.", "warning")
                self.notify("Actualizacion de potencia cancelada.", "warning")
                return
            self.set_busy(f"Actualizando potencia a {nueva_potencia}...")
            editar_potencia(archivo_ini, nueva_potencia)
            self.actualizar_datos_antena()
            self.widgets["potencia_entry"].delete(0, "end")
            self.set_status(f"Potencia actualizada correctamente a {nueva_potencia}.", "success")
            self.notify(f"Potencia actualizada a {nueva_potencia}.", "success")
        except Exception as exc:
            self.set_status(f"No se pudo actualizar la potencia: {exc}", "error")
            messagebox.showerror("Error", str(exc))
        finally:
            self.clear_busy()

    def abrir_testeo(self):
        testeo_path = self.settings["paths"]["testeo_path"]
        if not os.path.exists(testeo_path):
            self.set_status("No se encontro Testeo.exe en la ruta configurada.", "error")
            messagebox.showerror("Error", "No se encuentra Testeo.exe")
            return
        try:
            self.set_busy("Abriendo herramienta de testeo...")
            subprocess.run([testeo_path], check=True)
            self.set_status("Herramienta de testeo iniciada.", "success")
            self.notify("Herramienta de testeo iniciada.", "success")
        except Exception as exc:
            self.set_status(f"No se pudo abrir la herramienta de testeo: {exc}", "error")
            messagebox.showerror("Error", str(exc))
        finally:
            self.clear_busy()

    def _parse_via_number(self, ip_local):
        ip_split = ip_local.split(".")
        if len(ip_split) != 4:
            return None
        last_octet = ip_split[3]
        if not last_octet.isdigit():
            return None
        return int(last_octet)

    def abrir_configurador_antena(self):
        via_number = self.current_via_number
        antenna_settings = self.settings["antenna"]
        path_settings = self.settings["paths"]
        if via_number is None:
            self.set_status("No se pudo determinar la via actual para abrir el configurador.", "warning")
            self.notify("Actualiza la informacion del sistema para detectar la via.", "warning")
            return

        if via_number in set(antenna_settings["reader_test_vias"]):
            program_path = path_settings["reader_test_path"]
            program_name = "ReaderTest.exe"
        elif via_number in set(antenna_settings["uip_reader_vias"]):
            program_path = path_settings["uip_reader_path"]
            program_name = "UipReader01demomain.exe"
        else:
            self.set_status(f"La via {via_number} no tiene un configurador asignado.", "warning")
            self.notify(f"No hay configurador definido para la via {via_number}.", "warning")
            return

        if not os.path.exists(program_path):
            self.set_status(f"No se encontro {program_name} en la ruta configurada.", "error")
            messagebox.showerror("Error", f"No se encuentra {program_name} en {program_path}")
            return

        try:
            self.set_busy(f"Abriendo configurador de antena para la via {via_number}...")
            subprocess.run([program_path], check=True)
            self.set_status(f"Configurador de antena abierto para la via {via_number}.", "success")
            self.notify(f"Configurador abierto: {program_name}.", "success")
        except Exception as exc:
            self.set_status(f"No se pudo abrir el configurador de antena: {exc}", "error")
            messagebox.showerror("Error", str(exc))
        finally:
            self.clear_busy()

    def actualizar_info_tags(self):
        try:
            self.set_busy("Consultando estado de archivos de tags...")
            info_tags = obtener_info_tags()
            self.widgets["label_tag1_info"].configure(
                text=f"{info_tags[0]['tamano']} MB - {info_tags[0]['ultima_mod']}"
            )
            self.widgets["label_tag2_info"].configure(
                text=f"{info_tags[1]['tamano']} MB - {info_tags[1]['ultima_mod']}"
            )
            self.set_status("Estado de tags actualizado.", "success")
            self.notify("Estado de tags actualizado.", "success")
        except Exception as exc:
            self.set_status(f"No se pudo actualizar el estado de tags: {exc}", "error")
            messagebox.showerror("Error", str(exc))
        finally:
            self.clear_busy()

    def move_files(self):
        source_path = self.source_var.get().strip()
        destination_path = self.dest_var.get().strip()

        if not source_path:
            self.set_status("Debes indicar una ruta de origen.", "warning")
            self.notify("Ingresa una ruta de origen.", "warning")
            return

        if not os.path.exists(source_path):
            self.set_status("La ruta de origen no existe. Selecciona otra carpeta.", "warning")
            self.notify("La ruta de origen no existe. Selecciona otra carpeta.", "warning")
            source_path = filedialog.askdirectory(title="Seleccionar carpeta origen")
            if not source_path:
                self.set_status("Seleccion de carpeta de origen cancelada.", "warning")
                self.notify("Seleccion de origen cancelada.", "warning")
                return
            self.source_var.set(source_path)
            self.persist_settings()

        if not destination_path:
            self.set_status("Debes seleccionar una carpeta de destino antes de mover archivos.", "warning")
            self.notify("Selecciona una carpeta de destino.", "warning")
            return

        if not os.path.exists(destination_path):
            self.set_status("La carpeta de destino indicada no es valida.", "error")
            self.notify("La carpeta de destino indicada no es valida.", "error")
            return

        if not messagebox.askyesno(
            "Confirmar movimiento",
            "Se moveran todos los archivos .dat encontrados en la carpeta origen. Deseas continuar?",
        ):
            self.set_status("Movimiento de archivos cancelado por el usuario.", "warning")
            self.notify("Movimiento de archivos cancelado.", "warning")
            return

        try:
            self.set_busy("Moviendo archivos DAT. Esto puede tardar unos segundos...")
            final_folder = find_and_move_files(source_path, destination_path)
            self.persist_settings()
            if final_folder:
                self.set_status(f"Archivos movidos correctamente a {final_folder}.", "success")
                self.notify(f"Archivos movidos a {final_folder}.", "success", duration_ms=4200)
            else:
                self.set_status("No se encontraron archivos .dat para mover.", "warning")
                self.notify("No se encontraron archivos .dat para mover.", "warning")
        except Exception as exc:
            self.set_status(f"No se pudieron mover los archivos: {exc}", "error")
            messagebox.showerror("Error", str(exc))
        finally:
            self.clear_busy()

    def close_window(self):
        for _toast_id, (_toast, after_id) in list(self.toasts.items()):
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self.persist_settings()
        self.quit()
        self.destroy()


def run_app():
    ctk.set_appearance_mode("dark")
    apply_theme()
    app = DashboardApp()
    app.mainloop()


def iniciar_dashboard():
    run_app()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    run_app()
