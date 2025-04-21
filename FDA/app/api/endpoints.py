from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.asset import Asset
from app.data.ingestion import ingest_assets,fetch_asset_data
from app.services.genai import GenAIService
from app.core.config import settings

router = APIRouter()



@router.get("/all_symbols")
async def get_all_symbols(db: Session = Depends(get_db)):
    """Get all symbols from the database"""
    symbols = settings.DEFAULT_ASSETS
    return {"symbols": symbols }

@router.post("/add_symbol")
async def add_symbol(symbol: str, db: Session = Depends(get_db)):
    """Add a new asset to track"""
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    
    # Check if the symbol already exists in setting
    if symbol in settings.DEFAULT_ASSETS:
        raise HTTPException(status_code=400, detail="Symbol already exists in default assets")
    result =await fetch_asset_data(symbol)
    print(f"Fetched data for {symbol}: {result}")
    if not result:
        raise HTTPException(status_code=400, detail="Invalid symbol or data not available")
    # Add symbol to setting
    try:
        settings.DEFAULT_ASSETS.append(symbol)
        return {"message": f"symbol {symbol} added successfully", "asset":settings.DEFAULT_ASSETS }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/assets")
async def list_assets(db: Session = Depends(get_db)):
    """List all tracked assets"""
    assets = db.query(Asset).all()
    return [asset.to_dict() for asset in assets]

@router.get("/metrics/{symbol}")
async def get_metrics(symbol: str, db: Session = Depends(get_db)):
    """Get metrics for a specific asset"""
    asset = db.query(Asset).filter(Asset.symbol == symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset.to_dict()

@router.get("/compare")
async def compare_assets(asset1: str, asset2: str, db: Session = Depends(get_db)):
    """Compare two assets"""
    asset1_data = db.query(Asset).filter(Asset.symbol == asset1).first()
    asset2_data = db.query(Asset).filter(Asset.symbol == asset2).first()
    
    if not asset1_data or not asset2_data:
        raise HTTPException(status_code=404, detail="One or both assets not found")
        
    return {
        "comparison": {
            asset1: asset1_data.to_dict(),
            asset2: asset2_data.to_dict()
        }
    }

@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """Get GenAI-generated market summary"""
    assets = db.query(Asset).all()
    if not assets:
        raise HTTPException(status_code=404, detail="No market data available")
        
    assets_data = [asset.to_dict() for asset in assets]
    summary = await GenAIService.generate_summary(assets_data)
    
    return {"summary": summary}

@router.post("/ingest")
async def trigger_ingestion(db: Session = Depends(get_db)):
    """Trigger data ingestion"""
    try:
        results = await ingest_assets(db, settings.DEFAULT_ASSETS)
        return {"message": "Data ingestion successful", "assets_updated": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 