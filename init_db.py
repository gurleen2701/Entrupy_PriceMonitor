import asyncio
from sqlalchemy import text
from app.models.database import engine, Base
from app.models.schemas import Source

async def init_db():
    """Initialize database with tables and seed data"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed sources table
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    SessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with SessionLocal() as session:
        # Check if sources already exist
        result = await session.execute(text("SELECT COUNT(*) FROM sources"))
        count = result.scalar()
        
        if count == 0:
            sources = [
                Source(
                    name="1stdibs",
                    base_url="https://www.1stdibs.com"
                ),
                Source(
                    name="fashionphile",
                    base_url="https://www.fashionphile.com"
                ),
                Source(
                    name="grailed",
                    base_url="https://www.grailed.com"
                ),
            ]
            
            for source in sources:
                session.add(source)
            
            await session.commit()
            print("✓ Seeded 3 marketplace sources")
        else:
            print(f"✓ Sources table already has {count} entries")

if __name__ == "__main__":
    asyncio.run(init_db())
