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
from models import db, User, Planet, Characters, FavoritePlanets, FavoriteCharacters

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
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
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_all_people():
    people_query = Characters.query.all()
    all_people = list(map(lambda x: x.serialize(), people_query))
    return jsonify(all_people), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = Characters.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets_query = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets_query))
    return jsonify(all_planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users_query))
    return jsonify(all_users), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"msg": "user_id is required as a query parameter"}), 400
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404

    favorite_planets = [fav.planet.serialize() for fav in user.favorite_planets]
    favorite_characters = [fav.character.serialize() for fav in user.favorite_characters]

    return jsonify({
        "favorite_planets": favorite_planets,
        "favorite_characters": favorite_characters
    }), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"msg": "user_id is required in JSON body"}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404

    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    existing_fav = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_fav:
        return jsonify({"msg": "Planet already in favorites"}), 400

    new_fav = FavoritePlanets(user_id=user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()

    return jsonify({"msg": "Favorite planet added"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"msg": "user_id is required in JSON body"}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404

    character = Characters.query.get(people_id)
    if character is None:
        return jsonify({"msg": "Person not found"}), 404

    existing_fav = FavoriteCharacters.query.filter_by(user_id=user_id, character_id=people_id).first()
    if existing_fav:
        return jsonify({"msg": "Person already in favorites"}), 400

    new_fav = FavoriteCharacters(user_id=user_id, character_id=people_id)
    db.session.add(new_fav)
    db.session.commit()

    return jsonify({"msg": "Favorite person added"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"msg": "user_id is required in JSON body"}), 400

    favorite = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite planet not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite planet deleted"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"msg": "user_id is required in JSON body"}), 400

    favorite = FavoriteCharacters.query.filter_by(user_id=user_id, character_id=people_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite person not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite person deleted"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
