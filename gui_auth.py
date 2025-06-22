#Система регистрации и входа. (Скибицкий М. Е.)

import tkinter as tk
from tkinter import ttk, messagebox
from auth_system import AuthSystem


class AuthGUI:
    def __init__(self, root, on_successful_login):
        self.root = root
        self.auth = AuthSystem()
        self.on_successful_login = on_successful_login

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Вход / Регистрация")
        self.root.geometry("400x400")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Вкладка входа
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Вход")
        self._setup_login_tab()

        # Вкладка регистрации
        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="Регистрация")
        self._setup_register_tab()

    def _setup_login_tab(self):
        ttk.Label(self.login_frame, text="Логин:").pack(pady=(20, 5))
        self.login_username = ttk.Entry(self.login_frame)
        self.login_username.pack(pady=5, padx=20, fill="x")

        ttk.Label(self.login_frame, text="Пароль:").pack(pady=(10, 5))
        self.login_password = ttk.Entry(self.login_frame, show="*")
        self.login_password.pack(pady=5, padx=20, fill="x")

        ttk.Button(
            self.login_frame,
            text="Войти",
            command=self._handle_login
        ).pack(pady=20)

    def _setup_register_tab(self):
        ttk.Label(self.register_frame, text="Логин:").pack(pady=(20, 5))
        self.register_username = ttk.Entry(self.register_frame)
        self.register_username.pack(pady=5, padx=20, fill="x")

        ttk.Label(self.register_frame, text="Пароль:").pack(pady=(10, 5))
        self.register_password = ttk.Entry(self.register_frame, show="*")
        self.register_password.pack(pady=5, padx=20, fill="x")

        ttk.Label(self.register_frame, text="Роль:").pack(pady=(10, 5))

        self.role_var = tk.StringVar(value="user")
        roles_frame = ttk.Frame(self.register_frame)
        roles_frame.pack(pady=5)

        ttk.Radiobutton(
            roles_frame,
            text="Пользователь",
            variable=self.role_var,
            value="user"
        ).pack(side="left", padx=5)

        ttk.Radiobutton(
            roles_frame,
            text="Администратор",
            variable=self.role_var,
            value="admin"
        ).pack(side="left", padx=5)

        ttk.Radiobutton(
            roles_frame,
            text="Разработчик",
            variable=self.role_var,
            value="developer"
        ).pack(side="left", padx=5)

        ttk.Button(
            self.register_frame,
            text="Зарегистрироваться",
            command=self._handle_register
        ).pack(pady=20)

    def _handle_login(self):
        username = self.login_username.get()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        result = self.auth.login_user(username, password)

        if result["success"]:
            self.on_successful_login(
                username,
                result["role"],
                result["bg_color"],
                result["font_size"],
                result["font_weight"]
            )
        else:
            messagebox.showerror("Ошибка", result["message"])

    def _handle_register(self):
        username = self.register_username.get()
        password = self.register_password.get()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        result = self.auth.register_user(username, password, role)

        if result == "Успешная регистрация":
            messagebox.showinfo("Успех", result)
            self.notebook.select(0)  # Переключение на вкладку входа
            self.login_username.delete(0, tk.END)
            self.login_username.insert(0, username)
            self.login_password.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", result)
