import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
from app.models.asset import Asset
from sqlalchemy.orm import Session

async def fetch_asset_data(symbol: str) -> Dict:
    """Fetch asset data from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="7d")
        
        if hist.empty:
            return None
        print(f"Fetched data for {symbol}: {hist}")    
        latest_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        change_percent_24h = ((latest_price - prev_price) / prev_price) * 100
        average_price_7d = hist['Close'].mean()
        
        return {
            "symbol": symbol,
            "latest_price": float(latest_price),
            "change_percent_24h": float(change_percent_24h),
            "average_price_7d": float(average_price_7d)
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

async def ingest_assets(db: Session, symbols: List[str]) -> List[Dict]:
    """Ingest data for multiple assets"""
    tasks = [fetch_asset_data(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)
    print(f"Results from yfinance: {results}")
    valid_results = [r for r in results if r is not None]
    # check if sysmbol already exists in the database
    #drop sysmbols that already exist in the database
    existing_symbols = {asset.symbol for asset in db.query(Asset).all()}
    for symbol in existing_symbols:
        db.query(Asset).filter(Asset.symbol == symbol).delete()
        db.commit()
    for result in valid_results:
        asset = Asset(**result)
        db.add(asset)
    
    db.commit()
    return valid_results 