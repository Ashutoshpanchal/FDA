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
    
    OPENAI_API_KEY: str = ""
   
    class Config:
        case_sensitive = True

settings = Settings() 