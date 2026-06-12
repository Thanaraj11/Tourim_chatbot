from typing import Dict, List, Optional
from database.load_data import fetch_all_tourism_data
from retrieval.retriever import Retriever
from vector_db.vector_db import VectorDB

class ItineraryTool:
    """Creates personalized travel itineraries using tourism database"""
    
    def __init__(self):
        self.vector_db = VectorDB()
        self.vector_db.create_collection()
        self.retriever = Retriever(self.vector_db)
        
    async def create_itinerary(self, 
                               destination: str, 
                               num_days: int, 
                               preferences: List[str] = None,
                               budget: str = "moderate") -> Dict:
        """
        Create a day-by-day travel itinerary
        
        preferences: ['adventure', 'cultural', 'relaxation', 'food', 'nature']
        budget: 'budget', 'moderate', 'luxury'
        """
        
        preferences = preferences or ["cultural", "nature"]
        
        # Retrieve relevant places
        places_query = f"Popular tourist attractions in {destination}"
        retrieved_places = self.retriever.retrieve(places_query, top_k=8)
        
        # Retrieve hotels
        hotels_query = f"{budget} hotels in {destination}"
        retrieved_hotels = self.retriever.retrieve(hotels_query, top_k=3)
        
        # Retrieve restaurants
        restaurants_query = f"Best restaurants in {destination}"
        retrieved_restaurants = self.retriever.retrieve(restaurants_query, top_k=5)
        
        # Parse retrieved data
        places = self._parse_places(retrieved_places)
        hotels = self._parse_hotels(retrieved_hotels)
        restaurants = self._parse_restaurants(retrieved_restaurants)
        
        # Generate itinerary days
        daily_itinerary = self._generate_daily_schedule(
            destination, num_days, places, restaurants, preferences
        )
        
        return {
            "destination": destination,
            "num_days": num_days,
            "preferences": preferences,
            "budget_level": budget,
            "recommended_hotel": hotels[0] if hotels else None,
            "daily_itinerary": daily_itinerary,
            "estimated_cost_per_person": self._estimate_cost(num_days, budget),
            "tips": self._get_travel_tips(destination),
            "available": True
        }
    
    def _parse_places(self, retrieved_docs: List) -> List:
        places = []
        for doc in retrieved_docs:
            content = doc['content']
            # Extract place name and description
            name = self._extract_field(content, "Place Name", "Name")
            description = self._extract_field(content, "Description", "No description")
            
            if name:
                places.append({
                    "name": name,
                    "description": description[:150] + "..." if len(description) > 150 else description,
                    "category": doc['metadata'].get('category', 'place')
                })
        return places
    
    def _parse_hotels(self, retrieved_docs: List) -> List:
        hotels = []
        for doc in retrieved_docs[:2]:
            content = doc['content']
            name = self._extract_field(content, "Hotel Name", "Name")
            price = self._extract_field(content, "Price per Night", "Contact for pricing")
            
            if name:
                hotels.append({
                    "name": name,
                    "price_per_night": price,
                    "rating": self._extract_field(content, "Rating", "Not rated")
                })
        return hotels
    
    def _parse_restaurants(self, retrieved_docs: List) -> List:
        restaurants = []
        for doc in retrieved_docs[:3]:
            content = doc['content']
            name = self._extract_field(content, "Restaurant Name", "Name")
            cuisine = self._extract_field(content, "Cuisine", "Local")
            
            if name:
                restaurants.append({
                    "name": name,
                    "cuisine": cuisine,
                    "price_range": self._extract_field(content, "Price Range", "Moderate")
                })
        return restaurants
    
    def _extract_field(self, content: str, *field_names) -> str:
        for field_name in field_names:
            for line in content.split('\n'):
                if field_name + ":" in line or field_name + ":" in line:
                    return line.split(':', 1)[1].strip()
        return ""
    
    def _generate_daily_schedule(self, destination: str, num_days: int, places: List, restaurants: List, preferences: List) -> List:
        schedule = []
        
        # Activity distribution based on preferences
        activities = {
            "adventure": ["hiking", "trekking", "water sports", "wildlife safari"],
            "cultural": ["temple visits", "historical sites", "museums", "cultural shows"],
            "relaxation": ["beach time", "spa", "scenic views", "leisure walks"],
            "food": ["cooking class", "food tour", "local market", "signature restaurants"],
            "nature": ["waterfalls", "botanical gardens", "nature trails", "tea plantations"]
        }
        
        selected_activities = []
        for pref in preferences:
            selected_activities.extend(activities.get(pref, activities["cultural"]))
        
        for day in range(1, num_days + 1):
            day_schedule = {
                "day": day,
                "morning": self._get_activity_slot(selected_activities, day, "morning", places),
                "afternoon": self._get_activity_slot(selected_activities, day, "afternoon", places),
                "evening": self._get_activity_slot(selected_activities, day, "evening", places),
                "lunch_recommendation": restaurants[day % len(restaurants)] if restaurants else None,
                "dinner_recommendation": restaurants[(day + 1) % len(restaurants)] if restaurants else None
            }
            schedule.append(day_schedule)
        
        return schedule
    
    def _get_activity_slot(self, activities: List, day: int, slot: str, places: List) -> str:
        # Rotate through activities and places
        activity_index = (day * len(slot) + hash(slot)) % len(activities) if activities else 0
        place_index = day % len(places) if places else 0
        
        activity = activities[activity_index] if activities else "sightseeing"
        place = places[place_index]["name"] if places else destination
        
        return f"{activity.title()} at {place}"
    
    def _estimate_cost(self, num_days: int, budget: str) -> Dict:
        daily_rates = {
            "budget": 5000,
            "moderate": 15000,
            "luxury": 35000
        }
        
        daily = daily_rates.get(budget, 15000)
        total = daily * num_days
        
        return {
            "daily_lkr": daily,
            "total_lkr": total,
            "total_usd_approx": round(total / 320, 0),
            "breakdown": {
                "accommodation": int(daily * 0.5),
                "food": int(daily * 0.25),
                "activities": int(daily * 0.15),
                "transport": int(daily * 0.1)
            }
        }
    
    def _get_travel_tips(self, destination: str) -> List:
        tips = [
            "Book accommodations in advance during peak season (December-March)",
            "Respect local customs when visiting temples (cover shoulders and knees)",
            "Stay hydrated and use sunscreen, especially during outdoor activities",
            "Learn a few Sinhala phrases - locals appreciate the effort",
            "Use licensed guides for historical sites for better understanding"
        ]
        
        if destination.lower() in ["ella", "nuwara eliya", "hatton"]:
            tips.append("Pack warm clothes - hill country can be cool in evenings")
        
        if destination.lower() in ["arugam bay", "mirissa", "bentota"]:
            tips.append("Best time for surfing/beach activities is May-September")
        
        return tips
    
    def get_tool_definition(self) -> Dict:
        return {
            "name": "itinerary_tool",
            "description": "Create personalized travel itineraries with day-by-day schedules. Use when user asks for trip planning, itinerary, or tour schedule.",
            "parameters": {
                "destination": "string (required) - Main destination in Sri Lanka",
                "num_days": "number (required) - Number of days for the trip",
                "preferences": "array (optional) - Activities: adventure, cultural, relaxation, food, nature",
                "budget": "string (optional) - 'budget', 'moderate', or 'luxury'"
            }
        }