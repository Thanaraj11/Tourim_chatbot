import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.rag_service import RAGService
from retrieval.retriever import Retriever
from llm.llm import LLM
from vector_db.vector_db import VectorDB

def test_retrieval():
    vector_db = VectorDB()
    vector_db.create_collection()
    retriever = Retriever(vector_db)
    
    # If DB is empty, test will warn
    if vector_db.count() == 0:
        print("⚠️ Vector DB is empty. Run build_index.py first.")
        return
    
    results = retriever.retrieve("Sigiriya", top_k=3)
    print(f"Retrieved {len(results)} documents")
    for r in results:
        print(f"  - {r['metadata'].get('category')}: {r['content'][:100]}...")
        print(f"    Score: {r['relevance_score']:.2f}")

if __name__ == "__main__":
    test_retrieval()