# Financial Data Aggregator & GenAI Insight Engine

A Python-based financial data aggregator that fetches, processes, and provides insights about various financial assets using FastAPI and yfinance.

## Features

- Real-time financial data aggregation for multiple assets
- Asynchronous data processing
- RESTful API endpoints for data access
- GenAI-powered market summary generation
- SQLite database for data persistence

## Installation

### Local Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Docker Installation

1. Make sure you have Docker and Docker Compose installed
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. To run in detached mode:
   ```bash
   docker-compose up -d
   ```
4. To stop the containers:
   ```bash
   docker-compose down
   ```

## Usage

### Local Usage

1. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

2. Access the API documentation at: http://localhost:4321/api/v1/docs

### Docker Usage

1. After starting the containers, access the API documentation at: http://localhost:4321/api/v1/docs

## API Endpoints
- `GET /api/v1/all_symbols` - List all Symbols
- `POST /api/v1/add_symbol` - Add new Symbol
- `GET /api/v1/assets` - List all tracked assets
- `GET /api/v1/metrics/{symbol}` - Get metrics for a specific asset
- `GET /api/v1/compare?asset1=X&asset2=Y` - Compare two assets
- `GET /api/v1/summary` - Get GenAI-generated market summary
- `POST /api/v1/ingest` - Trigger data ingestion

## Project Structure

```
fin/
├── app/
│   ├── api/         # API endpoints
│   ├── core/        # Core configuration
│   ├── data/        # Data ingestion and processing
│   ├── models/      # Database models
│   ├── services/    # Business logic services
└── financial_data/ financial_data.db        # Database configuration
├── tests/           # Test logs
├── requirements.txt # Project dependencies
├── Dockerfile       # Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── main.py         # Application entry point
└── run_tests.py     # Test case
```

## Testing

Run tests using python run_test.py:

