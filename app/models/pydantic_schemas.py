from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# Product Schemas
class ProductBase(BaseModel):
    source: str
    source_product_id: str
    product_url: str
    brand: str
    model: str
    category: str
    current_price: float
    currency: str = "USD"
    condition: Optional[str] = None
    image_url: Optional[str] = None
    metadata: Optional[dict] = {}

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    current_price: float
    metadata: Optional[dict] = None
    image_url: Optional[str] = None

class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    old_price: Optional[float]
    new_price: float
    recorded_at: datetime
    source: str

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    source: str
    source_product_id: str
    product_url: str
    brand: str
    model: str
    category: str
    current_price: float
    currency: str
    condition: Optional[str]
    image_url: Optional[str]
    metadata: Optional[dict] = Field(default_factory=dict, alias="product_metadata")
    created_at: datetime
    updated_at: datetime
    price_history: Optional[List[PriceHistoryResponse]] = []

    class Config:
        from_attributes = True
        populate_by_name = True

# Event Schemas
class EventResponse(BaseModel):
    id: int
    product_id: int
    event_type: str
    payload: dict
    created_at: datetime
    delivered: bool
    delivery_attempts: int
    last_attempt_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Analytics Schemas
class AnalyticsResponse(BaseModel):
    total_products: int
    products_by_source: dict
    average_price_by_category: dict
    total_price_changes: int
    price_stats: dict  # {min, max, avg}

# Webhook Schemas
class WebhookSubscriptionCreate(BaseModel):
    url: str
    secret: str
    consumer_name: str

class WebhookSubscriptionResponse(BaseModel):
    id: int
    url: str
    consumer_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Refresh Response
class RefreshSummary(BaseModel):
    products_upserted: int
    price_changes_detected: int
    events_created: int

# Pagination
class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[Any]
