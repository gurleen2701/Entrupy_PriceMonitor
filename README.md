# Entrupy - Product Price Monitoring System

A full-stack product price monitoring system for luxury goods across 3 marketplaces (1stDibs, Fashionphile, Grailed), featuring:

- **SQLite Database** with price history tracking and event logging
- **Async REST API** (FastAPI) with API key authentication
- **Event-log based notifications** with optional webhook delivery
- **React Dashboard** for product browsing and analytics
- **Comprehensive Test Suite** with 12+ test cases

## Setup Instructions

### Prerequisites
- Python 3.9+
- pip or conda
- Node.js 16+ (for frontend)

### Backend Setup

#### 1. Create Virtual Environment
Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows (cmd.exe):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### 2. Install Dependencies
Linux/macOS:
```bash
pip install -r requirements.txt
```

Windows:
```powershell
pip install -r requirements.txt
```

#### 3. Initialize Database
```bash
python init_db.py
```

This creates all tables and seeds the 3 marketplace sources (1stdibs, fashionphile, grailed).

#### 4. Create Test API Key
```bash
python -c "
from app.api.auth import hash_api_key
from app.models.schemas import ApiKey
from app.models.database import SessionLocal
import asyncio

async def create_key():
    async with SessionLocal() as db:
        test_key = 'test_key_12345'
        api_key = ApiKey(
            key=test_key,
            key_hash=hash_api_key(test_key),
            consumer_name='test_consumer',
            is_active=True
        )
        db.add(api_key)
        await db.commit()
        print(f'Created API key: {test_key}')

asyncio.run(create_key())
"
```

#### 5. Run Server
Linux/macOS:
```bash
uvicorn app.main:app --reload --port 8000
```

Windows:
```powershell
uvicorn app.main:app --reload --port 8000
```

Server runs at `http://localhost:8000`

---

## Webhook Receiver Test (local)
You can validate webhook delivery by running a lightweight HTTP receiver locally and then creating a subscription.

### Option A: Python Flask receiver (recommended)
1. Create `webhook_receiver.py`:
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    print('Webhook received', request.json)
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(port=9000)
```
2. Run:
```bash
pip install flask
python webhook_receiver.py
```
3. Register webhook:
```bash
curl -X POST "http://localhost:8000/api/webhooks" \
  -H "X-API-Key: test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://host.docker.internal:9000/webhook","secret":"test_secret","consumer_name":"local_test"}'
```
4. Trigger refresh to send webhook events:
```bash
curl -X POST "http://localhost:8000/api/refresh" -H "X-API-Key: test_key_12345"
```

### Option B: ngrok for public webhook URL
1. Start ngrok:
```bash
ngrok http 9000
```
2. Use ngrok URL in webhook subscription payload:
```bash
curl -X POST "http://localhost:8000/api/webhooks" \
  -H "X-API-Key: test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://<ngrok-id>.ngrok.io/webhook","secret":"test_secret","consumer_name":"remote_test"}'
```
3. Monitor delivery in Flask output and ngrok inspector at `http://127.0.0.1:4040`.

---

### Frontend Setup

#### 1. Navigate to Frontend
```bash
cd frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Run Development Server
```bash
npm run dev
```

Frontend runs at `http://localhost:3000` (or next available port)

### Run Tests
```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## API Documentation

### Authentication
All endpoints (except `/health` and `/`) require `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/products
```

### Endpoints

#### Products

**GET /api/products** - List products with filters and pagination
```bash

curl -H "X-API-Key: test_key_12345" \
  "http://localhost:8000/api/products?source=1stdibs&min_price=1000&max_price=5000&page=1&page_size=20"
```

Query Parameters:
- `source` (string) - Filter by marketplace: 1stdibs, fashionphile, grailed
- `brand` (string) - Filter by brand (partial match)
- `category` (string) - Filter by category (partial match)
- `min_price` (float) - Minimum price
- `max_price` (float) - Maximum price
- `page` (int, default=1) - Page number
- `page_size` (int, default=20, max=100) - Items per page

Response:
```json
{
  "page": 1,
  "page_size": 20,
  "total": 150,
  "items": [
    {
      "id": 1,
      "source": "1stdibs",
      "brand": "Hermès",
      "model": "Birkin Bag 35cm",
      "category": "Handbags",
      "current_price": 8500,
      "currency": "USD",
      "condition": "Excellent",
      "image_url": "https://example.com/image.jpg",
      "product_url": "https://www.1stdibs.com/furniture/item/001",
      "metadata": {},
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00",
      "price_history": [
        {
          "id": 1,
          "product_id": 1,
          "old_price": 8200,
          "new_price": 8500,
          "recorded_at": "2024-01-01T12:00:00",
          "source": "1stdibs"
        }
      ]
    }
  ]
}
```

**GET /api/products/{id}** - Get product detail with full price history
```bash
curl -H "X-API-Key: test_key_12345" http://localhost:8000/api/products/1
```

**POST /api/refresh** - Trigger data ingestion
```bash
curl -X POST -H "X-API-Key: test_key_12345" http://localhost:8000/api/refresh
```

Response:
```json
{
  "products_upserted": 6,
  "price_changes_detected": 2,
  "events_created": 2
}
```

#### Analytics

**GET /api/analytics** - Get aggregate statistics
```bash
curl -H "X-API-Key: test_key_12345" http://localhost:8000/api/analytics
```

Response:
```json
{
  "total_products": 150,
  "products_by_source": {
    "1stdibs": 50,
    "fashionphile": 60,
    "grailed": 40
  },
  "average_price_by_category": {
    "Handbags": 3500.50,
    "Shoulder Bags": 1200.00,
    "Tote Bags": 1400.00
  },
  "total_price_changes": 45,
  "price_stats": {
    "min": 50,
    "max": 15000,
    "avg": 2250.75
  }
}
```

#### Events & Webhooks

**GET /api/events** - List events (price changes, product creation)
```bash
curl -H "X-API-Key: test_key_12345" \
  "http://localhost:8000/api/events?product_id=1&delivered=false&page=1&page_size=20"
```

Query Parameters:
- `product_id` (int) - Filter by product ID
- `delivered` (bool) - Filter by delivery status
- `start_date` (datetime) - Filter by start date
- `end_date` (datetime) - Filter by end date
- `page` (int, default=1)
- `page_size` (int, default=20, max=100)

**POST /api/webhooks** - Register webhook

Linux/macOS and Windows (using curl.exe):
```bash
curl.exe -X POST "http://localhost:8000/api/webhooks" \
  -H "X-API-Key: test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://localhost:9000/webhook","secret":"test_secret","consumer_name":"local_test"}'
```

Windows PowerShell alternate (escape JSON):
```powershell
curl.exe -X POST "http://localhost:8000/api/webhooks" -H "X-API-Key: test_key_12345" -H "Content-Type: application/json" -d '{"url":"http://localhost:9000/webhook","secret":"test_secret","consumer_name":"local_test"}'
```

Response:
```json
{
  "id": 1,
  "url": "http://localhost:9000/webhook",
  "consumer_name": "local_test",
  "is_active": true,
  "created_at": "2026-04-02T08:52:13.114890"
}
```

**DELETE /api/webhooks/{id}** - Remove webhook
```bash
curl.exe -X DELETE "http://localhost:8000/api/webhooks/1" -H "X-API-Key: test_key_12345"
```
  -d '{
    "url": "https://myserver.com/webhook",
    "secret": "my_webhook_secret",
    "consumer_name": "my_app"
  }' \
  http://localhost:8000/api/webhooks
```

**GET /api/webhooks** - List active webhooks
```bash
curl -H "X-API-Key: test_key_12345" http://localhost:8000/api/webhooks
```

**DELETE /api/webhooks/{id}** - Unregister webhook
```bash
curl -X DELETE -H "X-API-Key: test_key_12345" http://localhost:8000/api/webhooks/1
```

#### Health & Info

**GET /health** - Health check
```bash
curl http://localhost:8000/health
```

**GET /** - API info
```bash
curl http://localhost:8000/
```

---

## Design Decisions

### 1. Price History Scaling Strategy

**Approach:** Append-only price_history table with composite index on (product_id, recorded_at)

**Rationale:**
- **Immutability:** Price history is never updated, only appended → no lock contention
- **Indexing:** Composite index enables fast queries like "get last 30 days of prices for product X"
- **Partitioning Ready:** Table structure supports time-based partitioning (e.g., by month) for large datasets
- **Archival Strategy:** Old price history (>1 year) can be archived to cold storage or summarized by week

**For 100+ sources:**
- Add index on (source, recorded_at) for cross-source analytics
- Use time-range scans: `recorded_at >= NOW() - interval '7 days'` to cap query result size
- Implement background job to summarize older history (weekly/monthly aggregates)

### 2. Notification System: Event Log + Webhooks

**Architecture:**
- **Primary:** Immutable event_log table (never lose an event)
- **Secondary:** Optional webhook subscriptions for push notifications
- **Backup:** Consumers can query event log via GET /api/events if webhook delivery fails

**Why not alternatives?**
- ❌ **Pure polling:** Wastes bandwidth, high latency for real-time use cases
- ❌ **Pure webhooks:** No durability if webhook service is down; consumer can't replay
- ✅ **Event log + webhooks:** Best of both worlds — reliable storage + real-time push

**Webhook Delivery:**
- Async background task (non-blocking)
- HMAC-SHA256 signature for verification
- Retry up to 3 times with exponential backoff (2s, 4s, 8s)
- Track delivery_attempts and last_attempt_at for observability

### 3. Extending to 100+ Sources

**Strategy: Source Registry + Plugin Pattern**

**Phase 1 (Current):**
- Hardcoded 3 marketplace parsers in `IngestionService._parse_product()`
- Add new parser → commit → deploy

**Phase 2 (Plugin Pattern):**
```python
# sources/registry.py
PARSERS = {
    "1stdibs": FirstDibsParser,
    "fashionphile": FashionphileParser,
    "grailed": GrailedParser,
}

# sources/base.py - Abstract parser
class Marketplace Parser:
    def parse(self, data: dict) -> dict: ...

# sources/amazon_luxury.py - New source
class AmazonLuxuryParser(MarketplaceParser):
    def parse(self, data: dict) -> dict:
        return {
            "source": "amazon_luxury",
            "brand": data["brand"],
            ...
        }

# app/services/ingest.py
parser_class = PARSERS[source]
parser = parser_class()
parsed = parser.parse(product_data)
```

**Phase 3 (Task Queue):**
- Each marketplace has its own async task (scheduled via APScheduler or Celery)
- Marketplace-specific rate limits, auth tokens, retry logic
- Central queue coordinator submits tasks in parallel

**Data Flow for 100+ sources:**
```
APScheduler / Celery
    ↓ (scheduled tasks)
[1stdibs_task] [Fashionphile_task] [Grailed_task] ... [NewSource_task]
    ↓ (all in parallel)
     Fetch product data (async httpx)
    ↓
   Parse via plugin
    ↓
  Upsert to SQLite
    ↓
Create events
    ↓
[Event log]  →  [Webhook delivery] (background)
```

---

## Project Structure

```
entrupy/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, middleware, error handlers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── schemas.py          # ORM models
│   │   ├── pydantic_schemas.py # Request/response models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py             # API key authentication
│   │   ├── products.py         # Product CRUD endpoints
│   │   ├── analytics.py        # Analytics endpoints
│   │   ├── events.py           # Event log & webhook endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingest.py           # Data ingestion service
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── webhooks.py         # Webhook delivery service
├── frontend/                   # React/Vite app
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures
│   ├── test_api.py             # API endpoint tests
│   ├── test_ingestion.py       # Ingestion service tests
├── sample_products/            # Sample JSON files for testing
│   ├── 1stdibs_luxury_handbags.json
│   ├── fashionphile_designer_bags.json
│   ├── grailed_streetwear.json
├── init_db.py                  # Database initialization script
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── plan.md                     # Implementation plan
```

---

## Test Overview

**Total: 12+ tests covering:**

1. ✅ **API Auth** - Missing/invalid/valid API key behavior
2. ✅ **Ingestion** - Parse each marketplace format
3. ✅ **Price Detection** - History & event creation on price change
4. ✅ **Idempotency** - Re-ingesting same data → no duplicates
5. ✅ **Filtering** - Source, brand, category, price range
6. ✅ **Pagination** - Correct page/page_size handling
7. ✅ **Analytics** - Correct aggregates
8. ✅ **Product Detail** - Full history included
9. ✅ **Events** - Listing with filters
10. ✅ **Webhooks** - Create, list, delete
11. ✅ **Validation** - Bad input → 422

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test:**
```bash
pytest tests/test_api.py::test_api_key_missing -v
```

---

## Known Limitations

1. **SQLite** → Not suitable for multi-process writes. Use PostgreSQL in production.
2. **Local JSON ingestion** → Production would fetch from live APIs. Implement API clients for 1stDibs, Fashionphile, Grailed.
3. **Webhook retry** → No persistent queue; if server crashes mid-delivery, retries are lost. Use Celery/RabbitMQ in production.
4. **Frontend dashboard** → Basic React implementation; add real-time updates via WebSocket for live price tracking.
5. **API Key storage** → Storing key_hash only; production should use bcrypt or argon2.
6. **Cross-source product matching** → Currently kept separate; add deduplication logic for same product across marketplaces.

---

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Ingest 1000 products | O(n) | Async file reads + batch DB inserts |
| List products with filter | O(n log n) | Index on source, brand, category |
| Get product + history | O(log n + m) | O(log n) to find product, O(m) to fetch m history entries |
| Webhook delivery | Non-blocking | Background task, 3 retries max |

---

## Verification Checklist

- [ ] Database initialized: `python init_db.py`
- [ ] API key created and working
- [ ] Server running: `uvicorn app.main:app --reload`
- [ ] POST /api/refresh returns products upserted
- [ ] GET /api/products filters by source
- [ ] GET /api/analytics returns stats
- [ ] GET /api/events paginated
- [ ] POST /api/webhooks creates subscription
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Frontend loads: `npm run dev`

---

## Future Enhancements

1. **Real-time price tracking** - WebSocket connections for live price updates
2. **Email/SMS alerts** - Alternative notification channels
3. **Browser extension** - Price monitoring for shopping sites
4. **AI price prediction** - Forecast future prices based on history
5. **Multi-currency support** - Normalize prices across currencies
6. **User authentication** - Per-user product watchlists
7. **Rate limiting** - Protect API from abuse
8. **GraphQL API** - Alternative query interface

---

## Support

For issues or questions, check the plan.md for implementation details or review API documentation above.
