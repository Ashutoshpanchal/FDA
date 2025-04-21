from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    latest_price = Column(Float)
    change_percent_24h = Column(Float)
    average_price_7d = Column(Float)
    timestamp = Column(DateTime, default=datetime.now())
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "latest_price": self.latest_price,
            "change_percent_24h": self.change_percent_24h,
            "average_price_7d": self.average_price_7d,
            "timestamp": self.timestamp.isoformat()
        } 
    
