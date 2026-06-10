# COPIED FROM THE LAST PROJECT

import os
from flask_admin import Admin
from models import db, User, Film, Character, Location, Review, FavoriteFilm, FavoriteCharacter, FavoriteLocation
from flask_admin.contrib.sqla import ModelView


class CharacterView(ModelView):
    form_columns = [
        "name",
        "gender",
        "age",
        "eye_color",
        "hair_color",
        "film"
    ]


class LocationView(ModelView):
    form_columns = [
        "name",
        "climate",
        "terrain",
        "surface_water",
        "film"
    ]


class ReviewView(ModelView):
    form_columns = [
        "rating",
        "comment",
        "user",
        "film"
    ]


class FavoriteFilmView(ModelView):
    form_columns = [
        "user",
        "film"
    ]


class FavoriteCharacterView(ModelView):
    form_columns = [
        "user",
        "character"
    ]


class FavoriteLocationView(ModelView):
    form_columns = [
        "user",
        "location"
    ]


def setup_admin(app):
    app.secret_key = os.environ.get("FLASK_APP_KEY", "sample key")
    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    admin = Admin(app, name="Ghibli Blog Admin", template_mode="bootstrap3")

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Film, db.session))
    admin.add_view(CharacterView(Character, db.session))
    admin.add_view(LocationView(Location, db.session))
    admin.add_view(ReviewView(Review, db.session))
    admin.add_view(FavoriteFilmView(FavoriteFilm, db.session))
    admin.add_view(FavoriteCharacterView(FavoriteCharacter, db.session))
    admin.add_view(FavoriteLocationView(FavoriteLocation, db.session))
