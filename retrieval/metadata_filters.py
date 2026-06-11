from classifier.query_classifier import IntentType
from typing import Dict, List, Optional

class MetadataFilter:
    def __init__(self):
        self.intent_to_category = {
            IntentType.PLACE_QUERY: ["places"],
            IntentType.HOTEL_QUERY: ["hotels"],
            IntentType.RESTAURANT_QUERY: ["restaurants"],
            IntentType.PACKAGE_QUERY: ["packages"],
            IntentType.GUIDE_QUERY: ["guides"],
            IntentType.PRICE_QUERY: ["places", "hotels", "packages"],  # price exists in multiple
            IntentType.COMPARISON_QUERY: ["places", "hotels"],  # can compare across types
            IntentType.RECOMMENDATION_QUERY: ["places", "hotels", "restaurants"],
            IntentType.GENERAL_QUERY: ["places", "hotels", "restaurants", "packages", "guides"],
            IntentType.FOLLOWUP_QUERY: None  # Will be determined by context
        }
    
    def build_filter(self, intent: IntentType, entities: Dict, previous_intent: Optional[IntentType] = None) -> Dict:
        """
        Build ChromaDB metadata filter based on intent and entities
        """
        
        # For followup, use previous intent if available
        if intent == IntentType.FOLLOWUP_QUERY and previous_intent:
            intent = previous_intent
        
        categories = self.intent_to_category.get(intent, ["places", "hotels", "restaurants"])
        
        # Build where clause
        where_clause = {}
        
        if len(categories) == 1:
            # Single category filter
            where_clause = {"category": categories[0]}
        elif len(categories) > 1:
            # Multiple categories - use $or
            where_clause = {"$or": [{"category": cat} for cat in categories]}
        
        # Add location filter if entities have locations
        if entities.get("locations") and len(entities["locations"]) > 0:
            location = entities["locations"][0].lower()
            where_clause["name"] = {"$regex": location}
        
        return where_clause if where_clause else None
    
    def get_search_limit(self, intent: IntentType) -> int:
        """Return appropriate number of results based on intent"""
        limits = {
            IntentType.PLACE_QUERY: 3,
            IntentType.HOTEL_QUERY: 5,
            IntentType.RESTAURANT_QUERY: 5,
            IntentType.PACKAGE_QUERY: 3,
            IntentType.GUIDE_QUERY: 3,
            IntentType.PRICE_QUERY: 2,
            IntentType.COMPARISON_QUERY: 6,
            IntentType.RECOMMENDATION_QUERY: 5,
            IntentType.GENERAL_QUERY: 4,
            IntentType.FOLLOWUP_QUERY: 3
        }
        return limits.get(intent, 4)