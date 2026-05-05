import tkinter as tk
from tkinter import messagebox
import urllib.request
import urllib.error
import json

FAV_FILE = 'favorites.json'

def load_favorites():
    try:
        with open(FAV_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_favorites(favorites):
    with open(FAV_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, indent=4)

class GitHubUserFinder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GitHub User Finder")
        self.geometry("700x500")
        self.favorites = load_favorites()

        self.search_var = tk.StringVar()

        # Поле поиска
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Введите имя пользователя GitHub:").pack(side=tk.LEFT)
        tk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Поиск", command=self.search_user).pack(side=tk.LEFT)

        # Результаты
        self.results_list = tk.Listbox(self, height=10)
        self.results_list.pack(pady=10, fill=tk.BOTH, expand=True)

        # Кнопки
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Добавить в избранное", command=self.add_to_favorites).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Показать избранное", command=self.show_favorites).pack(side=tk.LEFT, padx=5)

        self.current_user_data = None  # для хранения текущих данных пользователя

    def search_user(self):
        username = self.search_var.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return
        url = f"https://api.github.com/users/{username}"
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data_bytes = response.read()
                    user_data = json.loads(data_bytes.decode('utf-8'))
                    self.results_list.delete(0, tk.END)
                    display_text = f"{user_data['login']} - {user_data.get('name', 'Без имени')}"
                    self.results_list.insert(tk.END, display_text)
                    self.current_user_data = user_data
                else:
                    messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден.")
                    self.results_list.delete(0, tk.END)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                messagebox.showerror("Ошибка", "Пользователь не найден.")
            else:
                messagebox.showerror("Ошибка", f"HTTP ошибка: {e.code}")
        except urllib.error.URLError as e:
            messagebox.showerror("Ошибка", f"Ошибка сети: {e.reason}")

    def add_to_favorites(self):
        if hasattr(self, 'current_user_data') and self.current_user_data:
            user = self.current_user_data
            if any(fav['id'] == user['id'] for fav in self.favorites):
                messagebox.showinfo("Инфо", "Пользователь уже в избранных.")
                return
            self.favorites.append(user)
            save_favorites(self.favorites)
            messagebox.showinfo("Успех", "Пользователь добавлен в избранное.")
        else:
            messagebox.showerror("Ошибка", "Сначала найдите пользователя.")

    def show_favorites(self):
        fav_window = tk.Toplevel(self)
        fav_window.title("Избранные пользователи")
        fav_listbox = tk.Listbox(fav_window, height=15)
        fav_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        for fav in self.favorites:
            display_text = f"{fav['login']} - {fav.get('name', 'Без имени')}"
            fav_listbox.insert(tk.END, display_text)

if __name__ == "__main__":
    app = GitHubUserFinder()
    app.mainloop()
