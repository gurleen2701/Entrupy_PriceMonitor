import hmac
import hashlib
import json
from typing import Optional
from datetime import datetime
import httpx
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schemas import Event, WebhookSubscription
from tenacity import retry, stop_after_attempt, wait_exponential

class NotificationService:
    """Service for handling webhook notifications and event delivery"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for webhook payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def deliver_webhooks(self, event_id: int):
        """
        Attempt to deliver event to all active webhook subscriptions.
        Retry up to 3 times with exponential backoff.
        """
        # Get event
        result = await self.db.execute(
            select(Event).where(Event.id == event_id)
        )
        event = result.scalars().first()
        
        if not event:
            return
        
        # Get active webhooks
        result = await self.db.execute(
            select(WebhookSubscription).where(
                WebhookSubscription.is_active == True
            )
        )
        webhooks = result.scalars().all()
        
        for webhook in webhooks:
            await self._attempt_delivery(event, webhook)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _attempt_delivery(self, event: Event, webhook: WebhookSubscription):
        """Attempt to deliver event to webhook with retries"""
        payload = json.dumps({
            "event_id": event.id,
            "event_type": event.event_type,
            "product_id": event.product_id,
            "payload": event.payload,
            "created_at": event.created_at.isoformat()
        })
        
        signature = self._generate_signature(payload, webhook.secret)
        
        headers = {
            "X-Webhook-Signature": f"sha256={signature}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    content=payload,
                    headers=headers
                )
                response.raise_for_status()
            
            # Mark as delivered
            event.delivered = True
            event.delivery_attempts += 1
            event.last_attempt_at = datetime.utcnow()
            await self.db.commit()
        
        except Exception as e:
            event.delivery_attempts += 1
            event.last_attempt_at = datetime.utcnow()
            await self.db.commit()
            raise e
    
    async def schedule_webhook_delivery(self, event_id: int):
        """Schedule webhook delivery as a background task (non-blocking)"""
        # This would typically be called via BackgroundTask in FastAPI
        await self.deliver_webhooks(event_id)
