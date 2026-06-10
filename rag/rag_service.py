from retrieval.retriever import Retriever
from llm.llm import LLM
from llm.prompt_builder import build_rag_prompt

class RAGService:
    def __init__(self, retriever: Retriever, llm: LLM):
        self.retriever = retriever
        self.llm = llm
    
    def answer_question(self, query: str, top_k: int = 5) -> dict:
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve(query, top_k)
        
        if not retrieved_docs:
            return {
                "query": query,
                "answer": "I couldn't find any relevant information in my database about that.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Step 2: Build prompt with context
        prompt = build_rag_prompt(query, retrieved_docs)
        
        # Step 3: Generate answer from LLM
        answer = self.llm.generate(prompt)
        
        # Step 4: Prepare response with sources
        sources = [
            {
                "content": doc['content'][:200] + "...",
                "category": doc['metadata'].get('category'),
                "relevance": doc['relevance_score']
            }
            for doc in retrieved_docs[:3]
        ]
        
        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "confidence": retrieved_docs[0]['relevance_score'] if retrieved_docs else 0.0
        }