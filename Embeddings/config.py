# config.py

# File paths
EMBEDDINGS_PATH = 'Embeddings\data\ingredient_embeddings.pkl'
STANDARDIZED_INGREDIENTS_FILE = 'Embeddings\data\standardized_ingredients_dummy.csv'

# Model and processing settings
MODEL_NAME = 'all-MiniLM-L6-v2'
BATCH_SIZE = 1000
THRESHOLD = 0.7

# Ingredients lists
USER_INGREDIENTS = [
    "all purpose flour",
    "gran sugar",
    "olive oil",
    "black pepper",
    "chicken breasts",
    "eggs",
    "milk",
    "butter"
]

AI_INGREDIENTS = [
    "all-purpose flour",
    "granulated sugar",
    "extra virgin olive oil",
    "black pepper",
    "chicken breast",
    "egg",
    "whole milk",
    "unsalted butter"
] 