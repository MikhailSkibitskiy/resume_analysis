import tkinter as tk
from tkinter import ttk, messagebox
from auth_system import AuthSystem


class AdminGUI:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.auth = AuthSystem()

        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        self.root.title(f"Панель администратора - {self.username}")
        self.root.geometry("800x600")

        # Список пользователей
        self.users_frame = ttk.LabelFrame(self.root, text="Список пользователей")
        self.users_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(
            self.users_frame,
            columns=("username", "role"),
            show="headings"
        )
        self.tree.heading("username", text="Логин")
        self.tree.heading("role", text="Роль")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Панель управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(control_frame, text="Логин:").pack(side="left", padx=5)
        self.edit_username = ttk.Entry(control_frame)
        self.edit_username.pack(side="left", padx=5, fill="x", expand=True)

        ttk.Label(control_frame, text="Пароль:").pack(side="left", padx=5)
        self.edit_password = ttk.Entry(control_frame)
        self.edit_password.pack(side="left", padx=5, fill="x", expand=True)

        ttk.Label(control_frame, text="Роль:").pack(side="left", padx=5)
        self.edit_role = ttk.Combobox(
            control_frame,
            values=["user", "admin"],
            state="readonly"
        )
        self.edit_role.pack(side="left", padx=5)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, fill="x")

        ttk.Button(
            button_frame,
            text="Обновить данные",
            command=self.update_user
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Удалить пользователя",
            command=self.delete_user
        ).pack(side="left", padx=5)

        # Привязка события выбора в Treeview
        self.tree.bind("<<TreeviewSelect>>", self.on_user_select)

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        users = self.auth.get_all_users()
        for user in users:
            if user["role"] != "developer":  # Админ не может управлять разработчиками
                self.tree.insert("", "end", values=(user["username"], user["role"]))

    def on_user_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        username = self.tree.item(selected[0])["values"][0]
        self.edit_username.delete(0, tk.END)
        self.edit_username.insert(0, username)

        # Очищаем пароль и роль
        self.edit_password.delete(0, tk.END)
        self.edit_role.set("")

    def update_user(self):
        old_username = self.tree.item(self.tree.selection()[0])["values"][0] if self.tree.selection() else None
        new_username = self.edit_username.get()
        new_password = self.edit_password.get()
        new_role = self.edit_role.get()

        if not old_username:
            messagebox.showerror("Ошибка", "Выберите пользователя для изменения")
            return

        result = self.auth.update_user(
            old_username,
            new_username if new_username != old_username else None,
            new_password if new_password else None,
            new_role if new_role else None
        )

        messagebox.showinfo("Результат", result)
        self.load_users()

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления")
            return

        username = self.tree.item(selected[0])["values"][0]

        if messagebox.askyesno(
                "Подтверждение",
                f"Вы уверены, что хотите удалить пользователя {username}?"
        ):
            result = self.auth.delete_user(username)
            messagebox.showinfo("Результат", result)
            self.load_users()