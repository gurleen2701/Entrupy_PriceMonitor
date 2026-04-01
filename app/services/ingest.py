import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schemas import Product, PriceHistory, Event
import aiofiles

class IngestionService:
    """Service for ingesting product data from sample JSON files"""
    
    def __init__(self, db: AsyncSession, sample_dir: str = "./sample_products"):
        self.db = db
        self.sample_dir = Path(sample_dir)
    
    async def ingest_all(self) -> Dict[str, int]:
        """
        Ingest all product data from sample directory.
        Returns: {products_upserted, price_changes_detected, events_created}
        """
        result = {
            "products_upserted": 0,
            "price_changes_detected": 0,
            "events_created": 0
        }
        
        if not self.sample_dir.exists():
            return result
        
        for file_path in self.sample_dir.glob("*.json"):
            source = self._detect_source(file_path.name)
            if not source:
                continue
            
            try:
                async with aiofiles.open(file_path, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                
                # Handle both single product and list of products
                products = data if isinstance(data, list) else [data]
                
                for product_data in products:
                    upserted, price_changed, event_created = await self._upsert_product(
                        product_data, source
                    )
                    if upserted:
                        result["products_upserted"] += 1
                    if price_changed:
                        result["price_changes_detected"] += 1
                    if event_created:
                        result["events_created"] += 1
            
            except Exception as e:
                print(f"Error ingesting {file_path}: {e}")
                continue
        
        await self.db.commit()
        return result
    
    def _detect_source(self, filename: str) -> Optional[str]:
        """Detect marketplace source from filename"""
        filename_lower = filename.lower()
        if filename_lower.startswith("1stdibs"):
            return "1stdibs"
        elif filename_lower.startswith("fashionphile"):
            return "fashionphile"
        elif filename_lower.startswith("grailed"):
            return "grailed"
        return None
    
    def _parse_product(self, data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Parse marketplace-specific JSON to common Product schema"""
        if source == "1stdibs":
            # Extract main image URL from main_images array
            image_url = ""
            if data.get("main_images") and isinstance(data.get("main_images"), list):
                image_url = data["main_images"][0].get("url", "") if data["main_images"] else ""
            
            product_url = data.get("product_url", "")
            # Extract product ID from URL if available, otherwise use product_id field or hash
            source_product_id = data.get("product_id", "")
            if not source_product_id:
                source_product_id = product_url.split("/id-")[-1].rstrip("/") if "/id-" in product_url else str(hash(product_url))
            
            return {
                "source": source,
                "source_product_id": source_product_id,
                "product_url": product_url,
                "brand": data.get("brand", "Unknown"),
                "model": data.get("model", ""),
                "category": data.get("category", "Accessories"),  # Use category if provided, else default
                "current_price": float(data.get("price", 0)),
                "currency": "USD",
                "condition": "Vintage/Pre-owned",  # 1stdibs specializes in vintage
                "image_url": image_url,
                "metadata": {
                    "full_description": data.get("full_description", ""),
                    "size": data.get("size", None),
                    "seller_location": data.get("seller_location", ""),
                }
            }
        
        elif source == "fashionphile":
            # Extract main image URL from main_images array
            image_url = data.get("image_url", "")
            if not image_url and data.get("main_images") and isinstance(data.get("main_images"), list):
                image_url = data["main_images"][0].get("url", "") if data["main_images"] else ""
            
            # Extract garment type from metadata if available
            garment_type = "jewelry"
            if data.get("metadata") and isinstance(data.get("metadata"), dict):
                garment_type = data["metadata"].get("garment_type", "jewelry")
            
            return {
                "source": source,
                "source_product_id": str(data.get("product_id", "")),
                "product_url": data.get("product_url", ""),
                "brand": data.get("brand_id", "Unknown"),
                "model": data.get("product_url", "").split("/")[-1] if data.get("product_url") else "",
                "category": garment_type.capitalize() if garment_type else "Jewelry",
                "current_price": float(data.get("price", 0)),
                "currency": data.get("currency", "USD"),
                "condition": data.get("condition", "Unknown"),
                "image_url": image_url,
                "metadata": {
                    "garment_type": garment_type,
                    "description": data.get("metadata", {}).get("description", "") if isinstance(data.get("metadata"), dict) else "",
                    "size_dimensions": data.get("metadata", {}).get("size_dimensions", {}) if isinstance(data.get("metadata"), dict) else {},
                }
            }
        
        elif source == "grailed":
            # Extract main image URL from main_images array
            image_url = data.get("image_url", "")
            if not image_url and data.get("main_images") and isinstance(data.get("main_images"), list):
                image_url = data["main_images"][0].get("url", "") if data["main_images"] else ""
            
            # Extract metadata
            metadata_obj = data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {}
            
            return {
                "source": source,
                "source_product_id": data.get("product_url", "").split("/")[-1] if data.get("product_url") else str(hash(str(data))),
                "product_url": data.get("product_url", ""),
                "brand": data.get("brand", "Unknown"),
                "model": data.get("model", ""),
                "category": metadata_obj.get("style", "Street").capitalize(),
                "current_price": float(data.get("price", 0)),
                "currency": "USD",
                "condition": "Sold" if metadata_obj.get("is_sold") else "Available",
                "image_url": image_url,
                "metadata": {
                    "style": metadata_obj.get("style", ""),
                    "color": metadata_obj.get("color", ""),
                    "size": data.get("size", None),
                    "full_product_description": metadata_obj.get("full_product_description", ""),
                    "is_sold": metadata_obj.get("is_sold", False),
                }
            }
        
        return {}
    
    async def _upsert_product(
        self, product_data: Dict[str, Any], source: str
    ) -> tuple[bool, bool, bool]:
        """
        Upsert product: if exists → update; otherwise → create.
        Returns: (upserted, price_changed, event_created)
        """
        parsed = self._parse_product(product_data, source)
        if not parsed.get("product_url"):
            return False, False, False
        
        # Find existing product
        result = await self.db.execute(
            select(Product).where(Product.product_url == parsed["product_url"])
        )
        existing = result.scalars().first()
        
        price_changed = False
        event_created = False
        
        if existing:
            old_price = existing.current_price
            new_price = parsed["current_price"]
            
            # Update fields
            existing.current_price = new_price
            existing.metadata = parsed.get("metadata", {})
            existing.image_url = parsed.get("image_url")
            existing.updated_at = datetime.utcnow()
            
            # Check for price change
            if old_price != new_price:
                price_changed = True
                
                # Create price history entry
                history = PriceHistory(
                    product_id=existing.id,
                    old_price=old_price,
                    new_price=new_price,
                    source=source
                )
                self.db.add(history)
                
                # Create event
                event = Event(
                    product_id=existing.id,
                    event_type="price_change",
                    payload={
                        "old_price": old_price,
                        "new_price": new_price,
                        "source": source
                    }
                )
                self.db.add(event)
                event_created = True
            
            upserted = True
        else:
            # Create new product
            product = Product(**parsed)
            self.db.add(product)
            await self.db.flush()  # Flush to get the ID
            
            # Create initial event
            event = Event(
                product_id=product.id,
                event_type="product_created",
                payload={"source": source}
            )
            self.db.add(event)
            event_created = True
            upserted = True
        
        return upserted, price_changed, event_created
