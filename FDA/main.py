from fastapi import FastAPI, Request
from app.api.endpoints import router
from app.db.database import engine, Base
from app.core.config import settings
from app.models.asset import Asset
import logging
import uvicorn
import os
# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG)



# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Include API router
app.include_router(router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def check_db_exists(request: Request, call_next):
    logging.debug("Checking if database exists...")
    if not os.path.exists(settings.DATABASE_URL):
        # You could raise an HTTPException or log and create the DB
        from sqlalchemy import create_engine
        from app.db.database import Base
        from app.models.asset import Asset

        engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        try:
            Asset.__table__.create(bind=engine)
        except:
            logging.debug("Table already exists, skipping creation.")    
        
        print("Database created!")

    response = await call_next(request)
    return response


if __name__ == "__main__":
    # Enable debugging mode for uvicorn and FastAPI
    logging.debug("Starting the FastAPI application in debug mode.")
    uvicorn.run("main:app", host="0.0.0.0", port=4321,reload=True) 
