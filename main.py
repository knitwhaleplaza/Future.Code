import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Имя файла для сохранения данных
DATA_FILE = "books.json"


class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x500")

        # Список для хранения книг (каждая книга - словарь)
        self.books = []

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_frame()
        self.create_button_frame()

        # Загрузка данных из файла
        self.load_data()

        # Обновление отображения
        self.refresh_book_list()

    # ==================== ИНТЕРФЕЙС ====================

    def create_input_frame(self):
        """Форма для ввода данных о книге"""
        input_frame = tk.LabelFrame(self.root, text="Добавление новой книги", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Название книги
        tk.Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Автор
        tk.Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.author_entry = tk.Entry(input_frame, width=20)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        # Жанр
        tk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.genre_entry = tk.Entry(input_frame, width=20)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)

        # Количество страниц
        tk.Label(input_frame, text="Количество страниц:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.pages_entry = tk.Entry(input_frame, width=10)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)

        # Кнопка добавления
        add_btn = tk.Button(input_frame, text="Добавить книгу", command=self.add_book, bg="lightgreen")
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)

    def create_filter_frame(self):
        """Панель фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        tk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=5)
        self.genre_filter_var = tk.StringVar()
        self.genre_filter_combo = ttk.Combobox(filter_frame, textvariable=self.genre_filter_var, width=20)
        self.genre_filter_combo.grid(row=0, column=1, padx=5)
        self.genre_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_book_list())

        # Фильтр по страницам (> 200)
        self.pages_filter_var = tk.BooleanVar()
        pages_filter_check = tk.Checkbutton(
            filter_frame,
            text="Только книги с количеством страниц больше 200",
            variable=self.pages_filter_var,
            command=self.refresh_book_list
        )
        pages_filter_check.grid(row=0, column=2, columnspan=2, padx=20)

        # Кнопка сброса фильтров
        reset_btn = tk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        reset_btn.grid(row=0, column=4, padx=10)

    def create_tree_frame(self):
        """Таблица для отображения списка книг"""
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы
        columns = ("Название", "Автор", "Жанр", "Страницы")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Настройка заголовков
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "Название" else 250)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_button_frame(self):
        """Кнопки управления"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)

        save_btn = tk.Button(button_frame, text="Сохранить в JSON", command=self.save_data, bg="lightblue")
        save_btn.pack(side="left", padx=5)

        load_btn = tk.Button(button_frame, text="Загрузить из JSON", command=self.load_data, bg="lightyellow")
        load_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(button_frame, text="Удалить выбранную книгу", command=self.delete_book, bg="salmon")
        delete_btn.pack(side="right", padx=5)

    # ==================== ЛОГИКА ПРИЛОЖЕНИЯ ====================

    def validate_input(self, title, author, genre, pages):
        """Проверка корректности ввода"""
        if not title.strip():
            messagebox.showerror("Ошибка", "Название книги не может быть пустым!")
            return False
        if not author.strip():
            messagebox.showerror("Ошибка", "Имя автора не может быть пустым!")
            return False
        if not genre.strip():
            messagebox.showerror("Ошибка", "Жанр не может быть пустым!")
            return False
        try:
            pages_num = int(pages)
            if pages_num <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
            return False
        return True

    def add_book(self):
        """Добавление новой книги"""
        title = self.title_entry.get()
        author = self.author_entry.get()
        genre = self.genre_entry.get()
        pages = self.pages_entry.get()

        if not self.validate_input(title, author, genre, pages):
            return

        book = {
            "title": title.strip(),
            "author": author.strip(),
            "genre": genre.strip(),
            "pages": int(pages)
        }

        self.books.append(book)
        self.refresh_book_list()
        self.clear_input_fields()

        messagebox.showinfo("Успех", f"Книга '{title}' успешно добавлена!")

    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления!")
            return

        # Получаем название книги из выбранной строки
        item = self.tree.item(selected[0])
        book_title = item['values'][0]

        # Удаляем из списка
        self.books = [book for book in self.books if book['title'] != book_title]

        self.refresh_book_list()
        messagebox.showinfo("Успех", f"Книга '{book_title}' удалена!")

    def get_filtered_books(self):
        """Возвращает отфильтрованный список книг"""
        filtered = self.books.copy()

        # Фильтр по жанру
        selected_genre = self.genre_filter_var.get()
        if selected_genre and selected_genre != "Все жанры":
            filtered = [book for book in filtered if book['genre'] == selected_genre]

        # Фильтр по страницам (> 200)
        if self.pages_filter_var.get():
            filtered = [book for book in filtered if book['pages'] > 200]

        return filtered

    def refresh_book_list(self):
        """Обновление таблицы с учётом фильтров"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получаем отфильтрованные книги
        filtered_books = self.get_filtered_books()

        # Заполняем таблицу
        for book in filtered_books:
            self.tree.insert("", "end", values=(book['title'], book['author'], book['genre'], book['pages']))

        # Обновляем список жанров в фильтре
        self.update_genre_filter()

    def update_genre_filter(self):
        """Обновление выпадающего списка жанров для фильтрации"""
        genres = sorted(set(book['genre'] for book in self.books))
        genres.insert(0, "Все жанры")
        self.genre_filter_combo['values'] = genres
        if not self.genre_filter_var.get() or self.genre_filter_var.get() not in genres:
            self.genre_filter_var.set("Все жанры")

    def reset_filters(self):
        """Сброс всех фильтров"""
        self.genre_filter_var.set("Все жанры")
        self.pages_filter_var.set(False)
        self.refresh_book_list()

    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    # ==================== РАБОТА С JSON ====================

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные успешно сохранены в файл '{DATA_FILE}'")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if not os.path.exists(DATA_FILE):
            messagebox.showwarning("Внимание", f"Файл '{DATA_FILE}' не найден. Начните с пустого списка.")
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded_books = json.load(f)

            # Проверка структуры данных
            if isinstance(loaded_books, list):
                self.books = loaded_books
                self.refresh_book_list()
                messagebox.showinfo("Успех", f"Загружено {len(self.books)} книг из файла '{DATA_FILE}'")
            else:
                messagebox.showerror("Ошибка", "Неверный формат файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")


def main():
    root = tk.Tk()
    app = BookTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()