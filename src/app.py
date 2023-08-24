"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Book, Cast
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route("/spec")
def spec():
    return jsonify(swagger(app))


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# endpoint (todos los personajes)


@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    serialized_characters = [character.serialize() for character in characters]
    return jsonify(serialized_characters)

# endpoint (un personaje)


@app.route('/character/<int:id>', methods=['GET'])
def get_characters_by_id(id):
    character = Character.query.get(id)
    return jsonify(character.serialize())

# endpoint para crear un personaje


@app.route('/character', methods=['POST'])
def create_character():
    data = request.get_json()  # objeto(request).metodo(get_json)
    data_name = data.get("name", None)
    data_gender = data.get("gender", None)
    data_species = data.get("species", None)
    data_is_alive = data.get("is_alive", None)
    # Obtener los datos para crear el personaje
    # Creando el nuevo personaje
    new_character = Character(name=data_name, gender=data_gender,
                              species=data_species, is_alive=data_is_alive)

    # Intentando ejecutar este bloque
    try:
        db.session.add(new_character)  # fallo aca
        # Confirmamos que se tiene que guardar
        db.session.commit()  # fallo aca
        return jsonify(new_character.serialize()), 201

    # Si no se puede cae aca
    except Exception as error:
        db.session.rollback()
        return error, 500  # 500 -> Error de servidor

# PUT | actualizar | id


@app.route('/character/<int:id>', methods=['PUT'])
def modify_character(id):
    # Obtener la informacion del body
    data = request.get_json()
    # Quiero "desglosar"
    name = data.get("name", None)
    gender = data.get("gender", None)
    species = data.get("species", None)
    is_alive = data.get("is_alive", None)
    # Buscar al personaje que vamos a actualizar
    character_to_edit = Character.query.get(id)

    # si el personaje no existe termina la funcion con un 404
    if not character_to_edit:
        return jsonify({"error": "Character not found"}), 404

    # modificamos los valores de los personajes
    character_to_edit.name = name
    character_to_edit.gender = gender
    character_to_edit.species = species
    character_to_edit.is_alive = is_alive

    try:
        db.session.commit()
        return jsonify({"character": character_to_edit.serialize()}), 200

    except Exception as error:
        db.session.rollback()
        return error
# Necesitamos con el metodo delete necesitamos recibir el id


@app.route('/character/<int:id>', methods=['DELETE'])
def delete_character_by_id(id):
    # Buscar el personaje en la bbdd
    character_to_delete = Character.query.get(id)
    if not character_to_delete:
        return jsonify({'error': 'Character not found'}), 404

    try:
        db.session.delete(character_to_delete)
        db.session.commit()
        return jsonify("character deleted successfully"), 200
    except Exception as error:
        db.session.rollback()
        return error

# CRUD de Libros
# CRUD de cast


# GET all
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    serialized_books = [book.serialize() for book in books]
    return jsonify(serialized_books), 200


# GET by id
@app.route('/book/<int:id>', methods=['GET'])
def get_book_by_id(id):
    current_book = Book.query.get(id)
    if not current_book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(current_book.serialize()), 200


# [POST] create book
@app.route('/book', methods=['POST'])
def create_book():
    data = request.get_json()
    name = data.get("name", None)
    order = data.get("order", None)
    release_date = data.get("release_date", None)

    try:
        new_book = Book(name=name, order=order, release_date=release_date)
        db.session.add(new_book)
        db.session.commit()
        return jsonify(new_book.serialize()), 201

    except Exception as error:
        db.session.rollback()
        return jsonify(error), 500


# [DELETE] delete a book
@app.route('/book/<int:id>', methods=['DELETE'])
def delete_book_by_id(id):
    book_to_delete = Book.query.get(id)

    if not book_to_delete:
        return jsonify({"error": "Book not found"}), 404

    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        return jsonify("Book deleted successfully"), 200

    except Exception as error:
        db.session.rollback()
        return error, 500


# PUT
@app.route('/book/<int:id>', methods=['PUT'])
def update_book_by_id(id):
    data = request.get_json()
    name = data.get("name", None)
    order = data.get("order", None)
    release_date = data.get("release_date", None)

    update_book = Book.query.get(id)
    if not update_book:
        return jsonify({"error": "Book not found"}), 404

    try:
        update_book.name = name
        update_book.order = order
        update_book.release_date = release_date
        db.session.commit()
        return jsonify({"book": update_book.serialize()}), 200

    except Exception as error:
        db.session.rollback()
        return error, 500

# CRUD CAST
# [POST]


@app.route('/cast/<int:book_id>/<int:character_id>', methods=['POST'])
def create_cast(book_id, character_id):
    # Verificar que esos IDS que me estan mandando sean reales
    book_to_cast = Book.query.get(book_id)
    character_to_cast = Character.query.get(character_id)

    if not book_to_cast or not character_to_cast:
        return jsonify({"error": "Book or character not found"}), 404

    # EVITAR dos veces la misma instancia del cast
    # filter_by
    cast_exists = Cast.query.filter_by(
        book_id=book_id, character_id=character_id).first()

    if cast_exists:
        return jsonify({"error": "Ya existe ese personaje en el libro"}), 400

    cast = Cast(book_id=book_id, character_id=character_id)
    try:
        db.session.add(cast)
        db.session.commit()
        return jsonify({"cast member": cast.serialize()}), 201
    except Exception as error:
        db.session.rollback()
        return error, 500

# Que me traiga todos los personajes que salieron en un libro X
# [GET]


@app.route('/cast/book/<int:id>', methods=['GET'])
def get_characters_from_book(id):
    casts = Cast.query.filter_by(book_id=id).all()
    if not casts:
        return jsonify({"error": "No cast member found"}), 404

    return jsonify({"cast": [cast.serialize() for cast in casts]})

# Buscar los libros en que aparece un personaje


@app.route('/cast/character/<int:id>', methods=['GET'])
def get_books_from_character(id):
    casts = Cast.query.filter_by(character_id=id).all()
    if not casts:
        return jsonify({"error": "No books for this character"}), 404

    return jsonify({"books": [book.serialize() for book in casts]})


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
