#Система регистрации и входа. (Скибицкий М. Е.)

import json
import os
import re
from typing import Dict, List


class AuthSystem:
    def __init__(self):
        self.users_file = "users.json"
        self.initialize_system()
#я разработчик
    def initialize_system(self):
        if not os.path.exists(self.users_file):
            default_users = {
                "МихаилС": {
                    "password": "Скибицкий1",
                    "role": "developer",
                    "bg_color": "default",
                    "font_size": "medium",
                    "font_weight": "normal"
                }
            }
            self._save_users(default_users)

    #провера спика пользователей
    def _load_users(self) -> Dict:
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_users(self, users: Dict):
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)

    #длинна пароля
    def validate_password(self, password: str) -> bool:
        if len(password) < 6:
            return False
        if not re.search(r"\d", password):
            return False
        return True

    #регистрация
    def register_user(self, username: str, password: str, role: str) -> str:
        users = self._load_users()

        if username in users:
            return "Логин уже существует"

        if not self.validate_password(password):
            return "Пароль должен содержать минимум 6 символов и хотя бы одну цифру"

        role_counts = self._count_roles(users)

        if role == "user" and role_counts["user"] >= 15:
            return "Максимальное число пользователей (15)"
        elif role == "admin" and role_counts["admin"] >= 3:
            return "Максимальное число администраторов (3)"
        elif role == "developer" and role_counts["developer"] >= 1:
            return "Максимальное число разработчиков (1)"

        users[username] = {
            "password": password,
            "role": role,
            "bg_color": "default",
            "font_size": "medium",
            "font_weight": "normal"
        }

        self._save_users(users)
        return "Успешная регистрация"

    #провера количества ролей
    def _count_roles(self, users: Dict) -> Dict[str, int]:
        counts = {"user": 0, "admin": 0, "developer": 0}
        for user_data in users.values():
            counts[user_data["role"]] += 1
        return counts

    #проверка наличия пользователей
    def login_user(self, username: str, password: str) -> Dict:
        users = self._load_users()

        if username not in users:
            return {"success": False, "message": "Неверный логин"}

        if users[username]["password"] != password:
            return {"success": False, "message": "Неверный пароль"}

        return {
            "success": True,
            "role": users[username]["role"],
            "bg_color": users[username]["bg_color"],
            "font_size": users[username]["font_size"],
            "font_weight": users[username]["font_weight"]
        }

    #добавление новичка
    def get_all_users(self) -> List[Dict]:
        users = self._load_users()
        return [{"username": k, **v} for k, v in users.items()]

    #сохранение изменений от администратора и разработчика
    def update_user(self, username: str, new_username: str = None,
                    new_password: str = None, new_role: str = None) -> str:
        users = self._load_users()

        if username not in users:
            return "Пользователь не найден"

        if new_username and new_username != username:
            if new_username in users:
                return "Новый логин уже существует"
            users[new_username] = users.pop(username)
            username = new_username

        if new_password:
            if not self.validate_password(new_password):
                return "Пароль должен содержать минимум 6 символов и хотя бы одну цифру"
            users[username]["password"] = new_password

        if new_role:
            role_counts = self._count_roles(users)
            current_role = users[username]["role"]

            if new_role != current_role:
                if new_role == "user" and role_counts["user"] >= 15:
                    return "Максимальное число пользователей (15)"
                elif new_role == "admin" and role_counts["admin"] >= 3:
                    return "Максимальное число администраторов (3)"
                elif new_role == "developer" and role_counts["developer"] >= 1:
                    return "Максимальное число разработчиков (1)"

                users[username]["role"] = new_role

        self._save_users(users)
        return "Данные пользователя обновлены"

    #проверка при входе
    def delete_user(self, username: str) -> str:
        users = self._load_users()

        if username not in users:
            return "Пользователь не найден"

        if users[username]["role"] == "developer":
            dev_count = sum(1 for u in users.values() if u["role"] == "developer")
            if dev_count <= 1:
                return "Нельзя удалить последнего разработчика"

        del users[username]
        self._save_users(users)
        return "Пользователь удален"

    def update_settings(self, username: str, bg_color: str = None,
                        font_size: str = None, font_weight: str = None) -> str:
        users = self._load_users()

        if username not in users:
            return "Пользователь не найден"

        if bg_color:
            users[username]["bg_color"] = bg_color
        if font_size:
            users[username]["font_size"] = font_size
        if font_weight:
            users[username]["font_weight"] = font_weight

        self._save_users(users)
        return "Настройки обновлены"
