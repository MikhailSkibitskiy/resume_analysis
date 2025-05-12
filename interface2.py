import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import time
import joblib
import re
import string
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer


class ResumeAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор резюме преподавателей")
        self.root.geometry("800x600")
        self.start_time = time.time()

        # Стиль в постельных тонах
        self.bg_colors = {
            "default": "#FFF5F5",
            "lavender": "#F5F0FF",
            "mint": "#F0FFF5",
            "peach": "#FFF0F5"
        }
        self.current_bg = "default"
        self.font_size = "medium"
        self.font_weight = "normal"

        # Загрузка модели (замените на свои пути)
        try:
            self.model = joblib.load('модель_преподавателей.pkl')
            self.vectorizer = joblib.load('векторизатор.pkl')
        except:
            messagebox.showerror("Ошибка", "Не удалось загрузить модель!")
            self.root.destroy()

        # Инициализация NLTK
        try:
            self.stemmer = SnowballStemmer("russian")
            self.russian_stopwords = stopwords.words("russian")
        except:
            messagebox.showerror("Ошибка", "Проблема с загрузкой NLTK данных!")
            self.root.destroy()

        self.setup_ui()
        self.show_home_screen()

    def setup_ui(self):
        # Боковая панель
        self.sidebar = tk.Frame(self.root, bg="#E8D5E2", width=150)
        self.sidebar.pack(side="left", fill="y")

        # Кнопки навигации
        buttons = [
            ("Главная", self.show_home_screen),
            ("Настройки", self.show_settings),
            ("О программе", self.show_about),
            ("Выход", self.exit_app)
        ]

        for text, command in buttons:
            if text == "Выход":
                btn = tk.Button(self.sidebar, text=text, command=command,
                                bg="#FF6B6B", fg="white", relief="flat",
                                font=("Arial", 10, "bold"))
            else:
                btn = tk.Button(self.sidebar, text=text, command=command,
                                bg="#E8D5E2", fg="#5D3B5D", relief="flat",
                                font=("Arial", 10))
            btn.pack(fill="x", pady=5, padx=5)

        # Основная область
        self.main_area = tk.Frame(self.root, bg=self.bg_colors[self.current_bg])
        self.main_area.pack(side="right", fill="both", expand=True)

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def update_style(self):
        bg_color = self.bg_colors[self.current_bg]
        self.main_area.config(bg=bg_color)

        font_config = ("Arial", self.get_font_size(), self.font_weight)

        for widget in self.main_area.winfo_children():
            if isinstance(widget, (tk.Label, tk.Button)):
                widget.config(bg=bg_color, font=font_config)
            elif isinstance(widget, tk.Text):
                widget.config(font=font_config)

    def get_font_size(self):
        sizes = {"small": 10, "medium": 12, "large": 14}
        return sizes[self.font_size]

    def show_home_screen(self):
        self.clear_main_area()

        # Приветственный экран
        welcome_frame = tk.Frame(self.main_area, bg=self.bg_colors[self.current_bg])
        welcome_frame.pack(pady=50)

        today = datetime.datetime.now().strftime("%d.%m.%Y")
        tk.Label(welcome_frame, text=f"Добро пожаловать!\nСегодня {today}",
                 font=("Arial", 16, "bold"), bg=self.bg_colors[self.current_bg]).pack(pady=20)

        tk.Button(welcome_frame, text="Анализировать резюме", command=self.show_analyzer,
                  bg="#9F86C0", fg="white", font=("Arial", 12)).pack(pady=20)

    def show_analyzer(self):
        self.clear_main_area()

        tk.Label(self.main_area, text="Введите текст резюме:",
                 font=("Arial", self.get_font_size(), self.font_weight),
                 bg=self.bg_colors[self.current_bg]).pack(pady=10)

        self.text_input = tk.Text(self.main_area, height=15, width=70,
                                  font=("Arial", self.get_font_size()),
                                  wrap="word", padx=10, pady=10)
        self.text_input.pack(pady=10)

        # Добавляем контекстное меню для копирования/вставки
        self.setup_text_context_menu()

        tk.Button(self.main_area, text="Проверить", command=self.analyze_resume,
                  bg="#9F86C0", fg="white", font=("Arial", 12)).pack(pady=10)

    def setup_text_context_menu(self):
        context_menu = tk.Menu(self.text_input, tearoff=0)
        context_menu.add_command(label="Копировать", command=lambda: self.text_input.event_generate("<<Copy>>"))
        context_menu.add_command(label="Вставить", command=lambda: self.text_input.event_generate("<<Paste>>"))
        context_menu.add_command(label="Вырезать", command=lambda: self.text_input.event_generate("<<Cut>>"))

        def show_context_menu(event):
            context_menu.tk_popup(event.x_root, event.y_root)

        self.text_input.bind("<Button-3>", show_context_menu)

    def analyze_resume(self):
        text = self.text_input.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showerror("Ошибка", "Введите текст резюме!")
            return

        try:
            # Предобработка текста
            processed_text = self.preprocess_text(text)
            text_vec = self.vectorizer.transform([processed_text])
            probability = self.model.predict_proba(text_vec)[0][1] * 100

            # Показ результата
            self.show_result(probability)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def preprocess_text(self, text):
        if not isinstance(text, str):
            return ""

        text = text.lower()
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        tokens = []
        for token in text.split():
            if token not in self.russian_stopwords:
                token = self.stemmer.stem(token)
                tokens.append(token)

        return " ".join(tokens)

    def show_result(self, probability):
        self.clear_main_area()

        tk.Label(self.main_area, text="Результат проверки:",
                 font=("Arial", 14, "bold"),
                 bg=self.bg_colors[self.current_bg]).pack(pady=20)

        tk.Label(self.main_area, text=f"Вероятность: {probability:.1f}%",
                 font=("Arial", 16, "bold"),
                 bg=self.bg_colors[self.current_bg]).pack(pady=10)

        if probability > 70:
            conclusion = "Это резюме преподавателя!"
        elif probability > 30:
            conclusion = "Возможно, это резюме преподавателя"
        else:
            conclusion = "Это не похоже на резюме преподавателя"

        tk.Label(self.main_area, text=conclusion,
                 font=("Arial", 14),
                 bg=self.bg_colors[self.current_bg]).pack(pady=10)

        tk.Button(self.main_area, text="В начало", command=self.show_home_screen,
                  bg="#9F86C0", fg="white", font=("Arial", 12)).pack(pady=20)

    def show_settings(self):
        self.clear_main_area()

        tk.Label(self.main_area, text="Настройки",
                 font=("Arial", 16, "bold"),
                 bg=self.bg_colors[self.current_bg]).pack(pady=20)

        # Цветовая схема
        tk.Label(self.main_area, text="Цвет фона:",
                 font=("Arial", self.get_font_size(), self.font_weight),
                 bg=self.bg_colors[self.current_bg]).pack(pady=5)

        color_frame = tk.Frame(self.main_area, bg=self.bg_colors[self.current_bg])
        color_frame.pack()

        for color_name, color_code in self.bg_colors.items():
            btn = tk.Button(color_frame, text=color_name.capitalize(),
                            command=lambda c=color_name: self.change_bg_color(c),
                            bg=color_code, fg="#5D3B5D", font=("Arial", 10))
            btn.pack(side="left", padx=5, pady=5)

        # Размер шрифта
        tk.Label(self.main_area, text="Размер шрифта:",
                 font=("Arial", self.get_font_size(), self.font_weight),
                 bg=self.bg_colors[self.current_bg]).pack(pady=5)

        size_frame = tk.Frame(self.main_area, bg=self.bg_colors[self.current_bg])
        size_frame.pack()

        for size in ["small", "medium", "large"]:
            btn = tk.Button(size_frame, text=size.capitalize(),
                            command=lambda s=size: self.change_font_size(s),
                            bg="#E8D5E2", fg="#5D3B5D", font=("Arial", 10))
            btn.pack(side="left", padx=5, pady=5)

        # Толщина шрифта
        tk.Label(self.main_area, text="Толщина шрифта:",
                 font=("Arial", self.get_font_size(), self.font_weight),
                 bg=self.bg_colors[self.current_bg]).pack(pady=5)

        weight_frame = tk.Frame(self.main_area, bg=self.bg_colors[self.current_bg])
        weight_frame.pack()

        for weight in ["normal", "bold"]:
            btn = tk.Button(weight_frame, text=weight.capitalize(),
                            command=lambda w=weight: self.change_font_weight(w),
                            bg="#E8D5E2", fg="#5D3B5D", font=("Arial", 10))
            btn.pack(side="left", padx=5, pady=5)

    def change_bg_color(self, color_name):
        self.current_bg = color_name
        self.update_style()

    def change_font_size(self, size):
        self.font_size = size
        self.update_style()

    def change_font_weight(self, weight):
        self.font_weight = weight
        self.update_style()

    def show_about(self):
        self.clear_main_area()

        tk.Label(self.main_area, text="О программе",
                 font=("Arial", 16, "bold"),
                 bg=self.bg_colors[self.current_bg]).pack(pady=20)

        version = "Beta 0.2.7"
        window_size = f"{self.root.winfo_width()}x{self.root.winfo_height()}"
        uptime = f"{int(time.time() - self.start_time)} секунд"

        info_text = f"""
Версия: {version}
Размер окна: {window_size}
Программа работает: {uptime}

Анализатор резюме преподавателей
Ораукл найма МС. Разработано с использованием Python
"""

        tk.Label(self.main_area, text=info_text,
                 font=("Arial", self.get_font_size()),
                 bg=self.bg_colors[self.current_bg], justify="left").pack(pady=20)

        tk.Button(self.main_area, text="Обновить", command=self.show_about,
                  bg="#9F86C0", fg="white", font=("Arial", 12)).pack(pady=10)

    def exit_app(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeAnalyzerApp(root)
    root.mainloop()
