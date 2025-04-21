import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock
from app.db.database import get_db
from app.models.asset import Asset
import logging
import os

LOG_FOLDER = "test/logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(LOG_FOLDER, "test_log.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@pytest.fixture
def mock_db():
    db = MagicMock()
    asset = Asset(symbol="AAPL", latest_price=150.0, change_percent_24h=1.2, average_price_7d=145.0)
    db.query().all.return_value = [asset]
    return db


def test_list_assets(mock_db):
    # Replace the actual dependency with a mock
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)
    response = client.get("/assets")
    logging.info("Testing /assets endpoint")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["symbol"] == "AAPL"
    logging.info("Test /assets passed successfully")
def test_get_metrics_found(mock_db):
    # Replace the actual dependency with a mock
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)
    response = client.get("/metrics/AAPL")
    
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"
    assert response.json()["latest_price"] == 150.0


def test_get_metrics_not_found(mock_db):
    # Replace the actual dependency with a mock
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)
    response = client.get("/metrics/TSLA")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Asset not found"


def test_compare_assets(mock_db):
    # Replace the actual dependency with a mock
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)
    
    # Test comparison with both assets available
    response = client.get("/compare?asset1=AAPL&asset2=AAPL")
    assert response.status_code == 200
    assert "comparison" in response.json()
    assert response.json()["comparison"]["AAPL"]["symbol"] == "AAPL"
    
    # Test comparison when one asset is missing
    response = client.get("/compare?asset1=AAPL&asset2=TSLA")
    assert response.status_code == 404
    assert response.json()["detail"] == "One or both assets not found"

from unittest.mock import patch

def test_trigger_ingestion(mock_db):
    # Replace the actual dependency with a mock
    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)
    
    # Patch the ingestion function
    with patch("app.data.ingestion.ingest_assets") as mock_ingest:
        mock_ingest.return_value = ["AAPL", "GOOGL"]
        response = client.post("/ingest")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Data ingestion successful"
        assert response.json()["assets_updated"] == 2
