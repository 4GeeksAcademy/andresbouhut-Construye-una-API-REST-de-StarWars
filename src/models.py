from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    favorite_characters: Mapped[list['FavoriteCharacters']] = relationship('FavoriteCharacters', back_populates='user', cascade='all, delete-orphan')
    favorite_planets: Mapped[list['FavoritePlanets']] = relationship('FavoritePlanets', back_populates='user', cascade='all, delete-orphan')

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name
        }

class Planet(db.Model):
    __tablename__ = 'planet'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(String(100), nullable=True)
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    terrain: Mapped[str] = mapped_column(String(100), nullable=True)

    favorite_by: Mapped[list['FavoritePlanets']] = relationship('FavoritePlanets', back_populates='planet', cascade='all, delete-orphan')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
            "terrain": self.terrain
        }

class Characters(db.Model):
    __tablename__ = 'characters'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    height: Mapped[int] = mapped_column(Integer)
    weight: Mapped[int] = mapped_column(Integer)

    favorite_by: Mapped[list['FavoriteCharacters']] = relationship('FavoriteCharacters', back_populates='character', cascade='all, delete-orphan')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "weight": self.weight
        }

class FavoritePlanets(db.Model):
    __tablename__ = 'favorite_planets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    planet_id: Mapped[int] = mapped_column(ForeignKey('planet.id'))

    user: Mapped['User'] = relationship('User', back_populates='favorite_planets')
    planet: Mapped['Planet'] = relationship('Planet', back_populates='favorite_by')

class FavoriteCharacters(db.Model):
    __tablename__ = 'favorite_characters'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'))

    user: Mapped['User'] = relationship('User', back_populates='favorite_characters')
    character: Mapped['Characters'] = relationship('Characters', back_populates='favorite_by')

from eralchemy2 import render_er
render_er(db.Model, 'diagram.png')
