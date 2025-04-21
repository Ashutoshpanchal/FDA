from typing import List, Dict
from app.core.config import settings

class GenAIService:
    @staticmethod
    async def generate_summary(assets_data: List[Dict]) -> str:
        """Generate a summary of market trends"""
        if not assets_data:
            return "No market data available for summary generation."
            
        # Mock implementation - in a real scenario, this would call an actual GenAI API
        summary_parts = []
        
        for asset in assets_data:
            symbol = asset['symbol']
            change = asset['change_percent_24h']
            trend = "increased" if change > 0 else "decreased"
            
            summary_parts.append(
                f"{symbol} {trend} by {abs(change):.2f}% over the last 24 hours, "
                f"with a weekly average price of ${asset['average_price_7d']:.2f}."
            )
            
        return " ".join(summary_parts) 