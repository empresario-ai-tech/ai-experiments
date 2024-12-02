from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import pickle
from .utils import DATA_PATH
import torch
import os

try:
    import torch_xla.core.xla_model as xm
except ImportError:
    xm = None

class IngredientEmbeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.device = self.get_device()
        self.model = SentenceTransformer(model_name).to(self.device)
        self.standardized_ingredients = self.load_standardized_ingredients()
        self.embeddings = self.generate_embeddings()
        self.index = self.build_faiss_index()

    def get_device(self):
        if xm and 'COLAB_TPU_ADDR' in os.environ:
            return xm.xla_device()
        elif torch.cuda.is_available():
            return 'cuda'
        else:
            return 'cpu'

    def load_standardized_ingredients(self):
        df = pd.read_csv(f"{DATA_PATH}/standardized_ingredients_dummy.csv")
        return df['ingredient_name'].tolist()

    def generate_embeddings(self):
        embeddings = self.model.encode(
            self.standardized_ingredients, 
            convert_to_tensor=True, 
            show_progress_bar=True, 
            device=self.device
        )
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