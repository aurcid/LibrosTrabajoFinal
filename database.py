import sqlite3
from datetime import datetime


class Database:
    def __init__(self):
        self.con = sqlite3.connect('data.db')
        self.cursor = self.con.cursor()
        self.create_user_table()
        self.create_books_table()

        if len(self.get_all_books()) == 0:
            self.inserts_books_by_default()

    def create_user_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS usuario(id integer PRIMARY KEY AUTOINCREMENT, usuario varchar(60) NOT NULL, password varchar(60) NOT NULL, nombre varchar(60) NOT NULL, apellido varchar(60) NOT NULL, logged_in integer NOT NULL DEFAULT 0)")
        self.con.commit()

    def create_user(self, usuario, password, nombre, apellido):
        self.cursor.execute(
            "INSERT INTO usuario(usuario, password, nombre, apellido, logged_in) VALUES(?, ?, ?, ?, 0)", (usuario, password, nombre, apellido))
        self.con.commit()

    def get_user(self, username):
        user = self.cursor.execute(
            "SELECT * FROM usuario WHERE usuario=?", (username,)).fetchone()

        if user:
            return {'status': True, 'data': user}
        else:
            return {'status': False}

    def log_out_user(self, username):
        self.cursor.execute(
            "UPDATE usuario SET logged_in = 0 WHERE usuario = ?", (username,))
        self.con.commit()

    def create_books_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS libros(id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, autor TEXT NOT NULL, fecha TEXT NOT NULL, precio REAL NOT NULL, categoria TEXT NOT NULL, descripcion TEXT NOT NULL, idioma TEXT NOT NULL)")
        self.con.commit()

    def inserts_books_by_default(self):
        books = [
            {
                "titulo": "Don Quijote",
                "autor": "Miguel de Cervantes",
                "fecha": datetime(1605, 1, 1),
                "precio": 15000,
                "categoria": "Novela",
                "descripcion": "Don Quijote de la Mancha es una novela que satiriza las novelas de caballería y la sociedad de la época.",
                "idioma": "Español"
            },
            {
                "titulo": "Cien años de soledad",
                "autor": "Gabriel García Márquez",
                "fecha": datetime(1967, 1, 1),
                "precio": 18000,
                "categoria": "Realismo mágico",
                "descripcion": "Cien años de soledad es una novela que explora la historia de la familia Buendía en el pueblo ficticio de Macondo.",
                "idioma": "Español"
            },
            {
                "titulo": "El señor de los anillos",
                "autor": "J.R.R. Tolkien",
                "fecha": datetime(1954, 1, 1),
                "precio": 22000,
                "categoria": "Fantasía",
                "descripcion": "El señor de los anillos es una trilogía épica que sigue la búsqueda de un anillo para destruir el mal en la Tierra Media.",
                "idioma": "Inglés"
            },
            {
                "titulo": "El código Da Vinci",
                "autor": "Dan Brown",
                "fecha": datetime(2003, 1, 1),
                "precio": 19000,
                "categoria": "Thriller",
                "descripcion": "El código Da Vinci es un thriller que sigue al profesor Robert Langdon en una búsqueda de secretos ocultos en obras de arte.",
                "idioma": "Inglés"
            },
            {
                "titulo": "Harry Potter y la piedra filosofal",
                "autor": "J.K. Rowling",
                "fecha": datetime(1997, 1, 1),
                "precio": 25000,
                "categoria": "Fantasía",
                "descripcion": "La primera entrega de la serie Harry Potter sigue las aventuras del joven mago Harry en Hogwarts.",
                "idioma": "Inglés"
            },
            {
                "titulo": "El retrato de Dorian Gray",
                "autor": "Oscar Wilde",
                "fecha": datetime(1890, 1, 1),
                "precio": 17000,
                "categoria": "Novela gótica",
                "descripcion": "El retrato de Dorian Gray es una novela que explora la moralidad y la decadencia a través del retrato envejeciente de un hombre.",
                "idioma": "Inglés"
            },
            {
                "titulo": "El perfume",
                "autor": "Patrick Süskind",
                "fecha": datetime(1985, 1, 1),
                "precio": 20000,
                "categoria": "Novela histórica",
                "descripcion": "El perfume sigue la vida de Jean-Baptiste Grenouille, un asesino obsesionado con el sentido del olfato.",
                "idioma": "Alemán"
            },
            {
                "titulo": "El alquimista",
                "autor": "Paulo Coelho",
                "fecha": datetime(1988, 1, 1),
                "precio": 16000,
                "categoria": "Novela filosófica",
                "descripcion": "El alquimista narra el viaje de Santiago en busca de su tesoro personal y la realización de sus sueños.",
                "idioma": "Portugués"
            }
        ]

        for book in books:
            self.cursor.execute("INSERT INTO libros (titulo, autor, fecha, precio, categoria, descripcion, idioma) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (book["titulo"], book["autor"], book["fecha"], book["precio"], book["categoria"], book["descripcion"], book["idioma"]))

            self.con.commit()

    def insert_book(self, titulo, autor, fecha, precio, categoria, descripcion, idioma):
        fecha_original = fecha
        fecha_objeto = datetime.strptime(fecha_original, "%A %d %B %Y")
        fecha_final = fecha_objeto.strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute(
            "INSERT INTO libros(titulo, autor, fecha, precio, categoria, descripcion, idioma) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (titulo, autor, fecha_final, precio, categoria, descripcion, idioma)
        )
        self.con.commit()

        book = self.search_books(titulo)

        if book:
            return book[0]

    def delete_book(self, book_id):
        self.cursor.execute("DELETE FROM libros WHERE id=?", (book_id,))
        self.con.commit()

    def update_book(self, book_id, titulo, autor, fecha, precio, categoria, descripcion, idioma):
        fecha_original = fecha
        fecha_objeto = datetime.strptime(fecha_original, "%A %d %B %Y")
        fecha_final = fecha_objeto.strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute(
            "UPDATE libros SET titulo=?, autor=?, fecha=?, precio=?, categoria=?, descripcion=?, idioma=? WHERE id=?",
            (titulo, autor, fecha_final, precio, categoria,
             descripcion, idioma, book_id)
        )
        self.con.commit()

    def search_books(self, search):
        books = self.cursor.execute(
            "SELECT * FROM libros WHERE titulo LIKE ? OR autor LIKE ?",
            (f"%{search}%", f"%{search}%")
        ).fetchone()
        return books

    def get_all_books(self):
        books = self.cursor.execute("SELECT * FROM libros").fetchall()
        return books

    def get_books_by_category(self, categoria):
        books = self.cursor.execute(
            "SELECT * FROM libros WHERE categoria = ?",
            (categoria,)
        ).fetchall()
        return books

    def close_db_connection(self):
        self.con.close()
