import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database import Base, engine


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "Clinical Document Intelligence Hub" in resp.json()["service"]


@pytest.mark.asyncio
async def test_list_documents_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/documents")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_patients_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/patients")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_search_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/search?q=")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
