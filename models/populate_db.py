#!/usr/bin/python3

import requests
from models.create_db import db, Recipe, Ingredients
from main import app


# Function to fetch recipes from TheMealDB API
def fetch_recipes():
    # Fetch recipes starting with 'a'
    url = "https://www.themealdb.com/api/json/v1/1/search.php?f=a"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('meals', [])
    else:
        print("Failed to fetch recipes from API.")
        return []


# Function to populate the database
def populate_database():
    with app.app_context():
        recipes = fetch_recipes()
        for recipe_data in recipes:
            # Add a recipe to the database
            recipe = Recipe(
                    title=recipe_data['strMeal'],
                    description=recipe_data['strInstructions'],
                    category=recipe_data['strCategory'],
                    created_at="2025-03-20"  # Use current date in production
                    )
            db.session.add(recipe)
            db.session.commit()

            # Add ingredients for the recipe
            # TheMealDB lists up to 20 ingredient
            for i in range(1, 21):
                ingredient_name = recipe_data.get(f'strIngredient{i}')
                quantity = recipe_data.get(f'strMeasure{i}')
                # Only add non-empty ingredients
                if ingredient_name:
                    # Check if ingredient exists
                    ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_name)
                    db.session.add(ingredient)
                    db.session.commit()

                # Add rekationship in RecipeIngredient table
                recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=quantity
                        )
                db.session.add(recipe_ingredient)
        db.session.commit()

    print("Database populated successfully!")


# Run the script
if __name__ == "__main__":
    populate_database()
