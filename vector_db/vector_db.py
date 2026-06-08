import chromadb
from chromadb.config import Settings
import os

class VectorDB:
    def __init__(self, persist_dir="./vector_db/chroma_data"):
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = None
    
    def create_collection(self, name="tourism_docs"):
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )
        return self.collection
    
    def add_documents(self, ids, embeddings, documents, metadatas):
        if not self.collection:
            self.create_collection()
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def search(self, query_embedding, top_k=5):
        if not self.collection:
            raise Exception("Collection not initialized")
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        return results
    
    def count(self):
        return self.collection.count() if self.collection else 0