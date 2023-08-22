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
from models import db, User, Character
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


# CRUD(Create, Read, Update, Delete)
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
