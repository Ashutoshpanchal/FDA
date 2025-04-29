import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch
from app.db.database import get_db
from app.models.asset import Asset
import logging
import os
from datetime import datetime

# Create the log directory if it doesn't exist
LOG_FOLDER = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

# Setup logger manually (don't rely solely on basicConfig)
log_file_path = os.path.join(LOG_FOLDER, "test_log.log")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Main logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Avoid duplicate handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Test log
logger.info("Logging system initialized.")


@pytest.fixture
def mock_db():
    db = MagicMock()
    
    # Create mock assets
    btc_asset = Asset(
        symbol="BTC-USD", 
        latest_price=150.0, 
        change_percent_24h=1.2, 
        average_price_7d=145.0,
        timestamp=datetime.now()
    )
    
    eth_asset = Asset(
        symbol="ETH-USD",
        latest_price=2000.0,
        change_percent_24h=-0.5,
        average_price_7d=2050.0,
        timestamp=datetime.now()
    )
    
    # Create a mock query that returns different results based on the symbol
    def mock_filter(*args, **kwargs):
        mock_query = MagicMock()
        logging.info(f"Mock filter called with args: {args}, kwargs: {kwargs}")
        
        # Store the filter condition for later use
        mock_query._filter_condition = args[0] if args else None
        
        def mock_first():
            # Get the symbol from the URL path parameter
            # This is a workaround since we can't easily extract it from the SQLAlchemy filter
            import inspect
            frame = inspect.currentframe()
            while frame:
                if 'symbol' in frame.f_locals:
                    symbol = frame.f_locals['symbol']
                    logging.info(f"Found symbol from frame: {symbol}")
                    if symbol == "BTC-USD":
                        return btc_asset
                    elif symbol == "ETH-USD":
                        return eth_asset
                frame = frame.f_back
            return None
        
        mock_query.first = mock_first
        return mock_query
    
    # Set up the mock to return our custom filter function
    db.query().filter.side_effect = mock_filter
    
    # For the list_assets endpoint
    db.query().all.return_value = [btc_asset, eth_asset]
    
    # For the ingestion test
    def mock_commit():
        pass
    
    db.commit = mock_commit
    
    return db


def test_list_assets(mock_db):
    logging.info("Starting test: test_list_assets")
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)
    response = client.get("/api/v1/assets")
    print(response.json())
    logging.info("Testing /assets endpoint")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["symbol"] == "BTC-USD"
    assert response.json()[1]["symbol"] == "ETH-USD"
    logging.info("Test /assets passed successfully")


def test_get_metrics_found(mock_db):
    logging.info("Starting test: test_get_metrics_found")
    
    # Create a mock asset
    btc_asset = Asset(
        symbol="BTC-USD", 
        latest_price=150.0, 
        change_percent_24h=1.2, 
        average_price_7d=145.0,
        timestamp=datetime.now()
    )
    
    # Create a mock function to replace the database query
    def mock_query_asset(symbol):
        if symbol == "BTC-USD":
            return btc_asset
        return None
    
    # Patch the get_metrics function to use our mock
    with patch("app.api.endpoints.get_metrics") as mock_get_metrics:
        # Set up the mock to return our asset
        mock_get_metrics.return_value = btc_asset.to_dict()
        
        # Override the dependency
        app.dependency_overrides[get_db] = lambda: mock_db
        
        # Create the test client
        client = TestClient(app)
        
        # Make the request
        response = client.get("/api/v1/metrics/BTC-USD")
        
        # Log the response
        logging.info(f"Response: {response.json()}")
        
        # Assert the response
        assert response.status_code == 200
        assert response.json()["symbol"] == "BTC-USD"
        assert response.json()["latest_price"] == 150.0
        
        logging.info("Test /metrics/BTC-USD passed successfully")


def test_get_metrics_not_found(mock_db):
    logging.info("Starting test: test_get_metrics_not_found")
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)
    response = client.get("/api/v1/metrics/TSLA")
    logging.info(f"Response: {response}")
    logging.info("Testing /metrics/TSLA endpoint")
    assert response.status_code == 404
    assert response.json()["detail"] == "Asset not found"
    logging.info("Test /metrics/TSLA passed successfully")




from unittest.mock import patch

def test_trigger_ingestion(mock_db):
    logging.info("Starting test: test_trigger_ingestion")
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)
    
    # Patch both the ingestion function and the settings
    with patch("app.data.ingestion.ingest_assets") as mock_ingest, \
         patch("app.core.config.settings.DEFAULT_ASSETS", ["GOOGL", "TSLA"]):
        logging.info("Patching ingest_assets function and settings.DEFAULT_ASSETS")
        # Return the same assets that we're using in the settings
        mock_ingest.return_value = ["GOOGL", "TSLA"]
        response = client.post("/api/v1/ingest")
        logging.info(f"Response: {response.json()}")
        logging.info("Testing /ingest endpoint")
        assert response.status_code == 200
        assert response.json()["message"] == "Data ingestion successful"
        assert response.json()["assets_updated"] == 2
        logging.info("Test /ingest passed successfully")
    test_get_metrics_found(mock_db)
    test_get_metrics_not_found(mock_db)



