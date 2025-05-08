from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict
import logging
from app.core.config import settings

class GroqService:
    def __init__(self):
        self.API_KEY = settings.GROQ_API_KEY
        self.MODEL_NAME = settings.GROQ_MODEL_NAME
        self.llm = ChatGroq(model_name=self.MODEL_NAME, api_key=self.API_KEY)

    def generate_response(self, question: str, asset_data: Dict[str, List[Dict]]) -> str:
        """Generate a response using Groq LLM based on all assets data and question"""
        # try:
            # Format the data for the prompt
        formatted_data = []
        for symbol, assets in asset_data.items():
            symbol_data = f"\n{symbol} Data:\n"
            for asset in assets:
                symbol_data += f"Timestamp: {asset['timestamp']}\n"
                symbol_data += f"Latest Price: ${asset['latest_price']:.2f}\n"
                symbol_data += f"24h Change: {asset['change_percent_24h']:.2f}%\n"
                symbol_data += f"7d Average Price: ${asset['average_price_7d']:.2f}\n"
                symbol_data += "-" * 20 + "\n"
            formatted_data.append(symbol_data)
        formatted_data_str = "\n".join(formatted_data)
        system_prompt = """You are a financial analyst assistant. Analyze the following market data and provide insights.
        Focus on:
        1. Overall market trends and patterns
        2. Correlations between different assets
        3. Significant price movements and their potential causes
        4. Market sentiment and potential future movements
        5. Volume and market cap analysis
        
        Keep responses clear, concise, and professional.
        Highlight any interesting patterns or relationships between different assets."""

        user_prompt = f"""Market Data:
        {formatted_data_str}
        
        Question: {question}"""
        logging.debug(f"System Prompt: {system_prompt}")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm(messages)
        logging.info("Successfully generated response using Groq LLM")
        return response.content

        # except Exception as e:
        #     logging.error(f"Error generating response: {str(e)}")
        #     return "Error generating response. Please try again later." 