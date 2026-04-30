import json
import os
from tkinter import *
from tkinter import ttk, messagebox

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("800x600")

        # Данные
        self.books = []
        self.load_data()

        # Переменные для фильтров
        self.filter_genre = StringVar()
        self.filter_pages = StringVar()

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table()
        self.create_button_frame()

        # Заполнение выпадающего списка жанров
        self.update_genre_filter()

    def create_input_frame(self):
        """Форма ввода новой книги"""
        frame = LabelFrame(self.root, text="Добавить книгу", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Название
        Label(frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.title_entry = Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5)

        # Автор
        Label(frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.author_entry = Entry(frame, width=30)
        self.author_entry.grid(row=1, column=1, padx=5)

        # Жанр
        Label(frame, text="Жанр:").grid(row=2, column=0, sticky="w")
        self.genre_entry = Entry(frame, width=30)
        self.genre_entry.grid(row=2, column=1, padx=5)

        # Страницы
        Label(frame, text="Кол-во страниц:").grid(row=3, column=0, sticky="w")
        self.pages_entry = Entry(frame, width=30)
        self.pages_entry.grid(row=3, column=1, padx=5)

        # Кнопка добавления
        self.add_btn = Button(frame, text="Добавить книгу", command=self.add_book, bg="lightgreen")
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=10)

    def create_filter_frame(self):
        """Фильтрация"""
        frame = LabelFrame(self.root, text="Фильтры", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        Label(frame, text="Жанр:").grid(row=0, column=0, sticky="w")
        self.genre_filter_combo = ttk.Combobox(frame, textvariable=self.filter_genre, width=27)
        self.genre_filter_combo.grid(row=0, column=1, padx=5)
        self.genre_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Кнопка сброса фильтра жанра
        Button(frame, text="Сбросить жанр", command=self.reset_genre_filter).grid(row=0, column=2, padx=5)

        # Фильтр по страницам (> N)
        Label(frame, text="Страниц >").grid(row=1, column=0, sticky="w")
        self.pages_filter_entry = Entry(frame, textvariable=self.filter_pages, width=27)
        self.pages_filter_entry.grid(row=1, column=1, padx=5)
        Button(frame, text="Применить", command=self.apply_filters).grid(row=1, column=2, padx=5)
        Button(frame, text="Сбросить фильтр страниц", command=self.reset_pages_filter).grid(row=1, column=3, padx=5)

    def create_table(self):
        """Таблица для отображения книг"""
        frame = Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы Treeview
        self.tree = ttk.Treeview(frame, columns=("ID", "Название", "Автор", "Жанр", "Страницы"),
                                 show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страницы", text="Страницы")

        self.tree.column("ID", width=30)
        self.tree.column("Название", width=200)
        self.tree.column("Автор", width=150)
        self.tree.column("Жанр", width=100)
        self.tree.column("Страницы", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления
        self.delete_btn = Button(self.root, text="Удалить выбранную книгу", command=self.delete_book, bg="lightcoral")
        self.delete_btn.pack(pady=5)

    def create_button_frame(self):
        """Кнопки сохранения/загрузки"""
        frame = Frame(self.root)
        frame.pack(pady=10)

        Button(frame, text="Сохранить в JSON", command=self.save_to_json, bg="lightblue").pack(side="left", padx=5)
        Button(frame, text="Загрузить из JSON", command=self.load_from_json, bg="lightblue").pack(side="left", padx=5)

    def add_book(self):
        """Добавление книги с проверкой"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        # Проверка на пустые поля
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка, что страницы — число
        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        # Создание ID
        new_id = max([book["id"] for book in self.books], default=0) + 1

        new_book = {
            "id": new_id,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }

        self.books.append(new_book)

        # Очистка полей
        self.title_entry.delete(0, END)
        self.author_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.pages_entry.delete(0, END)

        self.update_genre_filter()
        self.apply_filters()
        messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")

    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return

        # Получаем ID книги
        item = self.tree.item(selected[0])
        book_id = item["values"][0]

        # Удаляем из списка
        self.books = [book for book in self.books if book["id"] != book_id]

        self.update_genre_filter()
        self.apply_filters()
        messagebox.showinfo("Успех", "Книга удалена!")

    def apply_filters(self):
        """Применение фильтров к отображению"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered_books = self.books.copy()

        # Фильтр по жанру
        genre_filter = self.filter_genre.get().strip()
        if genre_filter:
            filtered_books = [book for book in filtered_books if book["genre"].lower() == genre_filter.lower()]

        # Фильтр по страницам
        pages_filter = self.filter_pages.get().strip()
        if pages_filter:
            try:
                pages_threshold = int(pages_filter)
                filtered_books = [book for book in filtered_books if book["pages"] > pages_threshold]
            except ValueError:
                pass  # Игнорируем некорректный ввод

        # Заполнение таблицы
        for book in filtered_books:
            self.tree.insert("", END, values=(book["id"], book["title"], book["author"],
                                              book["genre"], book["pages"]))

    def update_genre_filter(self):
        """Обновление выпадающего списка жанров"""
        genres = sorted(set(book["genre"] for book in self.books))
        self.genre_filter_combo["values"] = ["Все"] + genres
        if not self.filter_genre.get():
            self.filter_genre.set("Все")

    def reset_genre_filter(self):
        self.filter_genre.set("Все")
        self.apply_filters()

    def reset_pages_filter(self):
        self.filter_pages.set("")
        self.apply_filters()

    def save_to_json(self):
        """Сохранение данных в JSON"""
        try:
            with open("books.json", "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные сохранены в books.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_json(self):
        """Загрузка данных из JSON"""
        try:
            if not os.path.exists("books.json"):
                messagebox.showwarning("Предупреждение", "Файл books.json не найден!")
                return

            with open("books.json", "r", encoding="utf-8") as f:
                self.books = json.load(f)

            self.update_genre_filter()
            self.apply_filters()
            messagebox.showinfo("Успех", "Данные загружены из books.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

    def load_data(self):
        """Автоматическая загрузка при старте"""
        if os.path.exists("books.json"):
            try:
                with open("books.json", "r", encoding="utf-8") as f:
                    self.books = json.load(f)
            except:
                self.books = []


if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()