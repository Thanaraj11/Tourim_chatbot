import aiohttp
import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class WeatherTool:
    """Provides real-time weather information"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    async def get_current_weather(self, city: str) -> Dict:
        """Get current weather for a city"""
        if not self.api_key:
            return {"error": "Weather API key not configured", "available": False}
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": f"{city},LK",  # LK = Sri Lanka
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "city": city,
                            "temperature": data["main"]["temp"],
                            "feels_like": data["main"]["feels_like"],
                            "humidity": data["main"]["humidity"],
                            "condition": data["weather"][0]["description"],
                            "wind_speed": data["wind"]["speed"],
                            "timestamp": datetime.now().isoformat(),
                            "available": True
                        }
                    else:
                        return {"error": f"City '{city}' not found", "available": False}
        except Exception as e:
            return {"error": str(e), "available": False}
    
    async def get_forecast(self, city: str, days: int = 3) -> Dict:
        """Get weather forecast for a city"""
        if not self.api_key:
            return {"error": "Weather API key not configured", "available": False}
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": f"{city},LK",
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 3-hour intervals, 8 per day
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecasts = []
                        for item in data["list"][:days * 8:8]:  # One per day
                            forecasts.append({
                                "date": item["dt_txt"].split()[0],
                                "temp_high": item["main"]["temp_max"],
                                "temp_low": item["main"]["temp_min"],
                                "condition": item["weather"][0]["description"],
                                "rain_chance": item.get("pop", 0) * 100
                            })
                        return {
                            "city": city,
                            "forecasts": forecasts,
                            "available": True
                        }
                    else:
                        return {"error": f"Forecast for '{city}' not found", "available": False}
        except Exception as e:
            return {"error": str(e), "available": False}
    
    async def get_weather_for_tourism(self, city: str) -> Dict:
        """Get weather specifically formatted for tourism recommendations"""
        current = await self.get_current_weather(city)
        forecast = await self.get_forecast(city, 3)
        
        if not current.get("available", False):
            return {"available": False, "message": "Weather information unavailable"}
        
        # Generate tourism recommendation based on weather
        temp = current.get("temperature", 25)
        condition = current.get("condition", "").lower()
        
        if "rain" in condition or "storm" in condition:
            activity = "Indoor activities like museums, shopping, or cultural shows"
            recommendation = "Carry an umbrella. Consider indoor attractions today."
        elif temp > 32:
            activity = "Early morning or late evening outdoor activities. Beach time with caution."
            recommendation = "Very hot! Stay hydrated, use sunscreen. Visit water falls or pools."
        elif temp < 20:
            activity = "Tea plantations, mountain views, or cozy cafes"
            recommendation = "Cool weather. Perfect for Nuwara Eliya or hill country."
        else:
            activity = "Perfect for outdoor exploration, hiking, sightseeing, and beach activities"
            recommendation = "Excellent weather for tourism!"
        
        return {
            "available": True,
            "city": city,
            "current": current,
            "forecast": forecast,
            "tourism_advice": {
                "best_activities": activity,
                "recommendation": recommendation,
                "packing_tips": self._get_packing_tips(temp, condition)
            }
        }
    
    def _get_packing_tips(self, temp: float, condition: str) -> str:
        if "rain" in condition:
            return "Raincoat, umbrella, waterproof shoes"
        elif temp > 30:
            return "Light cotton clothes, hat, sunscreen, sunglasses"
        elif temp < 22:
            return "Light jacket, sweater, comfortable walking shoes"
        else:
            return "Comfortable casual wear, light layers"
    
    def get_tool_definition(self) -> Dict:
        """Return tool definition for the agent"""
        return {
            "name": "weather_tool",
            "description": "Get current weather and forecast for Sri Lankan cities. Use when user asks about weather, climate, or what to pack.",
            "parameters": {
                "city": "string (required) - City name like 'Kandy', 'Ella', 'Colombo'",
                "type": "string (optional) - 'current', 'forecast', or 'tourism'"
            }
        }