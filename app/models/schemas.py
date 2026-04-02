from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Index, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.database import Base

class MarketplaceEnum(str, enum.Enum):
    FIRST_DIBS = "1stdibs"
    FASHIONPHILE = "fashionphile"
    GRAILED = "grailed"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False, index=True)  # marketplace enum as string
    source_product_id = Column(String, nullable=False)
    product_url = Column(String, unique=True, index=True, nullable=False)
    brand = Column(String, index=True, nullable=False)
    model = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    current_price = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    condition = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    product_metadata = Column("metadata", JSON, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __getattr__(self, name):
        if name == "metadata":
            return self.product_metadata
        raise AttributeError(f"{self.__class__.__name__!r} object has no attribute {name!r}")

    def __setattr__(self, name, value):
        if name == "metadata":
            object.__setattr__(self, "product_metadata", value)
        else:
            super().__setattr__(name, value)

    # Relationships
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    old_price = Column(Float, nullable=True)
    new_price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="price_history")
    
    # Index for fast lookups: (product_id, recorded_at DESC)
    __table_args__ = (
        Index('idx_product_recorded', 'product_id', 'recorded_at'),
    )

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    base_url = Column(String, nullable=False)
    last_synced_at = Column(DateTime, nullable=True)

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    key_hash = Column(String, unique=True, nullable=False)
    consumer_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class ApiUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False, index=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # e.g., "price_change"
    payload = Column(JSON, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    delivered = Column(Boolean, default=False, nullable=False)
    delivery_attempts = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime, nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="events")

class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    consumer_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
