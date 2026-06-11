import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classifier.query_classifier import QueryClassifier, IntentType
from llm.llm import LLM

def test_classifier():
    llm = LLM()
    classifier = QueryClassifier(llm)
    
    test_queries = [
        "Tell me about Sigiriya",
        "Best hotels in Ella", 
        "How much is the entry fee?",
        "Restaurants in Kandy",
        "Compare Sigiriya and Polonnaruwa"
    ]
    
    for query in test_queries:
        result = classifier.classify(query)
        print(f"Query: {query}")
        print(f"Intent: {result['intent'].value}")
        print(f"Confidence: {result.get('confidence', 0.7)}")
        print("-" * 40)

if __name__ == "__main__":
    test_classifier()