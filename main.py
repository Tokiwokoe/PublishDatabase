import sys
import psycopg2
import openpyxl
import datetime
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QGraphicsScene
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from UIclass import main_window, LoginScreen, Add, delete, DeleteMessage, worker, add_worker, graphics, publish, registry, add_client, queries


class AuthWindow(QMainWindow, LoginScreen.Ui_Auth):
    def __init__(self):
        super(AuthWindow, self).__init__()
        self.setupUi(self)
        self.login.clicked.connect(self.to_login)

    def to_login(self):
        try:
            self.user = self.loginfield.text()
            self.password = self.passwordfield.text()
            self.connection = psycopg2.connect(
                host='localhost',
                database='Publish',
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT current_user;")
            self.current_user = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT rolname FROM pg_user JOIN pg_auth_members ON pg_user.usesysid = pg_auth_members.member JOIN pg_roles ON pg_roles.oid = pg_auth_members.roleid WHERE pg_user.usename = current_user;")
            self.role_group = self.cursor.fetchone()[0]
            print(f'{self.current_user} из группы {self.role_group} вошёл в систему')
            if self.role_group == 'publish_admin':
                self.admin_menu = MainMenu(self.connection, self.cursor, self.current_user, self.role_group)
                self.admin_menu.show()
            elif self.role_group == 'publish':
                self.cursor.execute(f"SELECT departament FROM \"publish_worker\" WHERE login = '{self.user}'")
                self.departament = self.cursor.fetchone()[0]
                self.publish_menu = PublishMenu(self.connection, self.cursor, self.current_user, self.departament, self.role_group)
                self.publish_menu.show()
            elif self.role_group == 'author':
                self.cursor.execute(f"SELECT author_id FROM \"author_worker\" WHERE login = '{self.user}'")
                self.departament = self.cursor.fetchone()[0]
                self.author_menu = AuthorMenu(self.connection, self.cursor, self.current_user, self.role_group, self.departament)
                self.author_menu.show()
            else:
                self.error.setText('Неизвестная роль')
            self.close()

        except psycopg2.Error as err:
            print(err)
            self.error.setText('Проверьте ввод')


class PrintTable(QMainWindow):
    def __init__(self):
        super(PrintTable, self).__init__()

    def to_print_table(self, query):
        self.cursor.execute(query)
        self.rows = self.cursor.fetchall()
        self.tableWidget.setRowCount(len(self.rows))
        self.tableWidget.setColumnCount(len(self.labels))
        self.tableWidget.setHorizontalHeaderLabels(self.labels)
        i = 0
        for elem in self.rows:
            j = 0
            for t in elem:
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(t).strip()))
                j += 1
            i += 1
        i = 0
        self.tableWidget.resizeColumnsToContents()

    def to_print_author(self):
        query = 'SELECT * FROM author_view'
        self.labels = ['Фамилия', 'Страна', 'Дата рождения', 'Дата смерти']
        self.to_print_table(query)

    def to_print_binding(self):
        query = 'SELECT * FROM binding_view'
        self.labels = ['Переплёт']
        self.to_print_table(query)

    def to_print_book(self):
        query = 'SELECT * FROM book_view'
        self.labels = ['Название', 'Фамилия автора', 'Жанр']
        self.to_print_table(query)

    def to_print_city(self):
        query = 'SELECT * FROM city_view'
        self.labels = ['Город']
        self.to_print_table(query)

    def to_print_country(self):
        query = 'SELECT * FROM country_view'
        self.labels = ['Страна']
        self.to_print_table(query)

    def to_print_genre(self):
        query = 'SELECT * FROM genre_view'
        self.labels = ['Жанр']
        self.to_print_table(query)

    def to_print_lang(self):
        query = 'SELECT * FROM lang_view'
        self.labels = ['Язык']
        self.to_print_table(query)

    def to_print_prop(self):
        query = 'SELECT * FROM prop_view'
        self.labels = ['Тип собственности']
        self.to_print_table(query)

    def to_print_pub_type(self):
        query = 'SELECT * FROM pub_type_view'
        self.labels = ['Тип издания']
        self.to_print_table(query)

    def to_print_pub_book(self):
        query = 'SELECT * FROM pub_book_view'
        self.labels = ['Издательство', 'Книга', 'Язык', 'Цена', 'Год публикации', 'Переплёт', 'Тип издания', 'Тираж']
        self.to_print_table(query)

    def to_print_publish(self):
        query = 'SELECT * FROM publish_view'
        self.labels = ['Название', 'Город', 'Тип собственности', 'Год открытия', 'Телефон', 'Адрес']
        self.to_print_table(query)

    def to_print_acc(self):
        query = 'SELECT login, departament FROM publish_worker'
        self.labels = ['Логин', 'Номер издательства']
        self.to_print_table(query)


class MainMenu(PrintTable, main_window.Ui_MainWindow):
    def __init__(self, connection, cursor, current_user, role_group):
        super(MainMenu, self).__init__()
        self.setupUi(self)
        self.setFixedSize(1320, 720)
        self.publish.clicked.connect(self.to_print_publish)
        self.book.clicked.connect(self.to_print_book)
        self.author.clicked.connect(self.to_print_author)
        self.book_in_pub.clicked.connect(self.to_print_pub_book)
        self.binding.clicked.connect(self.to_print_binding)
        self.country.clicked.connect(self.to_print_country)
        self.city.clicked.connect(self.to_print_city)
        self.lang.clicked.connect(self.to_print_lang)
        self.prop.clicked.connect(self.to_print_prop)
        self.genre.clicked.connect(self.to_print_genre)
        self.client_type_4.clicked.connect(self.to_print_pub_type)

        self.Change_button.clicked.connect(self.to_add)
        self.Delete_button.clicked.connect(self.to_delete)
        self.Workers_button.clicked.connect(self.to_add_worker)
        self.Queries_button.clicked.connect(self.queries)
        self.connection = connection
        self.cursor = cursor
        self.current_user = current_user
        self.role_group = role_group

    def to_add(self):
        self.add = Add(self.connection, self.cursor, self.role_group)
        self.add.show()

    def to_delete(self):
        self.delete = Delete(self.connection, self.cursor, self.role_group)
        self.delete.show()

    def to_add_worker(self):
        self.worker = AddWorker(self.connection, self.cursor, self.current_user, self.role_group)
        self.worker.show()

    def queries(self):
        self.q = Queries(self.connection, self.cursor)
        self.q.show()


class Add(QMainWindow, Add.Ui_Dialog):
    def __init__(self, connection, cursor, role_group):
        super(Add, self).__init__()
        self.setupUi(self)
        self.role_group = role_group
        self.connection = connection
        self.cursor = cursor
        if role_group == 'publish_admin':
            self.table.addItem('Город')
            self.table.addItem('Страна')
            self.table.addItem('Жанр')
            self.table.addItem('Язык')
            self.table.addItem('Тип издания')
            self.table.addItem('Тип собственности')
        self.OKbutton.clicked.connect(self.to_add)

    def to_add(self):
        if self.table.currentText() == 'Город':
            self.table_name = 'city'
        elif self.table.currentText() == 'Страна':
            self.table_name = 'country'
        elif self.table.currentText() == 'Жанр':
            self.table_name = 'genre'
        elif self.table.currentText() == 'Тип издания':
            self.table_name = 'publication_type'
        elif self.table.currentText() == 'Тип собственности':
            self.table_name = 'property_type'
        elif self.table.currentText() == 'Язык':
            self.table_name = 'language'
        try:
            self.name = self.id.text()
            query = f'SELECT id FROM {self.table_name} ORDER BY id DESC LIMIT 1'
            self.cursor.execute(query)
            self.name_id = self.cursor.fetchone()
            if not self.name_id:
                self.name_id = [0]
            query = f"INSERT INTO {self.table_name} VALUES({int(self.name_id[0]) + 1}, '{self.name}')"
            self.cursor.execute(query)
            self.connection.commit()
            self.error.setText('Успешно добавлено')
        except Exception as err:
            print(err)
            self.error.setText('Ошибка!')


class DeleteMess(QMainWindow, DeleteMessage.Ui_Dialog):
    def __init__(self, connection, cursor, table, id):
        super(DeleteMess, self).__init__()
        self.setupUi(self)
        self.setFixedSize(560, 150)
        self.connection = connection
        self.cursor = cursor
        self.table = table
        self.id = id
        query = f'SELECT * FROM {self.table} WHERE id = {self.id}'
        self.cursor.execute(query)
        self.text.setText(f'Вы действительно хотите удалить {self.cursor.fetchall()}')
        self.OKbutton.clicked.connect(self.delete)
        self.CancelButton.clicked.connect(self.cancel)

    def delete(self):
        try:
            query = f'DELETE FROM {self.table} WHERE id = {self.id}'
            self.cursor.execute(query)
            self.connection.commit()
            self.error.setText('Удалено!')
        except Exception as err:
            print(err)
            self.error.setText('Ошибка!')

    def cancel(self):
        self.close()


class Delete(QMainWindow, delete.Ui_Dialog):
    def __init__(self, connection, cursor, role_group):
        super(Delete, self).__init__()
        self.setupUi(self)
        self.role_group = role_group
        self.connection = connection
        self.cursor = cursor
        if role_group == 'publish_admin':
            self.table.addItem('Город')
            self.table.addItem('Страна')
            self.table.addItem('Жанр')
            self.table.addItem('Язык')
            self.table.addItem('Тип издания')
            self.table.addItem('Тип собственности')
            self.table.addItem('Издательства')
            self.table.addItem('Авторы')
            self.table.addItem('Работники издательства')
            self.table.addItem('Аккаунты авторов')
        elif role_group == 'publish':
            self.table.addItem('Книги издательства')
        elif role_group == 'author':
            self.table.addItem('Книги')
        self.OKbutton.clicked.connect(self.to_delete)

    def to_delete(self):
        if self.table.currentText() == 'Город':
            self.table_name = 'city'
        elif self.table.currentText() == 'Страна':
            self.table_name = 'country'
        elif self.table.currentText() == 'Жанр':
            self.table_name = 'genre'
        elif self.table.currentText() == 'Тип издания':
            self.table_name = 'publication_type'
        elif self.table.currentText() == 'Тип собственности':
            self.table_name = 'property_type'
        elif self.table.currentText() == 'Язык':
            self.table_name = 'language'
        elif self.table.currentText() == 'Издательства':
            self.table_name = 'publish'
        elif self.table.currentText() == 'Авторы':
            self.table_name = 'author'
        elif self.table.currentText() == 'Книги':
            self.table_name = 'book'
        elif self.table.currentText() == 'Книги издательства':
            self.table_name = 'publish_book'
        elif self.table.currentText() == 'Работники издательства':
            self.table_name = 'publish_worker'
        elif self.table.currentText() == 'Аккаунты авторов':
            self.table_name = 'author_worker'
        id = self.id.text()
        self.message = DeleteMess(self.connection, self.cursor, self.table_name, id)
        self.message.show()


class AddWorker(PrintTable, worker.Ui_Dialog):
    def __init__(self, connection, cursor, current_user, role_group):
        super(AddWorker, self).__init__()
        self.setupUi(self)
        self.setFixedSize(550, 580)
        self.connection = connection
        self.cursor = cursor
        self.current_user = current_user
        self.role_group = role_group
        self.update_reg.clicked.connect(self.to_print_reg)
        self.update_acc.clicked.connect(self.to_print_acc)
        self.add_acc.clicked.connect(self.to_add)
        self.add_reg.clicked.connect(self.to_add)
        self.delete_reg.clicked.connect(self.to_delete)
        self.delete_acc.clicked.connect(self.to_delete)

    def to_delete(self):
        self.delete = Delete(self.connection, self.cursor, self.role_group)
        self.delete.show()

    def to_add(self):
        self.add = AddEmployees(self.connection, self.cursor)
        self.add.show()

    def to_print_reg(self):
        query = 'SELECT login FROM author_worker ORDER BY id'
        self.labels = ['Логин']
        self.cursor.execute(query)
        self.rows = self.cursor.fetchall()
        self.tableWidget_2.setRowCount(len(self.rows))
        self.tableWidget_2.setColumnCount(len(self.labels))
        self.tableWidget_2.setHorizontalHeaderLabels(self.labels)
        i = 0
        for elem in self.rows:
            j = 0
            for t in elem:
                self.tableWidget_2.setItem(i, j, QTableWidgetItem(str(t).strip()))
                j += 1
            i += 1
        i = 0
        self.tableWidget_2.resizeColumnsToContents()


class AddEmployees(QMainWindow, add_worker.Ui_Dialog):
    def __init__(self, connection, cursor):
        super(AddEmployees, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.table.addItem('Издательство')
        self.table.addItem('Автор')
        self.table_name = 'publish_worker'
        self.table.currentTextChanged.connect(self.handle_table_change)  # Подключение сигнала
        self.add_button.clicked.connect(self.to_add)

    def handle_table_change(self):
        if self.table.currentText() == 'Издательство':
            self.table_name = 'publish_worker'
            self.dep.show()
            self.label_6.show()
        if self.table.currentText() == 'Автор':
            self.table_name = 'author_worker'
            self.dep.show()
            self.label_6.show()

    def to_add(self):
        self.query = f'SELECT id FROM {self.table_name} ORDER BY id DESC'
        self.cursor.execute(self.query)
        self.id = self.cursor.fetchone()
        if not self.id:
            self.id = [0]
        self.query = f"INSERT INTO {self.table_name} VALUES ({int(self.id[0])+1}, '{self.log.text()}', {self.dep.text()})"
        try:
            self.cursor.execute(self.query)
            self.connection.commit()
            self.error.setText('Успешно добавлено')
        except Exception as err:
            print(err)
            self.error.setText('Ошибка!')


class PublishMenu(PrintTable, publish.Ui_Dialog):
    def __init__(self, connection, cursor, current_user, departament, role_group):
        super(PublishMenu, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.current_user = current_user
        self.departament = departament
        self.role_group = role_group
        self.auth_as.setText(f'Вы вошли как: {current_user}, издательство № {self.departament}')
        self.Update_btn.clicked.connect(self.to_print_help_as_accountant)
        self.Add_btn.clicked.connect(self.to_add_help)
        self.Delete_btn.clicked.connect(self.to_delete)

    def to_print_help_as_accountant(self):
        query = f'SELECT publish.name AS pub, book.name AS book, language.name AS lang, publish_book.price, publish_book.year_published, binding.name AS binding, publication_type.name AS pub_type, publish_book.amount FROM publish_book LEFT JOIN publish ON publish.id = publish_book.publish_id LEFT JOIN book ON book.id = publish_book.book_id LEFT JOIN language ON language.id = publish_book.language LEFT JOIN binding ON binding.id = publish_book.binding LEFT JOIN publication_type ON publication_type.id = publish_book.publication_type WHERE publish.id = {self.departament}'
        self.labels = ['Издательство', 'Книга', 'Язык', 'Цена', 'Год публикации', 'Переплёт', 'Тип издания', 'Тираж']
        self.to_print_table(query)

    def to_delete(self):
        self.delete = Delete(self.connection, self.cursor, self.role_group)
        self.delete.show()

    def to_add_help(self):
        self.add = AddHelp(self.connection, self.cursor, self.departament)
        self.add.show()


class AuthorMenu(PrintTable, registry.Ui_Dialog):
    def __init__(self, connection, cursor, current_user, role_group, departament):
        super(AuthorMenu, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.current_user = current_user
        self.dep = departament
        self.role_group = role_group
        query = f'SELECT lastname FROM author WHERE id = {self.dep}'
        self.cursor.execute(query)
        self.lastname = self.cursor.fetchone()
        self.author = self.lastname[0].replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        self.auth_as.setText(f'Вы вошли как: {current_user}, {self.author}')
        self.Update_btn.clicked.connect(self.to_print_book_as_author)
        self.Add_btn.clicked.connect(self.to_add_client)
        self.Delete_btn.clicked.connect(self.to_delete)

    def to_print_book_as_author(self):
        query = f'SELECT book.name, author.lastname, genre.name AS genre FROM book LEFT JOIN author ON author.id = book.author LEFT JOIN genre ON genre.id = book.genre WHERE author.id = {self.dep}'
        self.labels = ['Книга', 'Автор', 'Жанр']
        self.to_print_table(query)

    def to_delete(self):
        self.delete = Delete(self.connection, self.cursor, self.role_group)
        self.delete.show()

    def to_add_client(self):
        self.add = AddClient(self.connection, self.cursor, self.dep)
        self.add.show()


class AddHelp(QMainWindow):
    def __init__(self, connection, cursor, departament):
        super(AddHelp, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.departament = departament
        query = 'SELECT id, name FROM "Client"'
        self.cursor.execute(query)
        for t in self.cursor.fetchall():
            self.client.addItem(str(t))
        query = 'SELECT id, name FROM "Help_type"'
        self.cursor.execute(query)
        for t in self.cursor.fetchall():
            self.help_type.addItem(str(t))
        self.Add.clicked.connect(self.correct_data)

    def correct_data(self):
        money = self.money.text()
        client = self.client.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        help_type = self.help_type.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        client_id = str(client[0])
        help_type_id = str(help_type[0])
        if int(money) > 0:
            try:
                query = f"INSERT INTO \"Help\" VALUES({client_id}, {self.departament}, {help_type_id}, {money}, '{datetime.date.today()}')"
                self.cursor.execute(query)
                self.connection.commit()
                self.error.setText('Успешно добавлено')
            except Exception as err:
                print(err)
                self.error.setText('Что-то пошло не так :(')
        else:
            self.error.setText('Проверьте корректность заполнения полей!')


class AddClient(QMainWindow, add_client.Ui_Dialog):
    def __init__(self, connection, cursor, departament):
        super(AddClient, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.dep = departament
        query = 'SELECT id, name FROM genre'
        self.cursor.execute(query)
        for t in self.cursor.fetchall():
            self.exemption.addItem(str(t))
        self.Add.clicked.connect(self.correct_data)

    def correct_data(self):
        name = self.name.text()
        exemption = self.exemption.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        exemption_id = str(exemption[0])
        if exemption_id:
            try:
                query = f'SELECT id FROM book ORDER BY id DESC LIMIT 1'
                self.cursor.execute(query)
                self.name_id = self.cursor.fetchone()
                if not self.name_id:
                    self.name_id = [0]
                query = f"INSERT INTO book VALUES({int(self.name_id[0])+1}, '{name}', {self.dep}, {exemption_id})"
                self.cursor.execute(query)
                self.connection.commit()
                self.error.setText('Успешно добавлено')
            except Exception as err:
                print(err)
                self.error.setText('Что-то пошло не так :(')
        else:
            self.error.setText('Проверьте корректность заполнения полей!')


class Queries(QMainWindow, queries.Ui_Dialog):
    def __init__(self, connection, cursor):
        super(Queries, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.queries.currentTextChanged.connect(self.handle_queries_change)  # Подключение сигнала
        self.queries.addItem('Симметричное внутреннее соединение с условием отбора по внешнему ключу')
        self.queries.addItem('Симметричное внутреннее соединение с условием отбора по внешнему ключу (2)')
        self.queries.addItem('Симметричное внутреннее соединение с условием отбора по датам')
        self.queries.addItem('Симметричное внутреннее соединение с условием отбора по датам (2)')
        self.queries.addItem('Симметричное внутреннее соединение без условия')
        self.queries.addItem('Симметричное внутреннее соединение без условия (2)')
        self.queries.addItem('Симметричное внутреннее соединение без условия (3)')
        self.queries.addItem('Левое внешнее соединение')
        self.queries.addItem('Правое внешнее соединение')
        self.queries.addItem('Запрос на запросе по принципу левого соединения')
        self.queries.addItem('Итоговый запрос без условия')
        self.queries.addItem('Итоговый запрос с условием на данные')
        self.queries.addItem('Итоговый запрос с условием на группы')
        self.queries.addItem('Итоговый запрос с условием на данные и на группы')
        self.queries.addItem('Запрос на запросе по принципу итогового запроса')
        self.queries.addItem('Запрос с подзапросом')

    def handle_queries_change(self):
        if self.queries.currentText() == 'Симметричное внутреннее соединение с условием отбора по внешнему ключу':
            self.hide_all()
            self.label_combo.show()
            self.label_combo.setText('Выберите тип собственности')
            self.comboBox.show()
            query = 'SELECT id, name FROM property_type'
            self.cursor.execute(query)
            for t in self.cursor.fetchall():
                self.comboBox.addItem(str(t))
            district = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
            district_id = str(district[0])
            self.labels = ['Издательство', 'Город', 'Телефон']
            self.query = f'SELECT * FROM q1({district_id})'
            self.comboBox.currentTextChanged.connect(self.q1)
        elif self.queries.currentText() == 'Симметричное внутреннее соединение с условием отбора по внешнему ключу (2)':
            self.hide_all()
            self.hide_all()
            self.label_combo.show()
            self.comboBox.show()
            self.label_combo.setText('Выберите страну')
            self.comboBox.show()
            query = 'SELECT id, name FROM country'
            self.cursor.execute(query)
            for t in self.cursor.fetchall():
                self.comboBox.addItem(str(t))
            exemption = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
            exemption_id = str(exemption[0])
            self.labels = ['Автор', 'Страна']
            self.query = f'SELECT * FROM q2({exemption_id})'
            self.comboBox.currentTextChanged.connect(self.q2)
        elif self.queries.currentText() == 'Симметричное внутреннее соединение с условием отбора по датам':
            self.hide_all()
            self.dateEdit.show()
            self.label_date.show()
            self.label_date.setText('Введите дату')
            self.dateEdit.dateChanged.connect(self.q3)  # Подключение сигнала
        elif self.queries.currentText() == 'Симметричное внутреннее соединение с условием отбора по датам (2)':
            self.hide_all()
            self.hide_all()
            self.label_text.show()
            self.dateEdit.show()
            self.label_date.setText('Введите дату')
            self.textEdit.textChanged.connect(self.q4)
        elif self.queries.currentText() == 'Симметричное внутреннее соединение без условия':
            self.hide_all()
            self.labels = ['Книга', 'Автор', 'Жанр']
            self.query = 'SELECT * FROM q5()'
        elif self.queries.currentText() == 'Симметричное внутреннее соединение без условия (2)':
            self.hide_all()
            self.labels = ['Издательство', 'Город', 'Год открытия']
            self.query = 'SELECT * FROM q6()'
        elif self.queries.currentText() == 'Симметричное внутреннее соединение без условия (3)':
            self.hide_all()
            self.labels = ['Книга', 'Язык']
            self.query = f'SELECT * FROM q7()'
        elif self.queries.currentText() == 'Левое внешнее соединение':
            self.hide_all()
            self.labels = ['Книга', 'Переплёт']
            self.query = f'SELECT * FROM q8()'
        elif self.queries.currentText() == 'ФИО, дата рождения по заданному типу клиента. Правое внешнее соединение':
            self.hide_all()
            self.labels = ['Книга', 'Переплёт']
            self.query = f'SELECT * FROM q9()'
        elif self.queries.currentText() == 'Запрос на запросе по принципу левого соединения':
            self.hide_all()
            self.textEdit.setText('')
            self.label_text.show()
            self.textEdit.show()
            self.label_text.setText('Выберите книгу')
            self.textEdit.textChanged.connect(self.q10)
        elif self.queries.currentText() == 'Итоговый запрос без условия':
            self.hide_all()
            self.labels = ['Издательство', 'Количество книг']
            self.query = f'SELECT * FROM q11()'
        elif self.queries.currentText() == 'Итоговый запрос с условием на данные':
            self.hide_all()
            self.label_text.show()
            self.textEdit.show()
            self.label_text_2.show()
            self.textEdit_2.show()
            self.textEdit.setText('')
            self.textEdit_2.setText('')
            self.label_text.setText('Выберите левую границу цены')
            self.label_text_2.setText('Выберите правую границу цены')
            self.textEdit.textChanged.connect(self.q12)
            self.textEdit_2.textChanged.connect(self.q12)
            self.excel_btn.show()
            self.graph_btn.show()
        elif self.queries.currentText() == 'Итоговый запрос с условием на группы':
            self.hide_all()
            self.label_text.show()
            self.textEdit.show()
            self.label_text.setText('Выберите количество книг')
            self.textEdit.textChanged.connect(self.q13)
            self.excel_btn.show()
            self.graph_btn.show()
        elif self.queries.currentText() == 'Итоговый запрос с условием на данные и на группы':
            self.hide_all()
            self.label_text.show()
            self.textEdit.show()
            self.label_text_2.show()
            self.textEdit_2.show()
            self.label_text_3.show()
            self.textEdit_3.show()
            self.textEdit.setText('')
            self.textEdit_2.setText('')
            self.label_text.setText('Выберите левую границу цены')
            self.label_text_2.setText('Выберите правую границу цены')
            self.label_text_3.setText('Выберите количество книг')
            self.textEdit.textChanged.connect(self.q14)
            self.textEdit_2.textChanged.connect(self.q14)
            self.textEdit_3.textChanged.connect(self.q14)
            self.excel_btn.show()
            self.graph_btn.show()
        elif self.queries.currentText() == 'Запрос на запросе по принципу итогового запроса':
            self.hide_all()
            self.label_text.show()
            self.textEdit.show()
            self.label_text.setText('Выберите количество книг')
            self.textEdit.textChanged.connect(self.q15)
            self.excel_btn.show()
            self.graph_btn.show()
        elif self.queries.currentText() == 'Запрос с подзапросом':
            self.hide_all()
            self.label_combo.show()
            self.comboBox.show()
            self.label_combo.setText('Выберите страну')
            self.comboBox.show()
            query = 'SELECT id, name FROM country'
            self.cursor.execute(query)
            for t in self.cursor.fetchall():
                self.comboBox.addItem(str(t))
            city = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
            city_id = str(city[1])
            self.labels = ['Автор']
            self.query = f'SELECT * FROM q16({city_id})'
            self.comboBox.currentTextChanged.connect(self.q16)
        self.print.clicked.connect(self.to_print)
        self.graph_btn.clicked.connect(self.create_chart)
        self.excel_btn.clicked.connect(self.export_to_excel)

    def hide_all(self):
        self.label_text.hide()
        self.textEdit.hide()
        self.label_combo.hide()
        self.comboBox.hide()
        self.label_text_2.hide()
        self.comboBox.clear()
        self.textEdit_2.hide()
        self.textEdit.clear()
        self.textEdit_2.clear()
        self.textEdit_3.clear()
        self.label_text_3.hide()
        self.textEdit_3.hide()
        self.dateEdit.hide()
        self.label_date.hide()
        self.graph_btn.hide()
        self.excel_btn.hide()

    def q1(self):
        district = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        district_id = str(district[0])
        self.labels = ['Издательство', 'Город', 'Телефон']
        self.query = f'SELECT * FROM q1({district_id})'

    def q2(self):
        exemption = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        exemption_id = str(exemption[0])
        self.labels = ['Автор', 'Страна']
        self.query = f'SELECT * FROM q2({exemption_id})'

    def q3(self):
        date = self.dateEdit.text()
        self.labels = ['Автор', 'Страна', 'Дата рождения']
        self.query = f"SELECT * FROM q3('{date}')"

    def q4(self):
        year = self.textEdit.text()
        self.labels = ['Автор', 'Страна', 'Дата смерти']
        self.query = f'SELECT * FROM q4({year})'

    def q10(self):
        name = self.textEdit.text()
        self.labels = ['Книга', 'Переплёт', 'Издательство']
        self.query = f"SELECT * FROM q10('{name}')"

    def q12(self):
        organ1 = self.textEdit.text()
        organ2 = self.textEdit_2.text()
        self.labels = ['Издательство', 'Количество книг']
        self.query = f'SELECT * FROM q12({organ1}, {organ2})'

    def q13(self):
        book_count = self.textEdit.text()
        self.labels = ['Издательство', 'Количество книг']
        self.query = f'SELECT * FROM q13({book_count})'

    def q14(self):
        organ1 = self.textEdit.text()
        organ2 = self.textEdit_2.text()
        helps = self.textEdit_3.text()
        self.labels = ['Издательство', 'Количество книг']
        self.query = f'SELECT * FROM q14({organ1}, {organ2}, {helps})'

    def q15(self):
        helps = self.textEdit.text()
        self.labels = ['Номер издательства']
        self.query = f'SELECT * FROM q15({helps})'

    def q16(self):
        query = 'SELECT id, name FROM country'
        self.cursor.execute(query)
        for t in self.cursor.fetchall():
            self.comboBox.addItem(str(t))
        dist = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        dist_id = str(dist[1])
        self.query = f'SELECT * FROM q16({dist_id})'

    def create_chart(self):
        self.label = self.queries.currentText()
        self.chart = Chart(self.connection, self.cursor, self.query, self.label)
        self.chart.show()

    def to_print(self):
        try:
            self.cursor.execute(self.query)
            self.rows = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(self.rows))
            self.tableWidget.setColumnCount(len(self.labels))
            self.tableWidget.setHorizontalHeaderLabels(self.labels)
            i = 0
            for elem in self.rows:
                j = 0
                for t in elem:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(t).strip()))
                    j += 1
                i += 1
            i = 0
            self.tableWidget.resizeColumnsToContents()
        except psycopg2.Error as err:
            print(err)
            self.error.setText('Проверьте ввод!')

    def export_to_excel(self):
        self.label = self.queries.currentText().split('. ')
        self.cursor = self.connection.cursor()
        book = openpyxl.Workbook()
        sheet = book.active
        self.cursor.execute(self.query)
        results = self.cursor.fetchall()
        i = 0
        for row in results:
            i += 1
            j = 1
            for col in row:
                cell = sheet.cell(row=i, column=j)
                cell.value = col
                j += 1
        try:
            book.save(f"{self.label[1]}.xlsx")
            self.error.setText('Успешно!')
        except Exception as err:
            print(err)
            self.error.setText('Ошибка!')


class Chart(QMainWindow, graphics.Ui_Dialog):
    def __init__(self, connection, cursor, query, label):
        super(Chart, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.query = query
        self.label = label.split('. ')
        self.cursor.execute(self.query)
        self.graphics_name.setText(self.label[0])
        data = self.cursor.fetchall()
        categories = [str(row[0]) for row in data]
        values = [row[1] for row in data]
        series = QBarSeries()
        bar_set = QBarSet("Количество книг")
        for value in values:
            bar_set.append(value)
        bar_set.setColor(QColor('pink'))
        series.append(bar_set)
        chart = QChart()
        chart.addSeries(series)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        scene = QGraphicsScene()
        scene.addItem(chart)
        chart.setMinimumSize(500, 500)
        scene.setSceneRect(chart.rect())
        self.graphicsView.setScene(scene)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AuthWindow()

    window.show()
    sys.exit(app.exec_())
