from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.database import get_db
from app.models.schemas import Product, PriceHistory, ApiKey
from app.models.pydantic_schemas import AnalyticsResponse
from app.api.auth import verify_api_key
from typing import Dict

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key)
):
    """Get analytics and aggregate statistics"""
    
    # Total products
    result = await db.execute(select(func.count(Product.id)))
    total_products = result.scalar() or 0
    
    # Products by source (GROUP BY source)
    result = await db.execute(
        select(Product.source, func.count(Product.id).label('count'))
        .group_by(Product.source)
    )
    products_by_source = {row[0]: row[1] for row in result.all()}
    
    # Average price by category (GROUP BY category)
    result = await db.execute(
        select(Product.category, func.avg(Product.current_price).label('avg_price'))
        .group_by(Product.category)
    )
    average_price_by_category = {row[0]: round(float(row[1]) if row[1] else 0, 2) for row in result.all()}
    
    # Total price changes (count of price_history entries)
    result = await db.execute(select(func.count(PriceHistory.id)))
    total_price_changes = result.scalar() or 0
    
    # Price stats (min, max, avg)
    result = await db.execute(
        select(
            func.min(Product.current_price).label('min'),
            func.max(Product.current_price).label('max'),
            func.avg(Product.current_price).label('avg')
        )
    )
    row = result.first()
    price_stats = {
        "min": float(row[0]) if row[0] else 0,
        "max": float(row[1]) if row[1] else 0,
        "avg": round(float(row[2]) if row[2] else 0, 2)
    }
    
    return AnalyticsResponse(
        total_products=total_products,
        products_by_source=products_by_source,
        average_price_by_category=average_price_by_category,
        total_price_changes=total_price_changes,
        price_stats=price_stats
    )
