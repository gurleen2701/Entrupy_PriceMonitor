from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime
from app.models.database import get_db
from app.models.schemas import Event, WebhookSubscription, ApiKey
from app.models.pydantic_schemas import (
    EventResponse, WebhookSubscriptionCreate, WebhookSubscriptionResponse, PaginatedResponse
)
from app.api.auth import verify_api_key
from typing import Optional

router = APIRouter(prefix="/api", tags=["events"])

@router.get("/events", response_model=PaginatedResponse)
async def list_events(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    delivered: Optional[bool] = Query(None, description="Filter by delivery status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key)
):
    """List events with optional filters and pagination"""
    
    filters = []
    
    if product_id is not None:
        filters.append(Event.product_id == product_id)
    if delivered is not None:
        filters.append(Event.delivered == delivered)
    if start_date:
        filters.append(Event.created_at >= start_date)
    if end_date:
        filters.append(Event.created_at <= end_date)
    
    # Count total
    count_query = select(func.count(Event.id))
    if filters:
        count_query = count_query.where(and_(*filters))
    
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = select(Event).order_by(Event.created_at.desc())
    if filters:
        query = query.where(and_(*filters))
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return PaginatedResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=[EventResponse.model_validate(e) for e in events]
    )

@router.post("/webhooks", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook: WebhookSubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key)
):
    """Register a webhook subscription"""
    
    db_webhook = WebhookSubscription(**webhook.model_dump())
    db.add(db_webhook)
    await db.commit()
    await db.refresh(db_webhook)
    
    return WebhookSubscriptionResponse.model_validate(db_webhook)

@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key)
):
    """Unregister a webhook subscription"""
    
    result = await db.execute(
        select(WebhookSubscription).where(WebhookSubscription.id == webhook_id)
    )
    webhook = result.scalars().first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    await db.delete(webhook)
    await db.commit()
    
    return None

@router.get("/webhooks", response_model=list[WebhookSubscriptionResponse])
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    api_key: ApiKey = Depends(verify_api_key)
):
    """List all active webhook subscriptions"""
    
    result = await db.execute(
        select(WebhookSubscription).where(WebhookSubscription.is_active == True)
    )
    webhooks = result.scalars().all()
    
    return [WebhookSubscriptionResponse.model_validate(w) for w in webhooks]
