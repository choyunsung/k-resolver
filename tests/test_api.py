"""API endpoint tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.dns import DNSServer, ISP


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root HTML endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "K-Resolver" in response.text


@pytest.mark.asyncio
async def test_get_isps_empty(client: AsyncClient):
    """Test getting ISPs when database is empty."""
    response = await client.get("/api/isps")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_isps_with_data(client: AsyncClient, db_session: AsyncSession):
    """Test getting ISPs with data."""
    # Create test ISP
    isp = ISP(
        name="Test ISP",
        name_en="Test ISP EN",
        country="KR",
        isp_type="landline",
    )
    db_session.add(isp)
    await db_session.commit()
    await db_session.refresh(isp)

    # Create test DNS server
    dns_server = DNSServer(
        isp_id=isp.id,
        ip_address="8.8.8.8",
        priority=1,
        server_type="standard",
    )
    db_session.add(dns_server)
    await db_session.commit()

    # Test API
    response = await client.get("/api/isps")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test ISP"
    assert len(data[0]["dns_servers"]) == 1


@pytest.mark.asyncio
async def test_get_isp_not_found(client: AsyncClient):
    """Test getting non-existent ISP."""
    response = await client.get("/api/isps/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_resolve_domain(client: AsyncClient):
    """Test DNS resolution endpoint."""
    response = await client.post(
        "/api/resolve",
        json={
            "domain": "google.com",
            "dns_server": "8.8.8.8",
            "record_type": "A",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["domain"] == "google.com"
    assert data["dns_server"] == "8.8.8.8"
    assert "response_time_ms" in data


@pytest.mark.asyncio
async def test_get_command_examples(client: AsyncClient):
    """Test command examples endpoint."""
    response = await client.get(
        "/api/resolve/examples?domain=google.com&dns_server=8.8.8.8"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(ex["platform"] == "windows" for ex in data)
    assert any(ex["platform"] == "linux" for ex in data)
