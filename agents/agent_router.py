from typing import Dict, List, Any
from enum import Enum

class ToolType(Enum):
    RAG = "rag"
    WEATHER = "weather"
    MAP = "map"
    CURRENCY = "currency"
    ITINERARY = "itinerary"

class AgentRouter:
    """
    Decides which tools to use based on user query
    """
    
    def __init__(self):
        self.tool_mapping = {
            # Weather related
            "weather": ToolType.WEATHER,
            "temperature": ToolType.WEATHER,
            "rain": ToolType.WEATHER,
            "forecast": ToolType.WEATHER,
            "climate": ToolType.WEATHER,
            "packing": ToolType.WEATHER,
            
            # Map related
            "distance": ToolType.MAP,
            "far": ToolType.MAP,
            "near": ToolType.MAP,
            "nearby": ToolType.MAP,
            "route": ToolType.MAP,
            "driving": ToolType.MAP,
            "travel time": ToolType.MAP,
            
            # Currency related
            "currency": ToolType.CURRENCY,
            "exchange": ToolType.CURRENCY,
            "convert": ToolType.CURRENCY,
            "price in": ToolType.CURRENCY,
            "budget": ToolType.CURRENCY,
            "cost": ToolType.CURRENCY,
            "how much": ToolType.CURRENCY,
            
            # Itinerary related
            "itinerary": ToolType.ITINERARY,
            "plan": ToolType.ITINERARY,
            "schedule": ToolType.ITINERARY,
            "trip": ToolType.ITINERARY,
            "days": ToolType.ITINERARY,
            "day by day": ToolType.ITINERARY,
            
            # Default falls back to RAG
        }
    
    def route_query(self, query: str, intent: str) -> List[ToolType]:
        """
        Determine which tools to use for this query
        Returns list of tools to execute (can be multiple)
        """
        tools_to_use = []
        query_lower = query.lower()
        
        # Check for weather + tourism combo (common pattern)
        if self._needs_weather(query_lower, intent):
            tools_to_use.append(ToolType.WEATHER)
            tools_to_use.append(ToolType.RAG)
        
        # Check for itinerary planning
        elif self._needs_itinerary(query_lower, intent):
            tools_to_use.append(ToolType.ITINERARY)
            if "weather" in query_lower:
                tools_to_use.append(ToolType.WEATHER)
        
        # Check for distance/route queries
        elif self._needs_maps(query_lower, intent):
            tools_to_use.append(ToolType.MAP)
            tools_to_use.append(ToolType.RAG)  # Also get place info
        
        # Check for currency queries
        elif self._needs_currency(query_lower, intent):
            tools_to_use.append(ToolType.CURRENCY)
        
        # Default to RAG for general tourism questions
        else:
            tools_to_use.append(ToolType.RAG)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tools = []
        for tool in tools_to_use:
            if tool not in seen:
                seen.add(tool)
                unique_tools.append(tool)
        
        return unique_tools
    
    def _needs_weather(self, query: str, intent: str) -> bool:
        weather_keywords = ["weather", "temperature", "rain", "forecast", "climate", "hot", "cold", "humid"]
        return any(keyword in query for keyword in weather_keywords)
    
    def _needs_maps(self, query: str, intent: str) -> bool:
        map_keywords = ["distance", "far", "near", "nearby", "route", "driving", "travel time", "how to get"]
        return any(keyword in query for keyword in map_keywords) or intent == "comparison"
    
    def _needs_currency(self, query: str, intent: str) -> bool:
        currency_keywords = ["currency", "exchange", "convert", "price in", "budget", "cost", "how much", "dollar", "euro", "usd", "lkr"]
        return any(keyword in query for keyword in currency_keywords)
    
    def _needs_itinerary(self, query: str, intent: str) -> bool:
        itinerary_keywords = ["itinerary", "plan", "schedule", "trip for", "days in", "day by day", "itinerary for"]
        return any(keyword in query for keyword in itinerary_keywords) or "days" in query
    
    def get_execution_plan(self, tools: List[ToolType]) -> Dict:
        """
        Create execution plan (parallel vs sequential)
        """
        if len(tools) == 1:
            return {"mode": "single", "tools": tools}
        elif ToolType.WEATHER in tools and ToolType.RAG in tools:
            # Can run in parallel
            return {"mode": "parallel", "tools": tools}
        elif ToolType.MAP in tools and ToolType.RAG in tools:
            # Can run in parallel
            return {"mode": "parallel", "tools": tools}
        else:
            # Sequential for dependent tools
            return {"mode": "sequential", "tools": tools}