import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Конфигурация
FAVORITES_FILE = "favorites.json"
GITHUB_API_URL = "https://api.github.com/users/"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле ввода
        self.search_label = ttk.Label(self.root, text="Введите имя пользователя GitHub:")
        self.search_label.pack(pady=5)

        self.search_entry = ttk.Entry(self.root, width=50)
        self.search_entry.pack(pady=5)

        # Кнопка поиска
        self.search_button = ttk.Button(self.root, text="Найти", command=self.search_user)
        self.search_button.pack(pady=5)

        # Список результатов
        self.results_frame = ttk.Frame(self.root)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.results_tree = ttk.Treeview(self.results_frame, columns=("Login", "Name", "Location", "Public Repos"), show="headings")
        self.results_tree.heading("Login", text="Логин")
        self.results_tree.heading("Name", text="Имя")
        self.results_tree.heading("Location", text="Местоположение")
        self.results_tree.heading("Public Repos", text="Публичных репозиториев")
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Полоса прокрутки
        self.scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=self.scrollbar.set)

        # Кнопки управления избранным
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.pack(pady=10)

        self.add_favorite_button = ttk.Button(self.buttons_frame, text="Добавить в избранное", command=self.add_to_favorites)
        self.add_favorite_button.pack(side=tk.LEFT, padx=5)

        self.show_favorites_button = ttk.Button(self.buttons_frame, text="Показать избранное", command=self.show_favorites)
        self.show_favorites_button.pack(side=tk.LEFT, padx=5)

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"{GITHUB_API_URL}{username}")
            if response.status_code == 200:
                user_data = response.json()
                self.display_user(user_data)
            else:
                messagebox.showerror("Ошибка", f"Пользователь {username} не найден!")
        except requests.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к GitHub API: {e}")

    def display_user(self, user_data):
        # Очистка предыдущих результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Добавление нового пользователя
        self.results_tree.insert("", "end", values=(
            user_data.get("login", "N/A"),
            user_data.get("name", "N/A"),
            user_data.get("location", "N/A"),
            user_data.get("public_repos", 0)
        ))

    def add_to_favorites(self):
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из списка!")
            return

        user_data = self.results_tree.item(selection[0])["values"]
        login = user_data[0]

        if login not in self.favorites:
            self.favorites[login] = {
                "name": user_data[1],
                "location": user_data[2],
                "public_repos": user_data[3]
            }
            self.save_favorites()
            messagebox.showinfo("Успех", f"{login} добавлен в избранное!")
        else:
            messagebox.showinfo("Информация", f"{login} уже в избранном!")

    def show_favorites(self):
        # Очистка результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Отображение избранных
        for login, data in self.favorites.items():
            self.results_tree.insert("", "end", values=(login, data["name"], data["location"], data["public_repos"]))

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
