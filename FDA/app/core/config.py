from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Financial Data Aggregator"
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///financial_data/financial_data.db"
    
    # Asset Settings
    DEFAULT_ASSETS: List[str] = ["BTC-USD", "ETH-USD", "TSLA"]
    
    # AI Service Settings
    GROQ_API_KEY: str = "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"
    GROQ_MODEL_NAME: str = "llama3-70b-8192"
   
    OPENAI_API_KEY: str = ""
   
    class Config:
        case_sensitive = True

settings = Settings() 