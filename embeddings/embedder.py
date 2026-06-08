from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # for MiniLM
    
    def embed_text(self, text):
        return self.model.encode(text).tolist()
    
    def embed_documents(self, documents):
        return self.model.encode(documents).tolist()
    
    def embed_query(self, query):
        return self.model.encode([query])[0].tolist()