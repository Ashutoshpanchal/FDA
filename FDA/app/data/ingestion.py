import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
from app.models.asset import Asset
from sqlalchemy.orm import Session
import requests
import random
import time
async def fetch_asset_data(symbol: str) -> Dict:
    """Fetch asset data from yfinance"""
    try:
        await asyncio.sleep(random.randint(1,3))
        session = requests.Session()

        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        ticker = yf.Ticker(symbol, session=session)
        hist = ticker.history(period="7d", interval="1d")
        time.sleep(3)
        # hist = yf.download(["AAPL"], period="7d", interval="1d")
        print(f"Fetched historical data for {symbol}: {hist}")
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
    print(f"Fetching data for symbols: {symbols}")
    print(f"Tasks: {tasks}")
    results = await asyncio.gather(*tasks)
    print(f"Results from yfinance: {results}")
    valid_results = [r for r in results if r is not None]
    existing_symbols = {asset.symbol for asset in db.query(Asset).all()}
    for symbol in existing_symbols:
        db.query(Asset).filter(Asset.symbol == symbol).delete()
        db.commit()
    for result in valid_results:
        asset = Asset(**result)
        db.add(asset)
    
    db.commit()
    return valid_results 