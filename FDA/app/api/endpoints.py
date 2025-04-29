from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.models.asset import Asset
from app.data.ingestion import ingest_assets, fetch_asset_data
from app.services.openai_service import OpenAIService
from app.core.config import settings

router = APIRouter()
#add pyadentic

# Response Models
class AssetResponse(BaseModel):
    symbol: str
    latest_price: float
    change_percent_24h: float
    average_price_7d: float
    timestamp: datetime

class SymbolsResponse(BaseModel):
    symbols: List[str]

class AddSymbolResponse(BaseModel):
    message: str
    asset: List[str]

class CompareResponse(BaseModel):
    comparison: Dict[str, AssetResponse]

class SummaryResponse(BaseModel):
    summary: str

class IngestResponse(BaseModel):
    message: str
    assets_updated: int

# Helper Functions
def get_asset_by_symbol(db: Session, symbol: str) -> Optional[Asset]:
    """Get asset by symbol from database"""
    return db.query(Asset).filter(Asset.symbol == symbol).first()

def get_all_assets(db: Session) -> List[Asset]:
    """Get all assets from database"""
    return db.query(Asset).all()

@router.get("/all_symbols", response_model=SymbolsResponse, 
    description="Get all available symbols that can be tracked",
    responses={
        200: {"description": "Successfully retrieved all symbols"},
        500: {"description": "Internal server error"}
    })
async def get_all_symbols(db: Session = Depends(get_db)):
    """Get all symbols from the database"""
    symbols = settings.DEFAULT_ASSETS
    return {"symbols": symbols}

@router.post("/add_symbol", response_model=AddSymbolResponse,
    description="Add a new asset symbol to track",
    responses={
        200: {"description": "Symbol successfully added"},
        400: {"description": "Invalid symbol or symbol already exists"},
        500: {"description": "Internal server error"}
    })
async def add_symbol(symbol: str, db: Session = Depends(get_db)):
    """Add a new asset to track"""
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    
    if symbol in settings.DEFAULT_ASSETS:
        raise HTTPException(status_code=400, detail="Symbol already exists in default assets")
    
    result = await fetch_asset_data(symbol)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid symbol or data not available")
    
    try:
        settings.DEFAULT_ASSETS.append(symbol)
        return {"message": f"symbol {symbol} added successfully", "asset": settings.DEFAULT_ASSETS}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assets", response_model=List[AssetResponse],
    description="List all tracked assets with their current metrics",
    responses={
        200: {"description": "Successfully retrieved all assets"},
        500: {"description": "Internal server error"}
    })
async def list_assets(db: Session = Depends(get_db)):
    """List all tracked assets"""
    assets = get_all_assets(db)
    return [asset.to_dict() for asset in assets]

@router.get("/metrics/{symbol}", response_model=AssetResponse,
    description="Get detailed metrics for a specific asset",
    responses={
        200: {"description": "Successfully retrieved asset metrics"},
        404: {"description": "Asset not found"},
        500: {"description": "Internal server error"}
    })
async def get_metrics(symbol: str, db: Session = Depends(get_db)):
    """Get metrics for a specific asset"""
    asset = get_asset_by_symbol(db, symbol)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset.to_dict()

@router.get("/compare", response_model=CompareResponse,
    description="Compare metrics between two assets",
    responses={
        200: {"description": "Successfully compared assets"},
        404: {"description": "One or both assets not found"},
        500: {"description": "Internal server error"}
    })
async def compare_assets(asset1: str, asset2: str, db: Session = Depends(get_db)):
    """Compare two assets"""
    asset1_data = get_asset_by_symbol(db, asset1)
    asset2_data = get_asset_by_symbol(db, asset2)
    
    if not asset1_data or not asset2_data:
        raise HTTPException(status_code=404, detail="One or both assets not found")
        
    return {
        "comparison": {
            asset1: asset1_data.to_dict(),
            asset2: asset2_data.to_dict()
        }
    }

@router.get("/summary", response_model=SummaryResponse,
    description="Get an AI-generated summary of current market trends",
    responses={
        200: {"description": "Successfully generated market summary"},
        404: {"description": "No market data available"},
        500: {"description": "Internal server error"}
    })
async def get_summary(db: Session = Depends(get_db)):
    """Get OpenAI-generated market summary"""
    assets = get_all_assets(db)
    if not assets:
        raise HTTPException(status_code=404, detail="No market data available")
        
    assets_data = [asset.to_dict() for asset in assets]
    
    # Use OpenAIService for summary generation
    openai_service = OpenAIService()
    summary = await openai_service.generate_summary(assets_data)
    
    return {"summary": summary}

@router.post("/ingest", response_model=IngestResponse,
    description="Trigger data ingestion for all tracked assets",
    responses={
        200: {"description": "Data ingestion successful"},
        500: {"description": "Internal server error during ingestion"}
    })
async def trigger_ingestion(db: Session = Depends(get_db)):
    """Trigger data ingestion"""
    try:
        results = await ingest_assets(db, settings.DEFAULT_ASSETS)
        return {"message": "Data ingestion successful", "assets_updated": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 