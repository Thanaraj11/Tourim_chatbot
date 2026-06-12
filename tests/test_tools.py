import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from tools.weather_tool import WeatherTool
from tools.map_tool import MapTool
from tools.currency_tool import CurrencyTool
from tools.itinerary_tool import ItineraryTool

async def test_tools():
    print("Testing Tools...\n")
    
    # Test Weather Tool
    print("1. Weather Tool:")
    weather = WeatherTool()
    result = await weather.get_weather_for_tourism("Kandy")
    if result.get("available"):
        print(f"   [OK] Weather for Kandy: {result['current']['temperature']}°C")
    else:
        print(f"   [WARN] Weather API: {result.get('error', 'Not available')}")
    
    # Test Map Tool
    print("\n2. Map Tool:")
    maps = MapTool()
    result = await maps.get_distance("Kandy", "Sigiriya")
    if result.get("available"):
        print(f"   [OK] Distance: {result['distance_km']:.1f} km")
    else:
        print(f"   [WARN] Maps API: {result.get('error', 'Not available')}")
    
    # Test Currency Tool
    print("\n3. Currency Tool:")
    currency = CurrencyTool()
    result = await currency.get_exchange_rate("USD", "LKR")
    if result.get("available"):
        print(f"   [OK] {result['conversion']}")
    else:
        print(f"   [WARN] Currency API: {result.get('error', 'Using approximations')}")
    
    # Test Itinerary Tool
    print("\n4. Itinerary Tool:")
    itinerary = ItineraryTool()
    result = await itinerary.create_itinerary("Kandy", 2, ["cultural", "nature"])
    if result.get("available"):
        print(f"   [OK] Created {result['num_days']}-day itinerary for {result['destination']}")
    else:
        print(f"   [WARN] Itinerary: {result.get('error', 'Check database')}")

if __name__ == "__main__":
    asyncio.run(test_tools())