from .vector_db import VectorDB
from embeddings.embedder import Embedder
from documents.document_generator import generate_all_documents
from database.load_data import fetch_all_tourism_data
import uuid

def build_vector_index():
    print("📚 Fetching data from database...")
    data = fetch_all_tourism_data()
    
    print("📄 Generating documents...")
    documents, metadatas = generate_all_documents(data)
    
    print(f"🔢 Generated {len(documents)} documents")
    
    print("🧠 Creating embeddings...")
    embedder = Embedder()
    embeddings = embedder.embed_documents(documents)
    
    print("💾 Storing in ChromaDB...")
    vector_db = VectorDB()
    vector_db.create_collection()
    
    ids = [str(uuid.uuid4()) for _ in range(len(documents))]
    
    vector_db.add_documents(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"✅ Index built successfully! Stored {vector_db.count()} vectors.")
    return vector_db

if __name__ == "__main__":
    build_vector_index()