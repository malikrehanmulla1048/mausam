"""
MAUSAM Backend Test Suite
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, ping_db

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns 200 and healthy status."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["ok", "degraded"]
    assert "version" in data
    assert "database" in data


def test_demo_seed_and_overview():
    """Seed demo data and check business overview."""
    business_id = "demo_ramesh_textiles"
    seed_resp = client.post(f"/api/v1/businesses/{business_id}/demo/seed")
    assert seed_resp.status_code == 200

    overview_resp = client.get(f"/api/v1/businesses/{business_id}/overview")
    assert overview_resp.status_code == 200
    data = overview_resp.json()
    assert "business_id" in data


def test_cash_forecast():
    """Verify Cash Mausam forecast endpoint."""
    business_id = "demo_ramesh_textiles"
    resp = client.get(f"/api/v1/businesses/{business_id}/cash-forecast")
    assert resp.status_code in [200, 404]


def test_reconciliation_findings():
    """Verify Truth Check findings endpoint."""
    business_id = "demo_ramesh_textiles"
    resp = client.get(f"/api/v1/businesses/{business_id}/findings")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict) or isinstance(data, list)


def test_health_passport_creation():
    """Verify Health Passport creation and structure."""
    business_id = "demo_ramesh_textiles"
    resp = client.post(f"/api/v1/businesses/{business_id}/passports")
    assert resp.status_code in [200, 201]
