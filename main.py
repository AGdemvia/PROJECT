import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox

# Класс для работы с базой данных сотрудников
class EmployeeDatabase:
    def __init__(self):
        # Создание подключения к базе данных и инициализация курсора
        self.conn = sqlite3.connect("employee.db")
        self.cur = self.conn.cursor()
        
        # Создание таблицы employees, если она не существует
        self.cur.execute('''CREATE TABLE IF NOT EXISTS employees (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            phone TEXT,
                            email TEXT,
                            salary REAL
                            )''')
        self.conn.commit()

    # Добавление сотрудника в базу данных
    def insert_employee(self, name, phone, email, salary):
        self.cur.execute("INSERT INTO employees (name, phone, email, salary) VALUES (?, ?, ?, ?)",
                         (name, phone, email, salary))
        self.conn.commit()

    # Получение всех сотрудников из базы данных
    def get_all_employees(self):
        self.cur.execute("SELECT * FROM employees")
        return self.cur.fetchall()

    # Получение данных о сотруднике по ID
    def get_employee_by_id(self, employee_id):
        self.cur.execute("SELECT * FROM employees WHERE id=?", (employee_id,))
        return self.cur.fetchone()

    # Обновление данных сотрудника
    def update_employee(self, employee_id, name, phone, email, salary):
        self.cur.execute("UPDATE employees SET name=?, phone=?, email=?, salary=? WHERE id=?",
                         (name, phone, email, salary, employee_id))
        self.conn.commit()

    # Удаление сотрудника по ID
    def delete_employee(self, employee_id):
        self.cur.execute("DELETE FROM employees WHERE id=?", (employee_id,))
        self.conn.commit()

    # Поиск сотрудников по имени
    def search_employees(self, name):
        self.cur.execute("SELECT * FROM employees WHERE name LIKE ?", (f"%{name}%",))
        return self.cur.fetchall()

# Класс для создания главного окна приложения
class EmployeeListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Список сотрудников компании")
        
        # Создание объекта для работы с базой данных
        self.db = EmployeeDatabase()
        
        self.init_ui()
        self.view_records()

    def init_ui(self):
        # Создание панели инструментов
        toolbar = tk.Frame(self.root, bg="#d7d7d7", bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

    # Создание кнопок для действий
        add_img = tk.PhotoImage(file="c:/Users/airat/Desktop/project/img/add.png")
        add_button = tk.Button(toolbar, image=add_img, command=self.open_add_dialog)
        add_button.image = add_img
        add_button.pack(side=tk.LEFT)

        update_img = tk.PhotoImage(file="c:/Users/airat/Desktop/project/img/update.png")
        update_button = tk.Button(toolbar, image=update_img, command=self.open_update_dialog)
        update_button.image = update_img
        update_button.pack(side=tk.LEFT)

        delete_img = tk.PhotoImage(file="c:/Users/airat/Desktop/project/img/delete.png")
        delete_button = tk.Button(toolbar, image=delete_img, command=self.delete_employee)
        delete_button.image = delete_img
        delete_button.pack(side=tk.LEFT)

        search_img = tk.PhotoImage(file="c:/Users/airat/Desktop/project/img/search.png")
        search_button = tk.Button(toolbar, image=search_img, command=self.open_search_dialog)
        search_button.image = search_img
        search_button.pack(side=tk.LEFT)

        refresh_img = tk.PhotoImage(file="c:/Users/airat/Desktop/project/img/refresh.png")
        refresh_button = tk.Button(toolbar, image=refresh_img, command=self.view_records)
        refresh_button.image = refresh_img
        refresh_button.pack(side=tk.LEFT)


        # Создание виджета Treeview для отображения данных
        self.tree = ttk.Treeview(self.root, columns=("id", "name", "phone", "email", "salary"), height=15, show="headings")
        self.tree.column("id", width=30, anchor=tk.CENTER)
        self.tree.column("name", width=150, anchor=tk.CENTER)
        self.tree.column("phone", width=100, anchor=tk.CENTER)
        self.tree.column("email", width=200, anchor=tk.CENTER)
        self.tree.column("salary", width=80, anchor=tk.CENTER)

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="ФИО")
        self.tree.heading("phone", text="Телефон")
        self.tree.heading("email", text="Эл. почта")
        self.tree.heading("salary", text="Заработная плата")

        self.tree.pack()

    # Метод для отображения записей сотрудников в Treeview
    def view_records(self):
        records = self.db.get_all_employees()
        self.clear_tree()
        for record in records:
            self.tree.insert("", "end", values=record)

    # Метод для очистки Treeview
    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    # Метод для открытия диалогового окна добавления сотрудника
    def open_add_dialog(self):
        AddEmployeeDialog(self, self.db)

    # Метод для открытия диалогового окна обновления сотрудника
    def open_update_dialog(self):
        selected_item = self.tree.selection()
        if selected_item:
            employee_id = self.tree.item(selected_item, "values")[0]
            UpdateEmployeeDialog(self, self.db, employee_id)
        else:
            tk.messagebox.showwarning("Ошибка", "Выберите сотрудника для редактирования.")

    # Метод для открытия диалогового окна поиска сотрудника
    def open_search_dialog(self):
        SearchEmployeeDialog(self, self.db)

    # Метод для удаления сотрудника
    def delete_employee(self):
        selected_item = self.tree.selection()
        if selected_item:
            employee_id = self.tree.item(selected_item, "values")[0]
            if tk.messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить этого сотрудника?"):
                self.db.delete_employee(employee_id)
                self.view_records()
        else:
            tk.messagebox.showwarning("Ошибка", "Выберите сотрудника для удаления.")

# Класс для диалогового окна добавления сотрудника
class AddEmployeeDialog:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db

        self.root = tk.Toplevel()
        self.root.title("Добавить сотрудника")
        self.root.geometry("400x200")

        self.init_ui()

    def init_ui(self):
        self.name_label = tk.Label(self.root, text="ФИО")
        self.name_label.pack()

        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        self.phone_label = tk.Label(self.root, text="Телефон")
        self.phone_label.pack()

        self.phone_entry = tk.Entry(self.root)
        self.phone_entry.pack()

        self.email_label = tk.Label(self.root, text="Эл. почта")
        self.email_label.pack()

        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        self.salary_label = tk.Label(self.root, text="Заработная плата")
        self.salary_label.pack()

        self.salary_entry = tk.Entry(self.root)
        self.salary_entry.pack()

        add_button = tk.Button(self.root, text="Добавить", command=self.add_employee)
        add_button.pack()

    # Метод для добавления сотрудника
    def add_employee(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        salary = float(self.salary_entry.get())

        self.db.insert_employee(name, phone, email, salary)
        self.parent.view_records()
        self.root.destroy()

# Класс для диалогового окна обновления сотрудника
class UpdateEmployeeDialog:
    def __init__(self, parent, db, employee_id):
        self.parent = parent
        self.db = db
        self.employee_id = employee_id

        self.root = tk.Toplevel()
        self.root.title("Изменить сотрудника")
        self.root.geometry("400x200")

        self.init_ui()

    def init_ui(self):
        # Получение данных о сотруднике
        employee_data = self.db.get_employee_by_id(self.employee_id)

        self.name_label = tk.Label(self.root, text="ФИО")
        self.name_label.pack()

        self.name_entry = tk.Entry(self.root)
        self.name_entry.insert(0, employee_data[1])
        self.name_entry.pack()

        self.phone_label = tk.Label(self.root, text="Телефон")
        self.phone_label.pack()

        self.phone_entry = tk.Entry(self.root)
        self.phone_entry.insert(0, employee_data[2])
        self.phone_entry.pack()

        self.email_label = tk.Label(self.root, text="Эл. почта")
        self.email_label.pack()

        self.email_entry = tk.Entry(self.root)
        self.email_entry.insert(0, employee_data[3])
        self.email_entry.pack()

        self.salary_label = tk.Label(self.root, text="Заработная плата")
        self.salary_label.pack()

        self.salary_entry = tk.Entry(self.root)
        self.salary_entry.insert(0, employee_data[4])
        self.salary_entry.pack()

        update_button = tk.Button(self.root, text="Изменить", command=self.update_employee)
        update_button.pack()

    # Метод для обновления данных сотрудника
    def update_employee(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        salary = float(self.salary_entry.get())

        self.db.update_employee(self.employee_id, name, phone, email, salary)
        self.parent.view_records()
        self.root.destroy()

# Класс для диалогового окна поиска сотрудника
class SearchEmployeeDialog:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db

        self.root = tk.Toplevel()
        self.root.title("Поиск сотрудника")
        self.root.geometry("400x200")

        self.init_ui()

    def init_ui(self):
        self.name_label = tk.Label(self.root, text="Поиск по ФИО")
        self.name_label.pack()

        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        search_button = tk.Button(self.root, text="Поиск", command=self.search_employees)
        search_button.pack()

    # Метод для поиска сотрудников
    def search_employees(self):
        name = self.name_entry.get()
        results = self.db.search_employees(name)
        self.parent.clear_tree()
        for result in results:
            self.parent.tree.insert("", "end", values=result)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeListApp(root)
    root.mainloop()