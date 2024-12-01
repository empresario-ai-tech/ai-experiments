from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import pickle
from .utils import DATA_PATH

class IngredientEmbeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.standardized_ingredients = self.load_standardized_ingredients()
        self.embeddings = self.generate_embeddings()
        self.index = self.build_faiss_index()

    def load_standardized_ingredients(self):
        df = pd.read_csv(f"{DATA_PATH}/standardized_ingredients.csv")
        return df['ingredient_name'].tolist()

    def generate_embeddings(self):
        embeddings = self.model.encode(self.standardized_ingredients, convert_to_tensor=True, show_progress_bar=True)
        return embeddings.cpu().numpy()

    def build_faiss_index(self):
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(self.embeddings)
        return index

    def save_embeddings(self, path='data/ingredient_embeddings.pkl'):
        with open(path, 'wb') as f:
            pickle.dump({
                'ingredients': self.standardized_ingredients,
                'embeddings': self.embeddings,
                'index': self.index
            }, f)

    def load_embeddings(self, path='data/ingredient_embeddings.pkl'):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.standardized_ingredients = data['ingredients']
            self.embeddings = data['embeddings']
            self.index = data['index'] 