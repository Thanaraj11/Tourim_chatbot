import aiohttp
import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class CurrencyTool:
    """Provides live currency exchange rates"""
    
    def __init__(self):
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        
    async def get_exchange_rate(self, from_currency: str = "USD", to_currency: str = "LKR") -> Dict:
        """Get exchange rate between two currencies"""
        try:
            url = f"{self.base_url}/{from_currency}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rate = data["rates"].get(to_currency)
                        
                        if rate:
                            return {
                                "from": from_currency,
                                "to": to_currency,
                                "rate": rate,
                                "conversion": f"1 {from_currency} = {rate:.2f} {to_currency}",
                                "last_updated": data.get("date", datetime.now().strftime("%Y-%m-%d")),
                                "available": True
                            }
                        else:
                            return {"error": f"Currency {to_currency} not found", "available": False}
                    else:
                        # Fallback to approximate rate if API fails
                        return self._get_fallback_rate(from_currency, to_currency)
        except Exception as e:
            return self._get_fallback_rate(from_currency, to_currency)
    
    def _get_fallback_rate(self, from_currency: str, to_currency: str) -> Dict:
        """Provide fallback approximate rates when API is unavailable"""
        approximate_rates = {
            ("USD", "LKR"): 320,
            ("EUR", "LKR"): 345,
            ("GBP", "LKR"): 400,
            ("AUD", "LKR"): 210,
            ("CAD", "LKR"): 235,
            ("LKR", "USD"): 0.0031,
        }
        
        rate = approximate_rates.get((from_currency, to_currency))
        if not rate:
            rate = approximate_rates.get((to_currency, from_currency))
            if rate:
                rate = 1 / rate
        
        if rate:
            return {
                "from": from_currency,
                "to": to_currency,
                "rate": rate,
                "conversion": f"1 {from_currency} ≈ {rate:.2f} {to_currency}",
                "approx": True,
                "available": True
            }
        
        return {"error": "Exchange rate unavailable", "available": False}
    
    async def convert_price(self, amount: float, from_currency: str, to_currency: str = "LKR") -> Dict:
        """Convert a price from one currency to another"""
        rate_info = await self.get_exchange_rate(from_currency, to_currency)
        
        if rate_info.get("available"):
            converted = amount * rate_info["rate"]
            return {
                "original": {"amount": amount, "currency": from_currency},
                "converted": {"amount": round(converted, 2), "currency": to_currency},
                "rate_used": rate_info["rate"],
                "approx": rate_info.get("approx", False),
                "available": True
            }
        
        return {"error": "Conversion failed", "available": False}
    
    async def get_budget_estimate(self, daily_budget_usd: float, num_days: int) -> Dict:
        """Convert daily budget to LKR and provide spending suggestions"""
        conversion = await self.convert_price(daily_budget_usd, "USD", "LKR")
        
        if conversion.get("available"):
            daily_lkr = conversion["converted"]["amount"]
            total_lkr = daily_lkr * num_days
            
            # Spending suggestions based on budget
            if daily_budget_usd < 50:
                category = "Budget"
                suggestion = "Stay in guesthouses, eat at local restaurants, use public transport"
            elif daily_budget_usd < 100:
                category = "Mid-range"
                suggestion = "Comfortable hotels, mix of local and tourist restaurants, private transport options"
            elif daily_budget_usd < 200:
                category = "Luxury"
                suggestion = "Premium hotels, fine dining, private drivers, and guided tours"
            else:
                category = "Premium"
                suggestion = "Luxury resorts, exclusive experiences, and premium services"
            
            return {
                "daily_budget_usd": daily_budget_usd,
                "daily_budget_lkr": round(daily_lkr),
                "total_budget_lkr": round(total_lkr),
                "num_days": num_days,
                "category": category,
                "suggestion": suggestion,
                "available": True
            }
        
        return {"error": "Budget calculation failed", "available": False}
    
    def get_tool_definition(self) -> Dict:
        return {
            "name": "currency_tool",
            "description": "Convert currencies and calculate travel budgets. Use when user asks about prices in different currencies, exchange rates, or budget planning.",
            "parameters": {
                "action": "string (required) - 'rate', 'convert', or 'budget'",
                "amount": "number (for convert) - Amount to convert",
                "from_currency": "string - Source currency (USD, EUR, GBP, LKR)",
                "to_currency": "string - Target currency",
                "daily_budget_usd": "number (for budget) - Daily budget in USD",
                "num_days": "number (for budget) - Number of travel days"
            }
        }