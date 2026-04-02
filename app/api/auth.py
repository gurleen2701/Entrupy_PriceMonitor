import hashlib
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import get_db
from app.models.schemas import ApiKey, ApiUsage

def hash_api_key(key: str) -> str:
    """Hash an API key using SHA256"""
    return hashlib.sha256(key.encode()).hexdigest()

async def verify_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> ApiKey:
    """Verify API key from X-API-Key header"""
    api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header"
        )
    
    # Hash the provided key and lookup in database
    key_hash = hash_api_key(api_key)
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True
        )
    )
    db_key = result.scalars().first()
    
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return db_key

async def log_api_usage(
    api_key: ApiKey,
    endpoint: str,
    method: str,
    status_code: int,
    db: AsyncSession
):
    """Log API usage to database"""
    usage = ApiUsage(
        api_key_id=api_key.id,
        endpoint=endpoint,
        method=method,
        status_code=status_code
    )
    db.add(usage)
    await db.commit()
