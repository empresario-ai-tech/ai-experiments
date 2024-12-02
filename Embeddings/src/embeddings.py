from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss
import pickle
# from src.utils import DATA_PATH
import torch
import os
from tqdm import tqdm
import config

try:
    import torch_xla.core.xla_model as xm
except ImportError:
    xm = None

class IngredientEmbeddings:
    def __init__(self, model_name=config.MODEL_NAME, batch_size=config.BATCH_SIZE):
        self.device = self.get_device()
        self.model = SentenceTransformer(model_name).to(self.device)
        self.batch_size = batch_size
        self.standardized_ingredients = None
        self.embeddings = None
        self.index = None

    def get_device(self):
        if xm and 'COLAB_TPU_ADDR' in os.environ:
            return xm.xla_device()
        elif torch.cuda.is_available():
            return 'cuda'
        else:
            return 'cpu'

    def load_standardized_ingredients(self):
        # Load the entire dataset into a DataFrame for access
        return pd.read_csv(config.STANDARDIZED_INGREDIENTS_FILE)

    def generate_embeddings(self):
        all_embeddings = []
        # Use tqdm to add a progress bar to the chunk processing loop
        for chunk in tqdm(pd.read_csv(config.STANDARDIZED_INGREDIENTS_FILE, chunksize=self.batch_size), desc="Generating Embeddings"):
            chunk_embeddings = self.model.encode(
                chunk['ingredient_name'].tolist(),
                convert_to_tensor=True,
                show_progress_bar=False,  # Disable internal progress bar
                device=self.device
            )
            all_embeddings.append(chunk_embeddings.cpu().numpy())
        return np.vstack(all_embeddings)

    def build_faiss_index(self):
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(self.embeddings)
        return index

    def save_embeddings(self, path=config.EMBEDDINGS_PATH):
        # Load the entire dataset for saving
        ingredient_data = self.load_standardized_ingredients()
        
        with open(path, 'wb') as f:
            pickle.dump({
                'ingredients': ingredient_data,  # Store the entire DataFrame
                'embeddings': self.embeddings,
                'index': self.index
            }, f)

    def load_embeddings(self, path=config.EMBEDDINGS_PATH):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.standardized_ingredients = data['ingredients']
            self.embeddings = data['embeddings']
            self.index = data['index']

    def initialize_embeddings(self):
        # Generate embeddings using chunking
        self.embeddings = self.generate_embeddings()
        # Build FAISS index
        self.index = self.build_faiss_index()
        # Load the full dataset for access
        self.standardized_ingredients = self.load_standardized_ingredients()
 