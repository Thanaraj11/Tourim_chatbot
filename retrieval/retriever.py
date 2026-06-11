from embeddings.embedder import Embedder
from vector_db.vector_db import VectorDB
from typing import Optional, Dict

class Retriever:
    def __init__(self, vector_db: VectorDB):
        self.vector_db = vector_db
        self.embedder = Embedder()
    
    def retrieve(self, query: str, top_k: int = 5, where_filter: Optional[Dict] = None):
        query_embedding = self.embedder.embed_query(query)
        results = self.vector_db.search(query_embedding, top_k, where_filter)
        
        retrieved_docs = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0
                retrieved_docs.append({
                    "content": doc,
                    "metadata": metadata,
                    "relevance_score": 1 - distance  # convert distance to similarity
                })
        
        return retrieved_docs