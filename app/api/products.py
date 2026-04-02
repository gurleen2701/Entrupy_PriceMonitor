from fastapi import APIRouter, Depends, Query, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.database import get_db
from app.models.schemas import Product, ApiKey
from app.models.pydantic_schemas import ProductResponse, RefreshSummary, PaginatedResponse
from app.api.auth import verify_api_key
from app.services.ingest import IngestionService
from app.notifications.webhooks import NotificationService
from typing import List, Optional

router = APIRouter(prefix="/api", tags=["products"])

@router.post("/refresh", response_model=RefreshSummary)
async def refresh_products(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key)
):
    """Trigger data ingestion from sample products"""
    ingestion_service = IngestionService(db)
    result = await ingestion_service.ingest_all()
    
    # Schedule webhook delivery for newly created events
    if result["events_created"] > 0:
        # Get the newly created events and schedule delivery
        events_result = await db.execute(
            select(Product.id).order_by(Product.created_at.desc()).limit(result["events_created"])
        )
        product_ids = events_result.scalars().all()
        
        notification_service = NotificationService(db)
        for product_id in product_ids:
            # Schedule in background
            background_tasks.add_task(
                notification_service.schedule_webhook_delivery,
                product_id
            )
    
    return RefreshSummary(**result)

@router.get("/products", response_model=PaginatedResponse)
async def list_products(
    source: Optional[str] = Query(None, description="Filter by marketplace source"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key)
):
    """List products with optional filters and pagination"""
    
    # Build filter conditions
    filters = []
    
    if source:
        filters.append(Product.source == source)
    if brand:
        filters.append(Product.brand.ilike(f"%{brand}%"))
    if category:
        filters.append(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        filters.append(Product.current_price >= min_price)
    if max_price is not None:
        filters.append(Product.current_price <= max_price)
    
    # Count total matching products
    count_query = select(func.count(Product.id))
    if filters:
        count_query = count_query.where(and_(*filters))
    
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = select(Product)
    if filters:
        query = query.where(and_(*filters))
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return PaginatedResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=[ProductResponse.model_validate(p) for p in products]
    )

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key)
):
    """Get single product with price history"""
    
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Reload to get price_history relationship
    from sqlalchemy import inspect
    inspect(product)
    
    return ProductResponse.model_validate(product)
