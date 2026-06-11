from enum import Enum
from llm.llm import LLM
import json

class IntentType(Enum):
    GENERAL_QUERY = "general"  # "Tell me about Sri Lanka"
    PLACE_QUERY = "place"      # "Sigiriya history"
    HOTEL_QUERY = "hotel"      # "Best hotels in Ella"
    RESTAURANT_QUERY = "restaurant"  # "Restaurants in Kandy"
    PACKAGE_QUERY = "package"  # "2 day tour packages"
    GUIDE_QUERY = "guide"      # "English speaking guides"
    PRICE_QUERY = "price"      # "Entry fee for Sigiriya"
    COMPARISON_QUERY = "comparison"  # "Sigiriya vs Polonnaruwa"
    RECOMMENDATION_QUERY = "recommendation"  # "Where should I go?"
    FOLLOWUP_QUERY = "followup"  # "How much is it?" (needs context)

class QueryClassifier:
    def __init__(self, llm: LLM):
        self.llm = llm
    
    def classify(self, query: str, conversation_history: list = None) -> dict:
        """
        Classifies user query into intent and extracts entities
        """
        
        # Simple keyword-based classification (fast path)
        keyword_intent = self._keyword_classify(query.lower())
        
        if keyword_intent and keyword_intent != IntentType.GENERAL_QUERY:
            entities = self._extract_entities_basic(query)
            return {
                "intent": keyword_intent,
                "entities": entities,
                "confidence": 0.8
            }
        
        # LLM-based classification for complex queries
        return self._llm_classify(query, conversation_history)
    
    def _keyword_classify(self, query_lower: str) -> IntentType:
        # Place keywords
        if any(word in query_lower for word in ["sigiriya", "kandy", "ella", "galle", "nuwara", "ancient", "temple", "fortress"]):
            return IntentType.PLACE_QUERY
        
        # Hotel keywords
        if any(word in query_lower for word in ["hotel", "stay", "accommodation", "room", "resort", "guesthouse", "villa"]):
            return IntentType.HOTEL_QUERY
        
        # Restaurant keywords
        if any(word in query_lower for word in ["restaurant", "food", "dinner", "lunch", "cuisine", "meal", "eat", "dining"]):
            return IntentType.RESTAURANT_QUERY
        
        # Package keywords
        if any(word in query_lower for word in ["package", "tour", "itinerary", "day trip", "excursion", "tourist"]):
            return IntentType.PACKAGE_QUERY
        
        # Guide keywords
        if any(word in query_lower for word in ["guide", "tour guide", "local guide"]):
            return IntentType.GUIDE_QUERY
        
        # Price keywords
        if any(word in query_lower for word in ["price", "cost", "fee", "entry", "ticket", "how much"]):
            return IntentType.PRICE_QUERY
        
        # Comparison keywords
        if any(word in query_lower for word in ["vs", "versus", "compare", "difference", "better"]):
            return IntentType.COMPARISON_QUERY
        
        # Recommendation keywords
        if any(word in query_lower for word in ["recommend", "suggest", "best", "top", "should i", "where should"]):
            return IntentType.RECOMMENDATION_QUERY
        
        # Followup detection (short queries)
        if len(query_lower.split()) <= 4:
            return IntentType.FOLLOWUP_QUERY
        
        return IntentType.GENERAL_QUERY
    
    def _extract_entities_basic(self, query: str) -> dict:
        entities = {
            "locations": [],
            "price_range": None,
            "duration": None,
            "people_count": None
        }
        
        # Extract location names (common Sri Lankan places)
        places = ["sigiriya", "kandy", "ella", "galle", "colombo", "nuwara eliya", "polonnaruwa", 
                  "anuradhapura", "mirissa", "bentota", "trincomalee", "jaffna"]
        
        query_lower = query.lower()
        for place in places:
            if place in query_lower:
                entities["locations"].append(place.title())
        
        # Extract price indicators
        if "cheap" in query_lower or "budget" in query_lower:
            entities["price_range"] = "budget"
        elif "luxury" in query_lower or "expensive" in query_lower:
            entities["price_range"] = "luxury"
        elif "mid" in query_lower or "moderate" in query_lower:
            entities["price_range"] = "moderate"
        
        return entities
    
    def _llm_classify(self, query: str, conversation_history: list) -> dict:
        history_text = ""
        if conversation_history:
            last_exchanges = conversation_history[-4:]  # Last 2 exchanges
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in last_exchanges])
        
        prompt = f"""
Classify this tourism query into intent and extract entities.

Conversation History:
{history_text if history_text else "No history"}

Current Query: {query}

Available intents:
- PLACE_QUERY: Asking about tourist attractions, historical sites
- HOTEL_QUERY: Questions about accommodation
- RESTAURANT_QUERY: Questions about dining
- PACKAGE_QUERY: Tour packages and itineraries
- GUIDE_QUERY: Tour guides and their services
- PRICE_QUERY: Cost, fees, pricing information
- COMPARISON_QUERY: Comparing multiple options
- RECOMMENDATION_QUERY: Asking for suggestions
- FOLLOWUP_QUERY: Short followup to previous question
- GENERAL_QUERY: Everything else

Return JSON:
{{
    "intent": "INTENT_NAME",
    "entities": {{
        "locations": [],
        "price_range": null,
        "duration": null,
        "specific_place": null
    }},
    "confidence": 0.95
}}
"""
        try:
            response = self.llm.generate(prompt)
            result = json.loads(response.strip())
            result["intent"] = IntentType(result["intent"].lower())
            return result
        except:
            # Fallback
            return {
                "intent": IntentType.GENERAL_QUERY,
                "entities": {},
                "confidence": 0.5
            }