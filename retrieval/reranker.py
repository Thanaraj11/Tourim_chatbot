import numpy as np
from typing import List, Dict

class Reranker:
    """Re-rank retrieved documents for better relevance"""
    
    def __init__(self):
        pass
    
    def rerank(self, documents: List[Dict], query: str, intent: str) -> List[Dict]:
        """
        Re-rank documents based on multiple factors
        """
        if not documents:
            return documents
        
        # Score each document
        for doc in documents:
            score = doc.get('relevance_score', 0.5)
            
            # Boost based on metadata
            metadata = doc.get('metadata', {})
            category = metadata.get('category', '')
            
            # Boost if category matches intent
            if self._category_matches_intent(category, intent):
                score += 0.15
            
            # Boost if document contains exact location match
            if self._contains_location_match(doc, query):
                score += 0.1
            
            # Freshness boost (if date available)
            if metadata.get('date'):
                score += 0.05
            
            # Length normalization (prefer concise answers for certain intents)
            content_length = len(doc.get('content', ''))
            if intent == 'price' and content_length < 500:
                score += 0.1
            elif intent == 'general' and 200 < content_length < 800:
                score += 0.05
            
            doc['reranked_score'] = min(score, 1.0)
        
        # Sort by new score
        documents.sort(key=lambda x: x.get('reranked_score', 0), reverse=True)
        
        return documents
    
    def _category_matches_intent(self, category: str, intent: str) -> bool:
        matches = {
            'place': ['place', 'general'],
            'hotel': ['hotel', 'accommodation'],
            'restaurant': ['restaurant', 'food'],
            'package': ['package', 'tour'],
            'guide': ['guide']
        }
        
        for key, intents in matches.items():
            if key in category and intent in intents:
                return True
        return False
    
    def _contains_location_match(self, doc: Dict, query: str) -> bool:
        """Check if document contains location mentioned in query"""
        query_lower = query.lower()
        content_lower = doc.get('content', '').lower()
        metadata = doc.get('metadata', {})
        
        # Check in content
        for word in query_lower.split():
            if len(word) > 3 and word in content_lower:
                return True
        
        # Check in metadata name
        if metadata.get('name', '').lower() in query_lower:
            return True
        
        return False