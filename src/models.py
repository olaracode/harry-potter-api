from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# IMPORTANTE: Cada vez que modifiquemos los datos de una clase
# o Creemos una clase
# Tenemos que correr las migraciones de la base de datos
# pipenv run migrate -> Oye mira estos modelos
# pipenv run upgrade -> Actualizate con estas tablas


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

# Quiero crear una clase Personaje, Escuela, Pelicula, Libro


class Character(db.Model):
    __tablename__ = "character"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    gender = db.Column(db.String(20), unique=False, nullable=False)
    species = db.Column(db.String(40), unique=False, nullable=False)
    is_alive = db.Column(db.Boolean, unique=False, nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey("house.id"), nullable=True)
    casted = db.relationship("Cast", backref="character", lazy=True)

    def __repr__(self):

        return f'Character {self.name}'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "species": self.species,
            "is_alive": self.is_alive
        }

# Libros


class House(db.Model):
    __tablename__ = 'house'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    characters = db.relationship('Character', backref='house', lazy=True)

    def __repr__(self):
        return f"<House {self.name}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # numero de orden
    order = db.Column(db.Integer, unique=True, nullable=False)
    release_date = db.Column(db.Date, unique=True, nullable=False)
    cast_members = db.relationship("Cast", backref="book", lazy=True)

    # Son los metodos de mi clase
    def __repr__(self):
        # Representacion visual
        return f'Book {self.name}'

    def serialize(self):
        # Para formatear la informacion
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "release_date": self.release_date
        }


class Cast(db.Model):
    __tablename__ = 'cast'
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey(
        "character.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    # movie_id = db.Column(....)

    def __repr__(self):
        return f'Cast {self.id}'

    def serialize(self):
        return {
            "id": self.id,
            "character_id": self.character_id,
            "book_id": self.book_id
        }
