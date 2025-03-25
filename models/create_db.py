#!/usr/bin/python3

from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../recipecloud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
print("Active database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

recipe_ingredient = db.Table(
        'recipe_ingredient',
        db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True),
        db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
        )

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ratings = db.relationship('Rating', backref='recipe', lazy=True)
    favorites = db.relationship('Favourite', backref='recipe', lazy=True)
    ingredients = db.relationship('Ingredients', secondary=recipe_ingredient, lazy='subquery')

class Ingredients(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

"""recipe_ingredient = db.Table('recipe_ingredient',
        db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True),
        db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
        )"""


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'),
                          nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Favourite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'),
                          nullable=False)
    user_identifier = db.Column(db.String(100), nullable=False)


# Create tables
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        print("Tables created:", inspector.get_table_names())
