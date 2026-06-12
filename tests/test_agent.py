import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from agents.tourism_agent import TourismAgent
from retrieval.retriever import Retriever
from llm.llm import LLM
from memory.chat_memory import ChatMemory
from vector_db.vector_db import VectorDB

async def test_agent():
    print("Testing Tourism Agent V3...")
    
    vector_db = VectorDB()
    vector_db.create_collection()
    retriever = Retriever(vector_db)
    llm = LLM()
    memory = ChatMemory("test_session")
    
    agent = TourismAgent(retriever, llm, memory)
    
    test_queries = [
        "What's the weather like in Kandy tomorrow?",
        "Create a 3 day itinerary for Ella",
        "How far is Sigiriya from Kandy?",
        "What's 100 USD in LKR?",
        "Tell me about Sigiriya"  # Should use RAG only
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        result = await agent.process_query(query)
        
        print(f"Intent: {result['intent']}")
        print(f"Tools used: {result['tools_used']}")
        print(f"Answer: {result['answer'][:300]}...")
        print(f"{'-'*40}")

if __name__ == "__main__":
    asyncio.run(test_agent())