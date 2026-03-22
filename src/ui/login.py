import customtkinter as ctk
from tkinter import messagebox

from src.ui.theme_utils import apply_theme

apply_theme()


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_success_callback, on_cancel_callback):
        super().__init__(master, fg_color="transparent")
        self.on_success_callback = on_success_callback
        self.on_cancel_callback = on_cancel_callback
        self._build_ui()

    def _build_ui(self):
        self.pack(fill="both", expand=True, padx=24, pady=24)

        container = ctk.CTkFrame(self, width=420, corner_radius=22, fg_color="#0f172a")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container,
            text="MEyS",
            font=ctk.CTkFont(family="Poppins", size=28, weight="bold"),
            text_color="#f8fafc",
        ).pack(pady=(28, 4))

        ctk.CTkLabel(
            container,
            text="Ingreso al panel operativo",
            font=ctk.CTkFont(family="Poppins", size=14),
            text_color="#94a3b8",
        ).pack(pady=(0, 20))

        self.username_entry = ctk.CTkEntry(
            container,
            placeholder_text="Usuario",
            font=ctk.CTkFont(family="Poppins", size=14),
            width=300,
            height=42,
        )
        self.username_entry.pack(pady=(0, 12), padx=32)

        self.password_entry = ctk.CTkEntry(
            container,
            placeholder_text="Contrasena",
            show="*",
            font=ctk.CTkFont(family="Poppins", size=14),
            width=300,
            height=42,
        )
        self.password_entry.pack(pady=(0, 18), padx=32)

        ctk.CTkButton(
            container,
            text="Acceder",
            command=self.login_action,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=12,
            width=300,
            height=42,
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            container,
            text="Salir",
            command=self.on_cancel_callback,
            fg_color="#334155",
            hover_color="#475569",
            corner_radius=12,
            width=300,
            height=42,
        ).pack(pady=(0, 28))

        self.username_entry.bind("<Return>", lambda _event: self.login_action())
        self.password_entry.bind("<Return>", lambda _event: self.login_action())
        self.password_entry.bind("<Escape>", lambda _event: self.on_cancel_callback())
        self.username_entry.focus()

    def login_action(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "admin" and password == "1234":
            self.on_success_callback()
        else:
            messagebox.showerror("Error", "Credenciales invalidas")
