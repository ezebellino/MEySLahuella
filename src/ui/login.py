# src/login.py
import customtkinter as ctk
from tkinter import messagebox

class LoginWindow(ctk.CTk):
    def __init__(self, on_success_callback):
        super().__init__()
        self.title("MEyS - Login")
        self.geometry("400x480")
        self.resizable(False, False)
        self.on_success_callback = on_success_callback

        # Tipografías
        font_title = ctk.CTkFont(family="Poppins", size=22, weight="bold")
        font_entry = ctk.CTkFont(family="Poppins", size=14)

        # Frame
        frame = ctk.CTkFrame(master=self, corner_radius=15)
        frame.pack(padx=20, pady=40, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Iniciar Sesión", font=font_title).pack(pady=(20, 10))

        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Usuario", font=font_entry)
        self.username_entry.pack(pady=(10, 10), padx=20, fill="x")

        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", font=font_entry)
        self.password_entry.pack(pady=(0, 20), padx=20, fill="x")

        ctk.CTkButton(
            frame,
            text="Acceder",
            command=self.login_action,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=10
        ).pack(pady=10)

    def login_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Aquí puedes reemplazar con lógica real de autenticación
        if username == "admin" and password == "1234":
            self.destroy()  # Cierra login
            self.on_success_callback()  # Llama al dashboard
        else:
            messagebox.showerror("Error", "Credenciales inválidas")
