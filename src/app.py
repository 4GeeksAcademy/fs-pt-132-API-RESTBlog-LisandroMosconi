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
from models import db, User, Film, Character, Location, Review, FavoriteFilm, FavoriteCharacter, FavoriteLocation
#from models import Person

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

# Need auth so we use a fixed user_id
CURRENT_USER_ID = 1

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Helper function to get the fake current user
def get_current_user():
    user = User.query.get(CURRENT_USER_ID)

    if user is None:
        raise APIException(
            "Current user does not exist. Please create a user with id 1 from the Flask admin.",
            status_code=404
        )

    return user

# -------------------------
# USERS
# -------------------------

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()

    return jsonify([user.serialize() for user in users]), 200


@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = get_current_user()

    favorite_films = FavoriteFilm.query.filter_by(user_id=user.id).all()
    favorite_characters = FavoriteCharacter.query.filter_by(user_id=user.id).all()
    favorite_locations = FavoriteLocation.query.filter_by(user_id=user.id).all()

    response_body = {
        "user": user.serialize(),
        "favorite_films": [
            favorite.film.serialize() for favorite in favorite_films
        ],
        "favorite_characters": [
            favorite.character.serialize() for favorite in favorite_characters
        ],
        "favorite_locations": [
            favorite.location.serialize() for favorite in favorite_locations
        ]
    }

    return jsonify(response_body), 200


# -------------------------
# FILMS
# -------------------------

@app.route("/films", methods=["GET"])
def get_films():
    films = Film.query.all()

    return jsonify([film.serialize() for film in films]), 200


@app.route("/films/<int:film_id>", methods=["GET"])
def get_single_film(film_id):
    film = Film.query.get(film_id)

    if film is None:
        raise APIException("Film not found", status_code=404)

    return jsonify(film.serialize()), 200


# -------------------------
# CHARACTERS / PEOPLE
# -------------------------

# /people is kept to match the original Star Wars project.
# /characters is the Ghibli version.
@app.route("/people", methods=["GET"])
@app.route("/characters", methods=["GET"])
def get_characters():
    characters = Character.query.all()

    return jsonify([character.serialize() for character in characters]), 200


@app.route("/people/<int:character_id>", methods=["GET"])
@app.route("/characters/<int:character_id>", methods=["GET"])
def get_single_character(character_id):
    character = Character.query.get(character_id)

    if character is None:
        raise APIException("Character not found", status_code=404)

    return jsonify(character.serialize()), 200


# -------------------------
# LOCATIONS / PLANETS
# -------------------------

# /planets is kept to match the original Star Wars project.
# /locations is the Ghibli version.
@app.route("/planets", methods=["GET"])
@app.route("/locations", methods=["GET"])
def get_locations():
    locations = Location.query.all()

    return jsonify([location.serialize() for location in locations]), 200


@app.route("/planets/<int:location_id>", methods=["GET"])
@app.route("/locations/<int:location_id>", methods=["GET"])
def get_single_location(location_id):
    location = Location.query.get(location_id)

    if location is None:
        raise APIException("Location not found", status_code=404)

    return jsonify(location.serialize()), 200


# -------------------------
# FAVORITE FILMS
# -------------------------

@app.route("/favorite/film/<int:film_id>", methods=["POST"])
def add_favorite_film(film_id):
    user = get_current_user()
    film = Film.query.get(film_id)

    if film is None:
        raise APIException("Film not found", status_code=404)

    favorite = FavoriteFilm.query.filter_by(
        user_id=user.id,
        film_id=film.id
    ).first()

    if favorite is not None:
        raise APIException("This film is already in favorites", status_code=400)

    new_favorite = FavoriteFilm(
        user_id=user.id,
        film_id=film.id
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({
        "msg": "Film added to favorites",
        "favorite": new_favorite.serialize()
    }), 201


@app.route("/favorite/film/<int:film_id>", methods=["DELETE"])
def delete_favorite_film(film_id):
    user = get_current_user()

    favorite = FavoriteFilm.query.filter_by(
        user_id=user.id,
        film_id=film_id
    ).first()

    if favorite is None:
        raise APIException("Favorite film not found", status_code=404)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "msg": "Film removed from favorites"
    }), 200


# -------------------------
# FAVORITE CHARACTERS / PEOPLE
# -------------------------

@app.route("/favorite/people/<int:character_id>", methods=["POST"])
@app.route("/favorite/character/<int:character_id>", methods=["POST"])
def add_favorite_character(character_id):
    user = get_current_user()
    character = Character.query.get(character_id)

    if character is None:
        raise APIException("Character not found", status_code=404)

    favorite = FavoriteCharacter.query.filter_by(
        user_id=user.id,
        character_id=character.id
    ).first()

    if favorite is not None:
        raise APIException("This character is already in favorites", status_code=400)

    new_favorite = FavoriteCharacter(
        user_id=user.id,
        character_id=character.id
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({
        "msg": "Character added to favorites",
        "favorite": new_favorite.serialize()
    }), 201


@app.route("/favorite/people/<int:character_id>", methods=["DELETE"])
@app.route("/favorite/character/<int:character_id>", methods=["DELETE"])
def delete_favorite_character(character_id):
    user = get_current_user()

    favorite = FavoriteCharacter.query.filter_by(
        user_id=user.id,
        character_id=character_id
    ).first()

    if favorite is None:
        raise APIException("Favorite character not found", status_code=404)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "msg": "Character removed from favorites"
    }), 200


# -------------------------
# FAVORITE LOCATIONS / PLANETS
# -------------------------

@app.route("/favorite/planet/<int:location_id>", methods=["POST"])
@app.route("/favorite/location/<int:location_id>", methods=["POST"])
def add_favorite_location(location_id):
    user = get_current_user()
    location = Location.query.get(location_id)

    if location is None:
        raise APIException("Location not found", status_code=404)

    favorite = FavoriteLocation.query.filter_by(
        user_id=user.id,
        location_id=location.id
    ).first()

    if favorite is not None:
        raise APIException("This location is already in favorites", status_code=400)

    new_favorite = FavoriteLocation(
        user_id=user.id,
        location_id=location.id
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({
        "msg": "Location added to favorites",
        "favorite": new_favorite.serialize()
    }), 201


@app.route("/favorite/planet/<int:location_id>", methods=["DELETE"])
@app.route("/favorite/location/<int:location_id>", methods=["DELETE"])
def delete_favorite_location(location_id):
    user = get_current_user()

    favorite = FavoriteLocation.query.filter_by(
        user_id=user.id,
        location_id=location_id
    ).first()

    if favorite is None:
        raise APIException("Favorite location not found", status_code=404)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "msg": "Location removed from favorites"
    }), 200


# -------------------------
# EXTRA: REVIEWS
# -------------------------

@app.route("/reviews", methods=["GET"])
def get_reviews():
    reviews = Review.query.all()

    return jsonify([review.serialize() for review in reviews]), 200


@app.route("/reviews/film/<int:film_id>", methods=["GET"])
def get_film_reviews(film_id):
    film = Film.query.get(film_id)

    if film is None:
        raise APIException("Film not found", status_code=404)

    reviews = Review.query.filter_by(film_id=film.id).all()

    return jsonify([review.serialize() for review in reviews]), 200


@app.route("/reviews/film/<int:film_id>", methods=["POST"])
def create_review(film_id):
    user = get_current_user()
    film = Film.query.get(film_id)

    if film is None:
        raise APIException("Film not found", status_code=404)

    body = request.get_json()

    if body is None:
        raise APIException("Request body is empty", status_code=400)

    rating = body.get("rating")
    comment = body.get("comment")

    if rating is None:
        raise APIException("Rating is required", status_code=400)

    new_review = Review(
        rating=rating,
        comment=comment,
        user_id=user.id,
        film_id=film.id
    )

    db.session.add(new_review)
    db.session.commit()

    return jsonify({
        "msg": "Review created",
        "review": new_review.serialize()
    }), 201


# This only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)