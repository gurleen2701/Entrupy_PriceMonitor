import pytest
import asyncio
import hashlib
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from app.main import app
from app.models.database import Base, get_db
from app.models.schemas import ApiKey, Source

# Setup test database (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_db():
    """Create test database and tables"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"timeout": 30},
        poolclass=StaticPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = pytest.fixtures.SessionLocal
    SessionLocal = pytest.fixtures.SessionLocal
    
    async def override_get_db():
        async with AsyncSession(engine) as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def client(test_db):
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def api_key(test_db):
    """Create test API key"""
    async with AsyncSession(engine=test_db) as session:
        # Create test key
        test_key = "test_api_key_12345"
        key_hash = hashlib.sha256(test_key.encode()).hexdigest()
        
        api_key = ApiKey(
            key=test_key,
            key_hash=key_hash,
            consumer_name="test_consumer",
            is_active=True
        )
        session.add(api_key)
        await session.commit()
        
        yield test_key

@pytest.fixture
async def setup_sources(test_db):
    """Setup marketplace sources"""
    async with AsyncSession(engine=test_db) as session:
        sources = [
            Source(name="1stdibs", base_url="https://www.1stdibs.com"),
            Source(name="fashionphile", base_url="https://www.fashionphile.com"),
            Source(name="grailed", base_url="https://www.grailed.com"),
        ]
        for source in sources:
            session.add(source)
        await session.commit()

# Import test modules
import sys
from pathlib import Path

# Add tests directory to path
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

# Run individual test files
pytest_plugins = [
    "conftest",
]
