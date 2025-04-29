import openai
from typing import Dict, Optional, List
from app.core.config import settings
import json
import logging

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_summary(self, assets_data: List[Dict]) -> str:
        """Generate a summary of market trends using OpenAI API"""
        if not assets_data:
            return "No market data available for summary generation."
            
        try:
            # Format the data for the prompt
            formatted_data = json.dumps(assets_data, indent=2)
            
            prompt = f"""Generate a concise and insightful summary of the current market trends based on the following data:
            {formatted_data}
            
            Focus on:
            1. Overall market sentiment
            2. Notable price movements
            3. Potential trends or patterns
            4. Brief comparison between assets
            
            Keep the summary under 200 words and use a professional tone."""
            print(f"Prompt: {prompt}")
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst providing market insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            logging.info("Successfully generated market summary")
            return summary
            
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            return "Error generating market summary. Please try again later." 