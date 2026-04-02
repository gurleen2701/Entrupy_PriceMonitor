import pytest
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.ingest import IngestionService
from app.models.schemas import Product, PriceHistory, Event

@pytest.mark.asyncio
async def test_ingestion_service_detects_marketplace(test_db):
    """Test that ingestion service correctly detects marketplace from filename"""
    service = IngestionService(db=None, sample_dir="./sample_products")
    
    assert service._detect_source("1stdibs_chanel_belts_01.json") == "1stdibs"
    assert service._detect_source("fashionphile_tiffany_01.json") == "fashionphile"
    assert service._detect_source("grailed_amiri_apparel_01.json") == "grailed"
    assert service._detect_source("unknown_source.json") is None

@pytest.mark.asyncio
async def test_parse_1stdibs_product():
    """Test parsing of 1stdibs product format"""
    service = IngestionService(db=None)
    
    data = {
        "product_url": "https://www.1stdibs.com/fashion/accessories/belts/chanel-5-rows-belt/id-v_3093883/",
        "model": "CHANEL 5 Rows Belt in Ruthenium Metal",
        "price": 2617.6,
        "size": None,
        "brand": "Chanel",
        "full_description": "Beautiful CHANEL belt 5 rows...",
        "main_images": [
            {
                "url": "https://scraping-framework-s3-public.s3.us-east-1.amazonaws.com/image_cache/c9522dd6.jpg",
                "format": "image/jpeg",
                "metadata": {"description": "Belt image"}
            }
        ]
    }
    
    result = service._parse_product(data, "1stdibs")
    
    assert result["source"] == "1stdibs"
    assert result["brand"] == "Chanel"
    assert result["current_price"] == 2617.6
    assert result["category"] == "Accessories"
    assert "full_description" in result["metadata"]

@pytest.mark.asyncio
async def test_parse_fashionphile_product():
    """Test parsing of Fashionphile product format"""
    service = IngestionService(db=None)
    
    data = {
        "product_url": "https://www.fashionphile.com/products/tiffany-18k-rose-gold-hoop-earrings",
        "condition": "Shows Wear",
        "price": 1480.0,
        "currency": "USD",
        "image_url": "https://scraping-framework-s3-public.s3.us-east-1.amazonaws.com/52759c.jpg",
        "main_images": [
            {
                "url": "https://scraping-framework-s3-public.s3.us-east-1.amazonaws.com/52759c.jpg",
                "format": "image/jpeg",
                "metadata": {"description": "Earrings image"}
            }
        ],
        "product_id": "84f903a5-3c76-53d5-9d31-25956c2ffdc3",
        "brand_id": "tiffany",
        "function_id": "apparel_authentication",
        "metadata": {
            "garment_type": "jewelry",
            "description": "This is an authentic TIFFANY 18K Rose Gold Medium T Wire Hoop Earrings.",
            "size_dimensions": {"length": "23 mm", "width": "11 mm"}
        }
    }
    
    result = service._parse_product(data, "fashionphile")
    
    assert result["source"] == "fashionphile"
    assert result["current_price"] == 1480.0
    assert result["condition"] == "Shows Wear"
    assert result["currency"] == "USD"
    assert result["category"] == "Jewelry"

@pytest.mark.asyncio
async def test_parse_grailed_product():
    """Test parsing of Grailed product format"""
    service = IngestionService(db=None)
    
    data = {
        "brand": "amiri",
        "model": "Amiri Washed Filigree T-Shirt",
        "price": 425.0,
        "size": None,
        "image_url": "https://media-assets.grailed.com/prd/listing/temp/069726883ab242969a4b4e5e42429c2a",
        "product_url": "https://www.grailed.com/listings/83672676",
        "metadata": {
            "seller_info": {},
            "full_product_description": "T-shirt details...",
            "color": "Black",
            "style": "Street",
            "is_sold": False
        },
        "main_images": [
            {
                "url": "https://media-assets.grailed.com/prd/listing/temp/069726883ab242969a4b4e5e42429c2a?w=1600",
                "format": "image/jpeg",
                "metadata": {"description": "T-shirt image"}
            }
        ]
    }
    
    result = service._parse_product(data, "grailed")
    
    assert result["source"] == "grailed"
    assert result["brand"] == "amiri"
    assert result["current_price"] == 425.0
    assert result["metadata"]["color"] == "Black"
    assert result["metadata"]["style"] == "Street"

@pytest.mark.asyncio
async def test_ingestion_idempotency(test_db):
    """Test that re-ingesting same data doesn't create duplicates"""
    # This would require a more complex setup with actual DB session
    # Simplified test structure
    service = IngestionService(db=test_db)
    
    sample_data = {
        "source": "test",
        "source_product_id": "123",
        "product_url": "https://example.com/unique",
        "brand": "Test",
        "model": "Model",
        "category": "Category",
        "current_price": 100,
        "currency": "USD"
    }
    
    # In a full test, we would:
    # 1. Insert once
    # 2. Insert again with same URL
    # 3. Verify only 1 product exists

@pytest.mark.asyncio
async def test_price_change_detection():
    """Test that price change creates history entry and event"""
    # This requires database session - simplified structure
    pass

@pytest.mark.asyncio
async def test_upsert_creates_event():
    """Test that upsert operation creates events"""
    pass
