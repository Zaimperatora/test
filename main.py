import tkinter as tk
from tkinter import messagebox, Listbox, END
import requests
import json
import os
from PIL import Image, ImageTk
import io

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("500x600")
        
        self.favorites_file = "favorites.json"
        self.current_user_data = None
        self.favorites = []
        
        self.setup_ui()
        self.load_favorites()

    def setup_ui(self):
        # --- Верхняя часть: Поиск ---
        search_frame = tk.Frame(self.root, pady=10)
        search_frame.pack(fill=tk.X)
        
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(search_frame, text="Найти", command=self.search_user)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # --- Средняя часть: Профиль пользователя ---
        profile_frame = tk.Frame(self.root, pady=10)
        profile_frame.pack(fill=tk.BOTH, expand=True)
        
        self.avatar_label = tk.Label(profile_frame)
        self.avatar_label.pack(pady=5)
        
        self.name_label = tk.Label(profile_frame, text="Имя пользователя", font=("Arial", 14, "bold"))
        self.name_label.pack()
        
        self.bio_label = tk.Label(profile_frame, text="Биография", wraplength=400, justify=tk.CENTER)
        self.bio_label.pack(pady=5)
        
        self.stats_label = tk.Label(profile_frame, text="Подписчики: 0 | Репозитории: 0")
        self.stats_label.pack()
        
        # --- Нижняя часть: Избранное ---
        fav_frame = tk.Frame(self.root, pady=10)
        fav_frame.pack(fill=tk.X)
        
        add_fav_btn = tk.Button(fav_frame, text="Добавить в избранное", command=self.add_to_favorites, bg="lightblue")
        add_fav_btn.pack(pady=5)
        
        tk.Label(fav_frame, text="Избранные пользователи:").pack()
        
        self.fav_listbox = Listbox(fav_frame, height=5)
        self.fav_listbox.pack(fill=tk.X, padx=20)
        self.fav_listbox.bind('<<ListboxSelect>>', self.on_favorite_select)

    def search_user(self):
        username = self.search_entry.get().strip()
        
        # Проверка на пустое поле
        if not username:
            messagebox.showwarning("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            url = f"https://api.github.com/users/{username}"
            # GitHub требует User-Agent
            headers = {'User-Agent': 'Python-GitHub-Finder-App'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.current_user_data = response.json()
                self.display_user(self.current_user_data)
            else:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден (Код: {response.status_code})")
                self.current_user_data = None
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", str(e))

    def display_user(self, data):
        self.name_label.config(text=data.get('name') or data.get('login'))
        self.bio_label.config(text=data.get('bio') or "Нет описания")
        self.stats_label.config(text=f"Подписчики: {data.get('followers', 0)} | Репозитории: {data.get('public_repos', 0)}")
        
        # Загрузка аватарки
        try:
            img_url = data.get('avatar_url')
            img_data = requests.get(img_url).content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((100, 100))
            self.photo = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=self.photo)
        except Exception:
            self.avatar_label.config(image='')

    def add_to_favorites(self):
        if not self.current_user_data:
            messagebox.showwarning("Внимание", "Сначала найдите пользователя!")
            return
            
        username = self.current_user_data['login']
        
        # Проверка дубликатов
        if username in self.favorites:
            messagebox.showinfo("Информация", "Этот пользователь уже в избранном.")
            return
            
        self.favorites.append(username)
        self.save_favorites()
        self.update_fav_listbox()
        messagebox.showinfo("Успех", f"{username} добавлен в избранное!")

    def save_favorites(self):
        with open(self.favorites_file, 'w') as f:
            json.dump(self.favorites, f)

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r') as f:
                    self.favorites = json.load(f)
                self.update_fav_listbox()
            except json.JSONDecodeError:
                self.favorites = []

    def update_fav_listbox(self):
        self.fav_listbox.delete(0, END)
        for user in self.favorites:
            self.fav_listbox.insert(END, user)

    def on_favorite_select(self, event):
        selection = self.fav_listbox.curselection()
        if selection:
            username = self.fav_listbox.get(selection[0])
            self.search_entry.delete(0, END)
            self.search_entry.insert(0, username)
            self.search_user()

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()