from img import download_save_images
from database import Database
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.widget import MDWidget
from kivymd.uix.anchorlayout import MDAnchorLayout

# ---
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDIconButton
from kivymd.uix.widget import MDWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.imagelist.imagelist import MDSmartTile
# ---

from kivymd.uix.screenmanager import MDScreenManager
from kivymd.app import MDApp
import os
import sys
from datetime import datetime


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
        date_dialog = MDDatePicker(
            title="FECHA", title_input="INGRESA LA FECHA")
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        date = value.strftime('%A %d %B %Y')
        self.ids.fecha.text = str(date)

    def menu_open_category(self, textfield):
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

        self.menu_dropdown = MDDropdownMenu(
            caller=self.ids.categoria, items=menu_items
        )

        self.menu_dropdown.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        Window.release_all_keyboards()

        self.menu_dropdown.open()

    def menu_open_lang(self):
        menu_items = [
            {
                "text": "Español",
                "on_release": lambda x="Español": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Ingles",
                "on_release": lambda x="Ingles": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Alemán",
                "on_release": lambda x="Aleman": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Portugués",
                "on_release": lambda x="Portugues": self.menu_callback(self.ids.idioma, x),
            }
        ]

        self.menu_dropdown = MDDropdownMenu(
            caller=self.ids.idioma, items=menu_items, position="center"
        )

        self.menu_dropdown.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        Window.release_all_keyboards()
        self.menu_dropdown.open()

    def menu_callback(self, text_box, text_item):
        text_box.text = text_item
        self.menu_dropdown.dismiss()
        self.menu_dropdown = None


class FilterDialog(MDBoxLayout):
    menu_dropdown = None
    app_screen_instance = None

    def __init__(self, app_screen_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_screen_instance = app_screen_instance

    def menu_open_category(self):
        categorias_libros = [
            "Novela", "Realismo mágico", "Fantasía", "Thriller", "Novela gótica",
            "Novela histórica", "Novela filosófica", "Ciencia ficción", "Misterio",
            "Aventura", "Biografía", "Poesía"
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
        self.menu_dropdown.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        Window.release_all_keyboards()

        self.menu_dropdown.open()

    def menu_callback(self, text_item):
        if self.menu_dropdown:
            self.menu_dropdown.dismiss()
            self.menu_dropdown = None

        app_screen = MDApp.get_running_app().root.get_screen('app_screen')
        app_screen.show_books(text_item)
        self.app_screen_instance.close_filter_dialog()

    def show_all_books(self):
        app_screen = MDApp.get_running_app().root.get_screen('app_screen')
        app_screen.show_all_books()
        self.app_screen_instance.close_filter_dialog()


class InformationBookDialog(MDBoxLayout):
    autor = StringProperty()
    fecha = StringProperty()
    precio = StringProperty()
    categoria = StringProperty()
    descripcion = StringProperty()
    idioma = StringProperty()
    imagen = StringProperty()

    def __init__(self, instance=None, titulo=None, **kwargs):
        super().__init__(**kwargs)
        self.instance = instance
        # (1, 'Don Quijote', 'Miguel de Cervantes', '1605-01-01 00:00:00', 15000.0, 'Novela', 'Don Quijote de la Mancha es una novela que satiriza las novelas de caballería y la sociedad de la época.', 'Español')
        res = database.search_books(titulo)

        self.autor = res[2]

        fecha_final = res[3]
        if res[3] != "":
            fecha_str = res[3]
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            fecha_final = fecha_obj.strftime("%A %d %B %Y")

        self.fecha = fecha_final
        self.precio = str(res[4]).split(".")[0]
        self.categoria = res[5]
        self.descripcion = res[6]
        self.idioma = res[7]
        self.imagen = "images/" + str(res[0]) + ".jpg"


class EditBookDialog(MDBoxLayout):
    book_id = NumericProperty()
    menu_dropdown = None

    def __init__(self, instance=None, titulo=None, **kwargs):
        super().__init__(**kwargs)
        self.instance = instance

        res = database.search_books(titulo)

        self.book_id = res[0]

        self.ids.titulo.text = res[1]
        self.ids.autor.text = res[2]

        fecha_final = ""
        if res[3] != "":
            fecha_str = res[3]
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            fecha_final = fecha_obj.strftime("%A %d %B %Y")

        self.ids.fecha.text = fecha_final

        self.ids.precio.text = str(res[4]).split(".")[0]
        self.ids.categoria.text = res[5]
        self.ids.descripcion.text = res[6]
        self.ids.idioma.text = res[7]

    def close_edit_book_dialog(self):
        self.instance.dialog_edit.dismiss()

    def show_date_picker(self):
        date_dialog = MDDatePicker(
            title="FECHA", title_input="INGRESA LA FECHA")
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        date = value.strftime('%A %d %B %Y')
        self.ids.fecha.text = str(date)

    def menu_open_category(self, textfield):
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

        self.menu_dropdown = MDDropdownMenu(
            caller=self.ids.categoria, items=menu_items
        )

        self.menu_dropdown.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        Window.release_all_keyboards()

        self.menu_dropdown.open()

    def menu_open_lang(self):
        menu_items = [
            {
                "text": "Español",
                "on_release": lambda x="Español": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Ingles",
                "on_release": lambda x="Ingles": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Alemán",
                "on_release": lambda x="Aleman": self.menu_callback(self.ids.idioma, x),
            },
            {
                "text": "Portugués",
                "on_release": lambda x="Portugues": self.menu_callback(self.ids.idioma, x),
            }
        ]

        self.menu_dropdown = MDDropdownMenu(
            caller=self.ids.idioma, items=menu_items, position="center"
        )

        self.menu_dropdown.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        Window.release_all_keyboards()
        self.menu_dropdown.open()

    def menu_callback(self, text_box, text_item):
        text_box.text = text_item
        self.menu_dropdown.dismiss()
        self.menu_dropdown = None


class MiCard(MDCard):
    titulo = StringProperty()
    autor = StringProperty()
    fecha = StringProperty()
    precio = StringProperty()
    categoria = StringProperty()
    descripcion = StringProperty()
    idioma = StringProperty()
    imagen = StringProperty("images/default.jpg")
    dialog_information = None
    dialog_edit = None

    def __init__(self, libro_id=None, titulo="", imagen="", **kwargs):
        super().__init__(**kwargs)
        self.titulo = titulo
        self.libro_id = libro_id

        if os.path.exists("images/" + imagen):
            self.imagen = "images/" + imagen

    def eliminar_libro(self, libro_id):
        database.delete_book(libro_id)
        self.parent.remove_widget(self)

    def open_book_information(self):
        if not self.dialog_information:
            self.dialog_information = MDDialog(
                title=self.titulo,
                type="custom",
                content_cls=InformationBookDialog(self, self.titulo),
            )
        self.dialog_information.open()

    def close_information_dialog(self):
        self.dialog_information.dismiss()
        self.dialog_information = None

    def open_edit_book_dialog(self):
        if not self.dialog_edit:
            self.dialog_edit = MDDialog(
                title=f"Modificar la información del libro \"{self.titulo}\"",
                type="custom",
                content_cls=EditBookDialog(self, self.titulo),
            )
        self.dialog_edit.open()


class AppScreen(MDScreen):
    _add_book_dialog = None
    _filter_dialog = None

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

    def on_enter(self):
        books = database.get_all_books()
        grid = self.ids.grid

        grid.clear_widgets()

        for book in books:
            imagen = str(book[0]) + '.jpg'
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
        if not self._filter_dialog:
            self._filter_dialog = MDDialog(
                title="Filtrar por Categoría",
                type="custom",
                content_cls=FilterDialog(app_screen_instance=self),
            )
        self._filter_dialog.open()

    def show_books(self, categoria):
        books = database.get_books_by_category(categoria)
        grid = self.ids.grid

        grid.clear_widgets()

        for book in books:
            imagen = str(book[0]) + ".jpg"
            titulo = book[1]
            new_widget = MiCard(libro_id=book[0], titulo=titulo, imagen=imagen)
            grid.add_widget(new_widget)

    def show_all_books(self):
        books = database.get_all_books()
        grid = self.ids.grid

        grid.clear_widgets()

        for book in books:
            imagen = str(book[0]) + ".jpg"
            titulo = book[1]
            new_widget = MiCard(libro_id=book[0], titulo=titulo, imagen=imagen)
            grid.add_widget(new_widget)

        self.close_filter_dialog()

    def close_filter_dialog(self):
        if self._filter_dialog is not None:
            self._filter_dialog.dismiss()
            self._filter_dialog = None


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

        self.manager.current = "login_screen"

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
                        on_release=lambda *args: (
                            self.show_new_account_screen(), self.close_dialog()),
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

    def get_screen_instance(self, screen):
        return self.root.get_screen(screen)

    def add_book(self, titulo, categoria, autor, precio, descripcion, idioma, imagen, fecha):

        empty = validate_empty(titulo, categoria, descripcion)

        if empty:
            return

        res = database.insert_book(titulo.text, autor.text, fecha.text, precio.text,
                                   categoria.text, descripcion.text, idioma.text)

        if imagen.text != "" and res:
            download_save_images(imagen.text, 'images/', str(res))

        app_screen = self.root.get_screen('app_screen')
        grid = app_screen.ids.grid
        new_widget = MiCard(res, titulo.text, str(res) + '.jpg')
        grid.add_widget(new_widget)

        app_screen.close_add_book_dialog()

    def close_filter_dialog(self):
        app_screen = self.root.get_screen('app_screen')
        app_screen.close_filter_dialog()

    def update_book(self, book_id, titulo, categoria, autor, precio, descripcion, idioma, imagen, fecha):
        print("update book", book_id)

        app_screen = self.root.get_screen('app_screen')
        widget_list = app_screen.ids.grid.children

        empty = validate_empty(titulo, categoria, descripcion)

        if empty:
            return

        database.update_book(book_id, titulo.text, autor.text, fecha.text,
                             precio.text, categoria.text, descripcion.text, idioma.text)

        if imagen.text != "":
            download_save_images(imagen.text, 'images/', str(book_id))

        widget_list[-book_id].titulo = titulo.text
        widget_list[-book_id].imagen = "images/" + str(book_id) + ".jpg"
        widget_list[-book_id].ids.smart_tile.source = "images/" + \
            str(book_id) + ".jpg"

        widget_list[-book_id].ids.smart_tile.ids.image.reload()


MainApp().run()
