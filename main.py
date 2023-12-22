
from datetime import datetime
import sys
import os
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.utils import platform
from kivy.core.window import Window
from database import Database

if hasattr(sys, '_MEIPASS'):
    os.environ['KIVY_NO_CONSOLELOG'] = '1'

database = Database()


def validate_empty(*args):
    errors = False

    for campo in args:
        if campo.text == "":
            campo.error = True
            errors = True

    return errors


class LoginScreen(MDScreen):
    def login(self):
        username = self.ids.user
        password = self.ids.password

        empty = validate_empty(username, password)

        if empty:
            self.ids.messages.text = "Todos los campos son requeridos."
            return

        res = database.get_user(username.text)

        if (res['status'] == False):
            app_instance = MDApp.get_running_app()
            app_instance.show_dialog()
        else:
            if (res['data'][2] != password.text):
                self.ids.messages.text = "Contraseña incorrecta."
                password.error = True
                return

            self.manager.transition.direction = 'left'
            self.manager.current = 'app_screen'

    def show_new_account_screen(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'new_account_screen'


class NewAccountScreen(MDScreen):

    def new_account(self):
        new_username = self.ids.new_user
        new_password = self.ids.new_user_password
        nombre = self.ids.nombre
        apellido = self.ids.apellido

        empty = validate_empty(new_username, new_password, nombre, apellido)

        if empty:
            self.ids.messages.text = "Todos los campos son requeridos."
            return

        res = database.get_user(new_username.text)

        if (res['status'] == True):
            self.ids.messages.text = "Ya existe una cuenta con este nombre de usuario."
            return

        database.create_user(
            new_username.text, new_password.text, nombre.text, apellido.text)

        self.ids.messages.theme_text_color = "Custom"
        self.ids.messages.text_color = "green"
        self.ids.messages.text = "Cuenta creada con exito!"

        Clock.schedule_once(
            lambda arg: (self.show_login_screen(), self.clean()), 2)

    def show_login_screen(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login_screen'

    def clean(self):
        self.ids.messages.theme_text_color = "Error"
        self.ids.messages.text = ""

        self.ids.new_user.text = ""
        self.ids.new_user_password.text = ""
        self.ids.nombre.text = ""
        self.ids.apellido.text = ""


class AddBookDialog(MDBoxLayout):
    menu_dropdown = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        date = value.strftime('%A %d %B %Y')
        self.ids.fecha.text = str(date)

    def menu_open_category(self):
        categorias_libros = [
            "Novela",
            "Realismo mágico",
            "Fantasía",
            "Thriller",
            "Novela gótica",
            "Novela histórica",
            "Novela filosófica",
            "Ciencia ficción",
            "Misterio",
            "Aventura",
            "Biografía",
            "Poesía"
        ]
        menu_items = [
            {
                "text": categorias,
                "on_release": lambda x=categorias: self.menu_callback(self.ids.categoria, x),
            } for categorias in categorias_libros
        ]
        if not self.menu_dropdown:
            self.menu_dropdown = MDDropdownMenu(
                caller=self.ids.categoria, items=menu_items, position="bottom"
            )

            self.menu_dropdown.open()

    def menu_open_lang(self):
        menu_items = [
            {
                "text": "Español",
                "on_release": lambda x=f"Español": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Ingles",
                "on_release": lambda x=f"Ingles": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Alemán",
                "on_release": lambda x=f"Aleman": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Portugués",
                "on_release": lambda x=f"Portugues": self.menu_callback(self.ids.idioma, x),
            }
        ]

        if not self.menu_dropdown:
            self.menu_dropdown = MDDropdownMenu(
                caller=self.ids.idioma, items=menu_items, position="top"
            )
            self.menu_dropdown.open()

    def menu_callback(self, text_box, text_item):
        text_box.text = text_item
        self.menu_dropdown.dismiss()
        self.menu_dropdown = None

class FilterDialog(MDBoxLayout):
    menu_dropdown = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def menu_open_category(self):
        categorias_libros = [
            "Novela",
            "Realismo mágico",
            "Fantasía",
            "Thriller",
            "Novela gótica",
            "Novela histórica",
            "Novela filosófica",
            "Ciencia ficción",
            "Misterio",
            "Aventura",
            "Biografía",
            "Poesía"
        ]
        menu_items = [
            {
                "text": categorias,
                "on_release": lambda x=categorias: self.menu_callback(x),
            } for categorias in categorias_libros
        ]
        self.menu_dropdown = MDDropdownMenu(
            caller=self.ids.categoria,
            items=menu_items,
            position="bottom",
        )
        self.menu_dropdown.open()

    def menu_callback(self, text_item):
        print("Categoría seleccionada:", text_item)
        self.menu_dropdown.dismiss()

class MiCard(MDCard):
    titulo = StringProperty()
    autor = StringProperty()
    anyo = StringProperty()
    precio = StringProperty()
    categoria = StringProperty()
    descripcion = StringProperty()
    idioma = StringProperty()
    imagen = StringProperty("images/default.jpg")

    def __init__(self, libro_id=None, titulo="", imagen="", **kwargs):
        super().__init__(**kwargs)
        self.titulo = titulo
        self.libro_id = libro_id

        if os.path.exists(imagen):
            self.imagen = imagen

    def eliminar_libro(self, libro_id):
        database.delete_book(libro_id)
        self.parent.remove_widget(self)


class AppScreen(MDScreen):
    _add_book_dialog = None
    _filtros_dialog = None

    def show_add_book_dialog(self):
        if not self._add_book_dialog:
            self._add_book_dialog = MDDialog(
                title="Agregar libro",
                type="custom",
                content_cls=AddBookDialog(),
            )
        self._add_book_dialog.open()

    def close_add_book_dialog(self):
        self._add_book_dialog.dismiss()
        self._add_book_dialog = None

    def log_out(self):
        # database.log_out_user()
        self.manager.transition.direction = 'right'
        self.manager.current = "login_screen"

    def on_pre_enter(self):
        books = database.get_all_books()
        grid = self.ids.grid

        for book in books:
            imagen = "images/" + str(book[0]) + ".jpg"
            titulo = book[1]
            new_widget = MiCard(libro_id=book[0], titulo=titulo, imagen=imagen)
            grid.add_widget(new_widget)

    def show_add_book_dialog(self):
        if not self._add_book_dialog:
            self._add_book_dialog = MDDialog(
                title="Agregar libro",
                type="custom",
                content_cls=AddBookDialog(),
            )
        self._add_book_dialog.open()

    def show_filter_dialog(self):
        if not self._filtros_dialog:
            self._filtros_dialog = MDDialog(
                title="Filtrar por Categoría",
                type="custom",
                content_cls=FilterDialog(),
            )
        self._filtros_dialog.open()


class MainApp(MDApp):
    dialog = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Purple"
        self.title = "Trabajo Final"

        if platform != 'android':
            Window.size = (900, 800)

        self.manager = MDScreenManager()
        self.manager.add_widget(LoginScreen(name='login_screen'))
        self.manager.add_widget(AppScreen(name='app_screen'))
        self.manager.add_widget(NewAccountScreen(name='new_account_screen'))

        self.manager.current = "app_screen"

        return self.manager

    def show_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Usuario no registrado",
                text="¿Desea crear una una nueva cuenta de usuario?",
                buttons=[
                    MDFlatButton(
                        text="ACEPTAR",
                        md_bg_color="purple",
                        theme_text_color="Custom",
                        text_color="white",
                        on_release=lambda *args: self.show_new_account_screen(),
                    ),
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda *args: self.close_dialog()
                    ),
                ],
            )
        self.dialog.open()

    def show_dialog_delete_book(self, libro_id, titulo, instance):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Eliminar libro",
                text=f"Estas eliminando el libro {titulo}, ¿quieres continuar?",
                buttons=[
                    MDFlatButton(
                        text="ACEPTAR",
                        md_bg_color="purple",
                        theme_text_color="Custom",
                        text_color="white",
                        on_release=lambda *args: (instance.eliminar_libro(
                            libro_id), self.close_dialog()),
                    ),
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda *args: self.close_dialog()
                    ),
                ],
            )
        self.dialog.open()

    def close_dialog(self):
        self.dialog.dismiss()
        self.dialog = None

    def show_new_account_screen(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'new_account_screen'
        self.dialog.dismiss()

    def close_add_book_dialog(self):
        app_screen = self.root.get_screen('app_screen')
        app_screen.close_add_book_dialog()

    def add_book(self, titulo, categoria, autor, precio, descripcion, idioma, imagen, fecha):
        print(titulo.text, categoria.text, autor.text, precio.text,
              descripcion.text, idioma.text, imagen.text, fecha.text)

        database.insert_book(titulo.text, autor.text, fecha.text, precio.text,
                             categoria.text, descripcion.text, idioma.text)

        app_screen = self.root.get_screen('app_screen')
        grid = app_screen.ids.grid
        new_widget = MiCard(titulo.text, imagen.text)
        grid.add_widget(new_widget)

    def search_books(self, categoria):
        pass

    def close_filter_dialog(self):
        app_screen = self.root.get_screen('app_screen')
        app_screen.close_filter_dialog()


MainApp().run()
