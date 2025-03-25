#!/usr/bin/python3


import requests
from datetime import datetime
from create_db import db, app, Recipe, Ingredients, recipe_ingredient

print("Active database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
#from main import app


# Function to fetch recipes from TheMealDB API
def fetch_recipes():
    # Fetch recipes starting with 'a'
    url = "https://www.themealdb.com/api/json/v1/1/search.php?f=a"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("API Status Code:", response.status_code)
        print("API Response:", data.get('meals', [])[:1])
        return data.get('meals', [])
    except requests.RequestException as e:
        print("Failed to fetch recipes from API:", e)
        return []


# Function to populate the database
def populate_database():
    with app.app_context():
        recipes = fetch_recipes()
        if not recipes:
            print("No recipes found. Exiting...")
            return

        for recipe_data in recipes:
            # Add a recipe
            recipe = Recipe(
                    title=recipe_data['strMeal'],
                    description=recipe_data['strInstructions'],
                    category=recipe_data['strCategory'],
                    created_at=datetime.utcnow()
            )
            db.session.add(recipe)
            db.session.commit()  # Commit to get `recipe.id`
            print(f"Added Recipe: {recipe.title} (ID: {recipe.id})")

            # Add ingredients and associate with the recipe
            for i in range(1, 21):
                ingredient_name = recipe_data.get(f'strIngredient{i}')
                if ingredient_name and ingredient_name.strip():  # Ignore empty ingredients
                    ingredient = Ingredients.query.filter_by(name=ingredient_name).first()
                    if not ingredient:
                        ingredient = Ingredients(name=ingredient_name)
                        db.session.add(ingredient)
                        db.session.commit()  # Commit to get `ingredient.id`
                    print(f"Processing Ingredient: {ingredient.name} (ID: {ingredient.id}) for Recipe: {recipe.title}")

                    # Check for duplicate entries in `recipe_ingredient`
                    existing_entry = db.session.query(recipe_ingredient).filter_by(recipe_id=recipe.id, ingredient_id=ingredient.id).first()
                    if existing_entry:
                        print(f"Skipping duplicate entry: Recipe ID={recipe.id}, Ingredient ID={ingredient.id}")
                        continue

                    stmt = recipe_ingredient.insert().values(
                            recipe_id=recipe.id,
                            ingredient_id=ingredient.id
                    )
                    db.session.execute(stmt)

            db.session.commit()  # Commit all changes

    print("Database populated successfully!")


# Run the script
if __name__ == "__main__":
    populate_database()
