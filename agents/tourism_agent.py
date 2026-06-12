import asyncio
from typing import Dict, List, Any
from datetime import datetime

from memory.chat_memory import ChatMemory
from classifier.query_classifier import QueryClassifier, IntentType
from retrieval.retriever import Retriever
from llm.llm import LLM

from agents.agent_router import AgentRouter, ToolType
from tools.weather_tool import WeatherTool
from tools.map_tool import MapTool
from tools.currency_tool import CurrencyTool
from tools.itinerary_tool import ItineraryTool

from prompts.agent_prompts import (
    AGENT_SYSTEM_PROMPT,
    build_agent_prompt,
    build_combined_results_prompt
)

class TourismAgent:
    """
    AI Agent that decides which tools to use and combines results
    """
    
    def __init__(self, retriever: Retriever, llm: LLM, memory: ChatMemory):
        self.retriever = retriever
        self.llm = llm
        self.memory = memory
        self.classifier = QueryClassifier(llm)
        self.router = AgentRouter()
        
        # Initialize tools
        self.weather_tool = WeatherTool()
        self.map_tool = MapTool()
        self.currency_tool = CurrencyTool()
        self.itinerary_tool = ItineraryTool()
        
        self.previous_intent = None
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main agent processing loop
        """
        # 1. Classify query
        conversation_history = self.memory.get_recent_messages(6)
        classification = self.classifier.classify(query, conversation_history)
        intent = classification["intent"]
        entities = classification.get("entities", {})
        
        # 2. Route to appropriate tools
        tools_to_use = self.router.route_query(query, intent.value)
        execution_plan = self.router.get_execution_plan(tools_to_use)
        
        # 3. Execute tools based on plan
        tool_results = await self._execute_tools(tools_to_use, query, entities, execution_plan)
        
        # 4. Get RAG context if needed
        rag_context = None
        if ToolType.RAG in tools_to_use or len(tools_to_use) == 0:
            rag_context = await self._get_rag_context(query, intent, entities)
        
        # 5. Build final prompt with all results
        prompt = build_agent_prompt(
            query=query,
            intent=intent.value,
            tool_results=tool_results,
            rag_context=rag_context,
            memory_summary=self.memory.get_conversation_summary()
        )
        
        # 6. Generate final answer
        answer = self.llm.generate(prompt)
        
        # 7. Update memory
        self.memory.add_message("user", query, {
            "intent": intent.value,
            "tools_used": [t.value for t in tools_to_use]
        })
        self.memory.add_message("assistant", answer, {
            "intent": intent.value,
            "tools_used": [t.value for t in tools_to_use]
        })
        
        # 8. Prepare response
        return {
            "query": query,
            "answer": answer,
            "intent": intent.value,
            "tools_used": [t.value for t in tools_to_use],
            "tool_results": tool_results,
            "entities": entities,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_tools(self, tools: List[ToolType], query: str, entities: Dict, plan: Dict) -> Dict:
        """
        Execute selected tools
        """
        results = {}
        
        if plan["mode"] == "parallel":
            # Execute tools in parallel
            tasks = []
            for tool in tools:
                if tool == ToolType.WEATHER:
                    tasks.append(self._execute_weather(query, entities))
                elif tool == ToolType.MAP:
                    tasks.append(self._execute_map(query, entities))
                elif tool == ToolType.CURRENCY:
                    tasks.append(self._execute_currency(query, entities))
                elif tool == ToolType.ITINERARY:
                    tasks.append(self._execute_itinerary(query, entities))
                elif tool == ToolType.RAG:
                    tasks.append(self._get_rag_context(query, None, entities))
            
            task_results = await asyncio.gather(*tasks)
            
            for i, tool in enumerate(tools):
                results[tool.value] = task_results[i]
        
        else:
            # Sequential execution
            for tool in tools:
                if tool == ToolType.WEATHER:
                    results[tool.value] = await self._execute_weather(query, entities)
                elif tool == ToolType.MAP:
                    results[tool.value] = await self._execute_map(query, entities)
                elif tool == ToolType.CURRENCY:
                    results[tool.value] = await self._execute_currency(query, entities)
                elif tool == ToolType.ITINERARY:
                    results[tool.value] = await self._execute_itinerary(query, entities)
        
        return results
    
    async def _execute_weather(self, query: str, entities: Dict) -> Dict:
        """Extract location from query and get weather"""
        location = self._extract_location(query, entities)
        if location:
            result = await self.weather_tool.get_weather_for_tourism(location)
            return result
        return {"error": "Could not determine location", "available": False}
    
    async def _execute_map(self, query: str, entities: Dict) -> Dict:
        """Handle map-related queries"""
        query_lower = query.lower()
        
        if "distance" in query_lower or "far" in query_lower:
            # Try to extract two locations
            locations = self._extract_two_locations(query, entities)
            if len(locations) >= 2:
                return await self.map_tool.get_distance(locations[0], locations[1])
        
        elif "nearby" in query_lower or "near" in query_lower:
            location = self._extract_location(query, entities)
            if location:
                return await self.map_tool.get_nearby_places(location)
        
        return {"error": "Could not process map request", "available": False}
    
    async def _execute_currency(self, query: str, entities: Dict) -> Dict:
        """Handle currency conversion"""
        query_lower = query.lower()
        
        if "budget" in query_lower:
            # Parse budget and days
            import re
            budget_match = re.search(r'(\d+)\s*(usd|\$)', query_lower)
            days_match = re.search(r'(\d+)\s*days?', query_lower)
            
            if budget_match and days_match:
                budget = float(budget_match.group(1))
                days = int(days_match.group(1))
                return await self.currency_tool.get_budget_estimate(budget, days)
        
        # Default to USD to LKR conversion
        return await self.currency_tool.get_exchange_rate("USD", "LKR")
    
    async def _execute_itinerary(self, query: str, entities: Dict) -> Dict:
        """Create itinerary from query"""
        import re
        
        # Extract destination
        destination = self._extract_location(query, entities)
        if not destination:
            destination = "Sri Lanka"
        
        # Extract number of days
        days_match = re.search(r'(\d+)\s*days?', query.lower())
        num_days = int(days_match.group(1)) if days_match else 3
        
        # Extract preferences
        preferences = []
        if "adventure" in query.lower():
            preferences.append("adventure")
        if "cultural" in query.lower():
            preferences.append("cultural")
        if "relax" in query.lower() or "beach" in query.lower():
            preferences.append("relaxation")
        if "food" in query.lower():
            preferences.append("food")
        if "nature" in query.lower():
            preferences.append("nature")
        
        if not preferences:
            preferences = ["cultural", "nature"]
        
        # Determine budget
        budget = "moderate"
        if "budget" in query.lower() or "cheap" in query.lower():
            budget = "budget"
        elif "luxury" in query.lower():
            budget = "luxury"
        
        return await self.itinerary_tool.create_itinerary(
            destination=destination,
            num_days=num_days,
            preferences=preferences,
            budget=budget
        )
    
    async def _get_rag_context(self, query: str, intent: IntentType, entities: Dict) -> Dict:
        """Get relevant documents from vector database"""
        top_k = 5
        where_filter = None
        
        # Apply category filter based on intent if needed
        if intent and intent != IntentType.GENERAL_QUERY:
            category_map = {
                IntentType.PLACE_QUERY: ["places"],
                IntentType.HOTEL_QUERY: ["hotels"],
                IntentType.RESTAURANT_QUERY: ["restaurants"],
                IntentType.PACKAGE_QUERY: ["packages"],
                IntentType.GUIDE_QUERY: ["guides"]
            }
            categories = category_map.get(intent, None)
            if categories:
                where_filter = {"category": categories[0]} if len(categories) == 1 else {"$or": [{"category": c} for c in categories]}
        
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k, where_filter=where_filter)
        
        return {
            "documents": retrieved_docs[:3],
            "count": len(retrieved_docs),
            "available": len(retrieved_docs) > 0
        }
    
    def _extract_location(self, query: str, entities: Dict) -> str:
        """Extract location name from query or entities"""
        # First check entities
        if entities.get("locations") and len(entities["locations"]) > 0:
            return entities["locations"][0]
        
        # Common Sri Lankan locations
        locations = ["kandy", "ella", "colombo", "galle", "sigiriya", "nuwara eliya", 
                     "mirissa", "bentota", "trincomalee", "jaffna", "anuradhapura", 
                     "polonnaruwa", "arugam bay", "hatton", "adam's peak"]
        
        query_lower = query.lower()
        for loc in locations:
            if loc in query_lower:
                return loc.title()
        
        return None
    
    def _extract_two_locations(self, query: str, entities: Dict) -> List[str]:
        """Extract two locations for distance calculation"""
        locations = []
        location_list = ["kandy", "ella", "colombo", "galle", "sigiriya", "nuwara eliya", 
                         "mirissa", "bentota", "trincomalee", "jaffna"]
        
        query_lower = query.lower()
        for loc in location_list:
            if loc in query_lower:
                locations.append(loc.title())
        
        return locations[:2]
    
    def get_available_tools(self) -> List[Dict]:
        """Return list of available tools with descriptions"""
        return [
            self.weather_tool.get_tool_definition(),
            self.map_tool.get_tool_definition(),
            self.currency_tool.get_tool_definition(),
            self.itinerary_tool.get_tool_definition(),
            {
                "name": "rag_retriever",
                "description": "Search tourism database for places, hotels, restaurants, and packages"
            }
        ]