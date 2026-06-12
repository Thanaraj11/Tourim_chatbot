import aiohttp
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class MapTool:
    """Provides location-based information and distances"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if self.api_key == "your_google_maps_api_key":
            self.api_key = None
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def get_distance(self, origin: str, destination: str) -> Dict:
        """Calculate distance and travel time between two locations"""
        if not self.api_key:
            return {"error": "Maps API key not configured", "available": False}
        
        try:
            url = f"{self.base_url}/distancematrix/json"
            params = {
                "origins": origin,
                "destinations": destination,
                "key": self.api_key,
                "units": "metric"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["status"] == "OK":
                            element = data["rows"][0]["elements"][0]
                            if element["status"] == "OK":
                                return {
                                    "origin": origin,
                                    "destination": destination,
                                    "distance_km": element["distance"]["value"] / 1000,
                                    "distance_text": element["distance"]["text"],
                                    "duration_minutes": element["duration"]["value"] / 60,
                                    "duration_text": element["duration"]["text"],
                                    "available": True
                                }
                    return {"error": "Could not calculate distance", "available": False}
        except Exception as e:
            return {"error": str(e), "available": False}
    
    async def get_nearby_places(self, location: str, place_type: str = "tourist_attraction", radius: int = 5000) -> Dict:
        """Find nearby places of interest"""
        if not self.api_key:
            return {"error": "Maps API key not configured", "available": False}
        
        try:
            # First, geocode the location
            geocode_url = f"{self.base_url}/geocode/json"
            geocode_params = {
                "address": f"{location}, Sri Lanka",
                "key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(geocode_url, params=geocode_params) as resp:
                    geocode_data = await resp.json()
                    if geocode_data["status"] != "OK":
                        return {"error": "Location not found", "available": False}
                    
                    location_data = geocode_data["results"][0]["geometry"]["location"]
                    lat = location_data["lat"]
                    lng = location_data["lng"]
                    
                    # Search for nearby places
                    nearby_url = f"{self.base_url}/place/nearbysearch/json"
                    nearby_params = {
                        "location": f"{lat},{lng}",
                        "radius": radius,
                        "type": place_type,
                        "key": self.api_key
                    }
                    
                    async with session.get(nearby_url, params=nearby_params) as resp2:
                        nearby_data = await resp2.json()
                        if nearby_data["status"] == "OK":
                            places = []
                            for place in nearby_data["results"][:5]:
                                places.append({
                                    "name": place["name"],
                                    "address": place.get("vicinity", "Address not available"),
                                    "rating": place.get("rating", "Not rated"),
                                    "types": place.get("types", [])
                                })
                            return {
                                "location": location,
                                "places": places,
                                "count": len(places),
                                "available": True
                            }
                        return {"error": "No places found", "available": False}
        except Exception as e:
            return {"error": str(e), "available": False}
    
    async def create_travel_route(self, waypoints: List[str]) -> Dict:
        """Create an optimized travel route between multiple points"""
        if len(waypoints) < 2:
            return {"error": "Need at least 2 locations", "available": False}
        
        routes = []
        total_distance = 0
        total_duration = 0
        
        for i in range(len(waypoints) - 1):
            distance_info = await self.get_distance(waypoints[i], waypoints[i + 1])
            if distance_info.get("available"):
                routes.append({
                    "from": waypoints[i],
                    "to": waypoints[i + 1],
                    "distance_km": distance_info["distance_km"],
                    "duration_minutes": distance_info["duration_minutes"],
                    "duration_text": distance_info["duration_text"]
                })
                total_distance += distance_info["distance_km"]
                total_duration += distance_info["duration_minutes"]
        
        return {
            "waypoints": waypoints,
            "routes": routes,
            "total_distance_km": round(total_distance, 1),
            "total_duration_hours": round(total_duration / 60, 1),
            "available": True if routes else False
        }
    
    def get_tool_definition(self) -> Dict:
        return {
            "name": "map_tool",
            "description": "Calculate distances, find nearby attractions, and create travel routes. Use when user asks about distance between places, nearby locations, or travel planning.",
            "parameters": {
                "action": "string (required) - 'distance', 'nearby', or 'route'",
                "origin": "string (for distance/route) - Starting location",
                "destination": "string (for distance) - Ending location",
                "location": "string (for nearby) - Center location",
                "place_type": "string (optional) - Type of place to find"
            }
        }