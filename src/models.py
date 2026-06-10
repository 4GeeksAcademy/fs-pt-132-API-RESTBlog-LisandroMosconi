# COPIED FROM THE LAST PROJECT

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    favorite_films: Mapped[list["FavoriteFilm"]] = relationship(back_populates="user")
    favorite_characters: Mapped[list["FavoriteCharacter"]] = relationship(back_populates="user")
    favorite_locations: Mapped[list["FavoriteLocation"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active
        }


class Film(db.Model):
    __tablename__ = "film"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    original_title: Mapped[str] = mapped_column(String(120), nullable=True)
    director: Mapped[str] = mapped_column(String(80), nullable=True)
    producer: Mapped[str] = mapped_column(String(80), nullable=True)
    release_date: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)

    characters: Mapped[list["Character"]] = relationship(back_populates="film")
    locations: Mapped[list["Location"]] = relationship(back_populates="film")
    reviews: Mapped[list["Review"]] = relationship(back_populates="film")
    favorites: Mapped[list["FavoriteFilm"]] = relationship(back_populates="film")

    def __repr__(self):
        return self.title

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "original_title": self.original_title,
            "director": self.director,
            "producer": self.producer,
            "release_date": self.release_date,
            "description": self.description,
            "image_url": self.image_url
        }


class Character(db.Model):
    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    gender: Mapped[str] = mapped_column(String(40), nullable=True)
    age: Mapped[str] = mapped_column(String(40), nullable=True)
    eye_color: Mapped[str] = mapped_column(String(40), nullable=True)
    hair_color: Mapped[str] = mapped_column(String(40), nullable=True)

    film_id: Mapped[int] = mapped_column(ForeignKey("film.id"), nullable=False)
    film: Mapped["Film"] = relationship(back_populates="characters")

    favorites: Mapped[list["FavoriteCharacter"]] = relationship(back_populates="character")

    def __repr__(self):
        return self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "eye_color": self.eye_color,
            "hair_color": self.hair_color,
            "film_id": self.film_id
        }


class Location(db.Model):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str] = mapped_column(String(80), nullable=True)
    terrain: Mapped[str] = mapped_column(String(80), nullable=True)
    surface_water: Mapped[str] = mapped_column(String(40), nullable=True)

    film_id: Mapped[int] = mapped_column(ForeignKey("film.id"), nullable=False)
    film: Mapped["Film"] = relationship(back_populates="locations")

    favorites: Mapped[list["FavoriteLocation"]] = relationship(back_populates="location")

    def __repr__(self):
        return self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "film_id": self.film_id
        }


class Review(db.Model):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    film_id: Mapped[int] = mapped_column(ForeignKey("film.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="reviews")
    film: Mapped["Film"] = relationship(back_populates="reviews")

    def serialize(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "comment": self.comment,
            "user_id": self.user_id,
            "film_id": self.film_id
        }


class FavoriteFilm(db.Model):
    __tablename__ = "favorite_film"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    film_id: Mapped[int] = mapped_column(ForeignKey("film.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorite_films")
    film: Mapped["Film"] = relationship(back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "film_id": self.film_id
        }


class FavoriteCharacter(db.Model):
    __tablename__ = "favorite_character"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorite_characters")
    character: Mapped["Character"] = relationship(back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }


class FavoriteLocation(db.Model):
    __tablename__ = "favorite_location"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorite_locations")
    location: Mapped["Location"] = relationship(back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "location_id": self.location_id
        }