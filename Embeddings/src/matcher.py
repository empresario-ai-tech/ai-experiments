from src.embeddings import IngredientEmbeddings
from sentence_transformers import SentenceTransformer
import numpy as np
import torch
import torch_xla.core.xla_model as xm
import os

class IngredientMatcher:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.device = self.get_device()
        self.embeddings = IngredientEmbeddings()
        try:
            self.embeddings.load_embeddings()
        except FileNotFoundError:
            self.embeddings.generate_embeddings()
            self.embeddings.save_embeddings()
    
    def get_device(self):
        if 'COLAB_TPU_ADDR' in os.environ:
            return xm.xla_device()
        elif torch.cuda.is_available():
            return 'cuda'
        else:
            return 'cpu'

    def get_embedding(self, ingredient):
        model = self.embeddings.model.to(self.device)
        return model.encode(
            [ingredient], 
            convert_to_tensor=True, 
            device=self.device
        ).cpu().numpy()

    def match_ingredient(self, ingredient):
        query_embedding = self.get_embedding(ingredient)
        distances, indices = self.embeddings.index.search(query_embedding, 1)
        closest_distance = distances[0][0]
        closest_index = indices[0][0]
        similarity = 1 / (1 + closest_distance)  # Convert L2 distance to similarity
        if similarity >= self.threshold:
            return self.embeddings.standardized_ingredients[closest_index], similarity
        else:
            return None, similarity

    def match_ingredients_list(self, ingredients):
        matched = {}
        for ingredient in ingredients:
            match, score = self.match_ingredient(ingredient)
            matched[ingredient] = {
                'matched_name': match,
                'similarity': score
            }
        return matched 