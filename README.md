# Entrupy - Product Price Monitoring System

A full-stack product price monitoring system for luxury goods across 3 marketplaces (1stDibs, Fashionphile, Grailed), featuring:

- **SQLite Database** with price history tracking and event logging
- **Async REST API** (FastAPI) with API key authentication
- **Event-log based notifications** with optional webhook delivery
- **React Dashboard** for product browsing and analytics
- **Comprehensive Test Suite** with 12+ test cases

## Setup Instructions

### Prerequisites
- Python 3.13
- pip or conda
- Node.js 16+ (for frontend)
- Built and tested on Windows

### Quick Start (Windows)

Run the setup script to install everything automatically:

```cmd
setup.bat
```

This will create a virtual environment, install Python and Node.js dependencies, and initialize the database. Then follow the printed instructions to start the backend and frontend.

After setup, activate the virtual environment and create a test API key:

```cmd
venv\Scripts\activate
```
Then run the script from [Step 4 - Create Test API Key](#4-create-test-api-key) below.

### Step-by-Step Setup

#### Backend Setup

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

### Python Flask receiver
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

Windows (PowerShell):
```powershell
curl.exe -X POST -H "X-API-Key: test_key_12345" -H "Content-Type: application/json" --% -d "{\"url\": \"http://localhost:9000/webhook\", \"secret\": \"test_secret\", \"consumer_name\": \"local_test\"}" http://localhost:8000/api/webhooks
```

4. Trigger refresh to send webhook events:
```bash
curl -X POST "http://localhost:8000/api/refresh" -H "X-API-Key: test_key_12345"
```

Windows (PowerShell):
```powershell
curl.exe -X POST -H "X-API-Key: test_key_12345" http://localhost:8000/api/refresh
```

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
```

---

## API Documentation

### Authentication
All endpoints (except `/health` and `/`) require `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/products
```

Windows (PowerShell):
```powershell
curl.exe -H "X-API-Key: your_api_key" http://localhost:8000/api/products
```

### Endpoints

#### Products

**GET /api/products** - List products with filters and pagination
```bash
curl -H "X-API-Key: test_key_12345" \
  "http://localhost:8000/api/products?source=1stdibs&min_price=1000&max_price=5000&page=1&page_size=20"
```

Windows (PowerShell):
```powershell
curl.exe -H "X-API-Key: test_key_12345" "http://localhost:8000/api/products?source=1stdibs&min_price=1000&max_price=5000&page=1&page_size=20"
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

Windows (PowerShell):
```powershell
curl.exe -H "X-API-Key: test_key_12345" http://localhost:8000/api/products/1
```

**POST /api/refresh** - Trigger data ingestion
```bash
curl -X POST -H "X-API-Key: test_key_12345" http://localhost:8000/api/refresh
```

Windows (PowerShell):
```powershell
curl.exe -X POST -H "X-API-Key: test_key_12345" http://localhost:8000/api/refresh
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

Windows (PowerShell):
```powershell
curl.exe -H "X-API-Key: test_key_12345" http://localhost:8000/api/analytics
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

Windows (PowerShell):
```powershell
curl.exe -H "X-API-Key: test_key_12345" "http://localhost:8000/api/events?product_id=1&delivered=false&page=1&page_size=20"
```

Query Parameters:
- `product_id` (int) - Filter by product ID
- `delivered` (bool) - Filter by delivery status
- `start_date` (datetime) - Filter by start date
- `end_date` (datetime) - Filter by end date
- `page` (int, default=1)
- `page_size` (int, default=20, max=100)

**POST /api/webhooks** - Register webhook

Linux/macOS:
```bash
curl -X POST "http://localhost:8000/api/webhooks" \
  -H "X-API-Key: test_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://localhost:9000/webhook","secret":"test_secret","consumer_name":"local_test"}'
```

Windows (PowerShell):
```powershell
curl.exe -X POST -H "X-API-Key: test_key_12345" -H "Content-Type: application/json" --% -d "{\"url\": \"http://localhost:9000/webhook\", \"secret\": \"test_secret\", \"consumer_name\": \"local_test\"}" http://localhost:8000/api/webhooks
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
curl -X DELETE -H "X-API-Key: test_key_12345" http://localhost:8000/api/webhooks/1
```

Windows (PowerShell):
```powershell
curl.exe -X DELETE -H "X-API-Key: test_key_12345" http://localhost:8000/api/webhooks/1
```

**GET /api/webhooks** - List active webhooks
```bash
curl -H "X-API-Key: test_key_12345" http://localhost:8000/api/webhooks
```

Windows (PowerShell):
```powershell
curl.exe -H "X-API-Key: test_key_12345" http://localhost:8000/api/webhooks
```

#### Health & Info

**GET /health** - Health check
```bash
curl http://localhost:8000/health
```

Windows (PowerShell):
```powershell
curl.exe http://localhost:8000/health
```

**GET /** - API info
```bash
curl http://localhost:8000/
```

Windows (PowerShell):
```powershell
curl.exe http://localhost:8000/
```

---

## Design Decisions

### 1. How Does Price History Scale? What Happens at Millions of Rows?

**Approach:** Append-only `price_history` table with composite index on `(product_id, recorded_at)`.

**Why append-only?**
- Price history is immutable — records are only inserted, never updated or deleted. This eliminates lock contention and makes writes cheap even under high concurrency.
- Append-only workloads are ideal for SQLite's WAL (Write-Ahead Logging) mode and scale naturally to PostgreSQL partitioned tables.

**Indexing strategy:**
- **Composite index `idx_product_recorded` on `(product_id, recorded_at)`** — enables fast range queries like "price history for product X in the last 30 days" without scanning the full table.
- **Index on `source`** — supports cross-marketplace analytics queries (e.g., average price change by source).

**At millions of rows:**
- **Time-range scans:** Queries always include a `recorded_at` filter (e.g., `WHERE recorded_at >= NOW() - interval '30 days'`), so the DB reads only the relevant partition/index range — not all rows.
- **Partitioning (PostgreSQL):** The table structure is designed for time-based partitioning by month. Each month becomes its own physical table, reducing index size and enabling fast archival.
- **Archival strategy:** Records older than 1 year can be summarized into weekly/monthly aggregates and moved to cold storage. The current schema already stores `old_price` and `new_price` per entry, making aggregation straightforward.
- **Batch commits:** The ingestion service uses a single `db.commit()` after processing all products (not per-product), reducing write amplification.

**Current implementation choice (SQLite):** Chosen for zero-configuration local development. The async engine (`aiosqlite`) provides non-blocking queries. For production at scale, PostgreSQL with table partitioning would be a direct migration — no schema changes needed.

### 2. How Did You Implement Notification of Price Changes, and Why?

**Architecture: Event Log + Webhook Push (dual-path)**

When a data refresh detects a price change, two things happen:
1. An **immutable event record** is written to the `events` table (`event_type="price_change"` with `old_price`, `new_price`, `source` in the JSON payload).
2. **Webhook delivery** is triggered as a FastAPI `BackgroundTask` — the API response returns immediately while webhooks are dispatched asynchronously.

**Why this hybrid approach over alternatives?**

| Approach | Pros | Cons |
|----------|------|------|
| **Pure polling (GET /events)** | Simple, stateless | High latency, wasted bandwidth when no changes |
| **Pure webhooks** | Real-time push | No durability if consumer is down; can't replay missed events |
| **Event log + webhooks (chosen)** | Real-time push AND durable history | Slightly more complex |

The event log acts as the **source of truth** — events are never lost, even if webhook delivery fails. Consumers can:
- Receive real-time push via webhook subscriptions
- Poll `GET /api/events?delivered=false` to catch anything they missed
- Replay historical events by querying with `start_date`/`end_date` filters

**Webhook reliability guarantees:**
- **HMAC-SHA256 signatures:** Every webhook payload is signed with the subscriber's secret (`X-Webhook-Signature: sha256={hexdigest}`), so consumers can verify authenticity.
- **Retry with exponential backoff:** Uses `tenacity` library — 3 attempts with exponential wait (2s, 4s, 8s). Failed deliveries are tracked via `delivery_attempts` and `last_attempt_at` columns.
- **Non-blocking:** Webhook delivery runs as a background task (`background_tasks.add_task()`), so it never delays the API response to the refresh caller.
- **Async HTTP client:** Uses `httpx.AsyncClient` with a 10-second timeout per delivery attempt.

**Event types generated:**
- `price_change` — when `current_price` differs from the incoming price
- `product_created` — when a new product URL is ingested for the first time

### 3. How Would You Extend This System to 100+ Data Sources?

**Current state (3 sources):** Each marketplace has a parsing branch in `IngestionService._parse_product()` that maps raw JSON fields to a unified Product schema. This works for 3 sources but wouldn't scale.

**Phase 1 — Plugin/Registry pattern:**
```python
# sources/base.py
class MarketplaceParser(ABC):
    @abstractmethod
    def parse(self, data: dict) -> dict: ...

# sources/registry.py
PARSERS = {
    "1stdibs": FirstDibsParser,
    "fashionphile": FashionphileParser,
    "grailed": GrailedParser,
}

# Adding a new source = one new file + one registry entry
# sources/amazon_luxury.py
class AmazonLuxuryParser(MarketplaceParser):
    def parse(self, data: dict) -> dict:
        return {"source": "amazon_luxury", "brand": data["brand"], ...}
```
Each parser is self-contained. Adding a source requires zero changes to existing code.

**Phase 2 — Parallel task queue:**
- Each marketplace gets its own async task with source-specific rate limits, auth tokens, and retry policies.
- A task coordinator (APScheduler or Celery) runs all sources in parallel.
- Sources that fail don't block others — errors are logged and skipped.

**Phase 3 — Infrastructure:**
```
Scheduler (APScheduler / Celery Beat)
    ↓ triggers
[Source 1] [Source 2] ... [Source N]  (parallel async tasks)
    ↓ each
Fetch → Parse (via plugin) → Upsert → Create Events
    ↓
Event Log  →  Webhook Delivery (background)
```

**Database considerations at 100+ sources:**
- The `sources` table already tracks each marketplace with `last_synced_at` for monitoring sync health.
- Index on `(source, recorded_at)` in `price_history` enables per-source analytics without full table scans.
- The `product_metadata` JSON column stores marketplace-specific fields (1stDibs has multi-currency pricing, Fashionphile has condition breakdowns, Grailed has sold status) — new sources can store arbitrary metadata without schema migrations.

### 4. Schema Design Rationale

**Product deduplication:** Products are keyed by `product_url` (UNIQUE constraint). The same physical item on different marketplaces (different URLs) is stored as separate products. This is intentional — we're tracking **listings**, not items. Each listing has its own independent price history, which enables cross-marketplace price comparison and arbitrage detection.

**Metadata flexibility:** Each marketplace provides different fields (1stDibs: seller ratings, period, multi-currency pricing; Fashionphile: condition details per component, authentication certificates; Grailed: sold status, style tags). Rather than adding nullable columns for each, a JSON `product_metadata` column stores marketplace-specific data. This avoids schema migrations when adding sources.

**API key authentication:** SHA256-hashed keys stored in `api_keys` table. The raw key is sent via `X-API-Key` header, hashed server-side, and looked up against `key_hash`. Per-request usage is logged to `api_usage` table (endpoint, method, status code, timestamp) for audit and future rate limiting.

**Async throughout:** The entire stack is async — `aiosqlite` for the database, `aiofiles` for reading sample JSON files, `httpx.AsyncClient` for webhook delivery. This ensures the server can handle concurrent requests without blocking on I/O.

### 5. Assumptions Made

- **One product per URL:** The same physical item listed on multiple marketplaces is tracked independently. Cross-marketplace deduplication (matching by brand + model + condition) was considered but left as a future enhancement — URL-based dedup is deterministic and avoids false matches.
- **Price comparison is exact:** A price change is detected when `new_price != current_price`. No tolerance threshold is applied, since even small price changes on luxury goods are significant.
- **Sample data represents live API responses:** The ingestion service reads local JSON files. In production, this would be replaced with async HTTP clients hitting marketplace APIs, but the parsing and upsert logic remains identical. For local testing, the user needs to update the price in the sample_products json and then trigger refresh api either via UI or via CURL
- **USD default currency:** All prices are stored in USD. Multi-currency data (e.g., 1stDibs `all_prices`) is preserved in metadata for reference but not normalized.

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

1. **SQLite for production** → SQLite does not support concurrent writes from multiple processes. For production deployments, migrate to PostgreSQL (the async SQLAlchemy setup supports this with a connection string change).
2. **Local JSON ingestion** → The ingestion service reads from local `sample_products/*.json` files. Production would replace this with async HTTP clients (`httpx`) fetching from live marketplace APIs, with per-source rate limiting and authentication.
3. **Webhook retry is in-memory** → Retries use `tenacity` within the same process. If the server crashes mid-delivery, pending retries are lost. A production system would use a persistent task queue (Celery + Redis/RabbitMQ) to guarantee delivery.
4. **No cross-source product deduplication** → The same physical item on different marketplaces is stored as separate products (keyed by URL). Semantic matching (by brand + model + condition) would enable cross-marketplace price comparison but risks false positives.
5. **API key hashing uses SHA256** → Sufficient for API keys with high entropy, but production should use bcrypt or argon2 for defense against brute-force attacks on leaked hashes.
6. **Usage logging not wired to middleware** → The `api_usage` table and `log_api_usage()` function exist but are not yet integrated into a request/response middleware. Per-request tracking requires connecting this to a FastAPI middleware or dependency.
7. **No rate limiting** → API consumers are authenticated but not rate-limited. Production should enforce per-key request quotas using the `api_usage` table or a Redis-based rate limiter.
8. **Frontend is basic** → Functional React dashboard with filtering and charts, but no real-time updates (WebSocket), loading states, or error boundaries.
9. **Price comparison is exact** → Any difference between `new_price` and `current_price` triggers a change event. For some use cases, a configurable tolerance threshold (e.g., ignore changes < 1%) would reduce noise.
10. **Single-currency storage** → Prices are stored in USD. 1stDibs provides multi-currency data (`all_prices`) which is preserved in metadata but not used for normalization.

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
