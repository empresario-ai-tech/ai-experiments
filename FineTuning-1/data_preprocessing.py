import json
import pandas as pd

def preprocess_recipes(recipe_file):
    with open(recipe_file, 'r') as file:
        recipes = json.load(file)
    df = pd.DataFrame(recipes)
    # Clean and normalize data
    df['ingredients'] = df['ingredients'].apply(lambda x: [ing.lower() for ing in x])
    return df

def preprocess_schedule(schedule_file):
    schedule = pd.read_csv(schedule_file)
    # Convert times to datetime objects
    schedule['meal_time'] = pd.to_datetime(schedule['meal_time'])
    return schedule 