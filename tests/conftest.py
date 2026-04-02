import pytest
import asyncio
import hashlib
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from app.main import app
from app.models.database import Base, get_db
from app.models.schemas import ApiKey, Source

# Setup test database (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
def test_db():
    """Create test database and tables"""
    async def setup_db():
        engine = create_async_engine(
            TEST_DATABASE_URL,
            connect_args={"timeout": 30},
            poolclass=StaticPool,
            echo=False,
        )
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Override the get_db dependency
        async def override_get_db():
            async with AsyncSession(engine) as session:
                yield session
        
        app.dependency_overrides[get_db] = override_get_db
        
        return engine
    
    engine = asyncio.run(setup_db())
    
    yield engine
    
    # Cleanup
    async def cleanup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
    
    asyncio.run(cleanup())

@pytest.fixture
def client(test_db):
    """Create test client"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def api_key(test_db):
    """Create test API key"""
    async def create_key():
        async with AsyncSession(test_db) as session:
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
            
            return test_key
    
    return asyncio.run(create_key())

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
