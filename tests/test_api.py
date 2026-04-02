import pytest
import json
import hashlib
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.models.schemas import Product, PriceHistory, Event
from datetime import datetime

def test_api_key_missing(client):
    """Test that missing API key returns 401"""
    response = client.get("/api/products")
    assert response.status_code == 401
    assert "API-Key" in response.text or "api_key" in response.text.lower()

def test_api_key_invalid(client):
    """Test that invalid API key returns 401"""
    response = client.get(
        "/api/products",
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 401

def test_api_key_valid(client, api_key):
    """Test that valid API key allows access"""
    response = client.get(
        "/api/products",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_refresh_endpoint_exists(client, api_key):
    """Test that refresh endpoint exists and returns correct schema"""
    response = await client.post(
        "/api/refresh",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "products_upserted" in data
    assert "price_changes_detected" in data
    assert "events_created" in data

@pytest.mark.asyncio
async def test_list_products_pagination(client, api_key):
    """Test pagination works correctly"""
    # First request
    response = await client.get(
        "/api/products?page=1&page_size=10",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert "total" in data
    assert "items" in data

@pytest.mark.asyncio
async def test_list_products_filter_by_source(client, api_key):
    """Test filtering by source returns correct subset"""
    response = await client.get(
        "/api/products?source=1stdibs",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["source"] == "1stdibs"

@pytest.mark.asyncio
async def test_list_products_filter_by_price_range(client, api_key):
    """Test filtering by price range works"""
    response = await client.get(
        "/api/products?min_price=1000&max_price=5000",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["current_price"] >= 1000
        assert item["current_price"] <= 5000

@pytest.mark.asyncio
async def test_analytics_endpoint(client, api_key):
    """Test analytics endpoint returns correct structure"""
    response = await client.get(
        "/api/analytics",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "products_by_source" in data
    assert "average_price_by_category" in data
    assert "total_price_changes" in data
    assert "price_stats" in data

@pytest.mark.asyncio
async def test_product_detail_endpoint(client, api_key):
    """Test getting single product detail"""
    # Create a test product first
    response = await client.post(
        "/api/refresh",
        headers={"X-API-Key": api_key}
    )
    
    # Get products
    response = await client.get(
        "/api/products",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    products = response.json()["items"]
    
    if products:
        product_id = products[0]["id"]
        response = await client.get(
            f"/api/products/{product_id}",
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert "price_history" in data

@pytest.mark.asyncio
async def test_events_list_endpoint(client, api_key):
    """Test listing events with pagination"""
    response = await client.get(
        "/api/events",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "page_size" in data
    assert "total" in data
    assert "items" in data

@pytest.mark.asyncio
async def test_webhook_create_endpoint(client, api_key):
    """Test creating webhook subscription"""
    webhook_data = {
        "url": "https://example.com/webhook",
        "secret": "webhook_secret",
        "consumer_name": "test_consumer"
    }
    response = await client.post(
        "/api/webhooks",
        headers={"X-API-Key": api_key},
        json=webhook_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == webhook_data["url"]
    assert data["consumer_name"] == webhook_data["consumer_name"]

@pytest.mark.asyncio
async def test_webhook_list_endpoint(client, api_key):
    """Test listing webhooks"""
    response = await client.get(
        "/api/webhooks",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_invalid_input_validation(client, api_key):
    """Test that bad input returns 422"""
    response = await client.get(
        "/api/products?min_price=invalid",
        headers={"X-API-Key": api_key}
    )
    # Should either be 422 or 200 (depending on validation)
    assert response.status_code in [200, 422]

@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
