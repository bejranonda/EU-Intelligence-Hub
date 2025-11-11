"""Tests for health check and basic API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "European News Intelligence Hub API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "operational"
    assert data["docs"] == "/docs"


def test_health_endpoint(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "environment" in data
    assert data["status"] in ["healthy", "degraded"]
    assert data["database"] in ["healthy", "unhealthy"]


def test_api_status_endpoint(client: TestClient):
    """Test API status endpoint."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "1.0.0"
    assert "features" in data
    features = data["features"]
    assert features["sentiment_analysis"] is True
    assert features["semantic_search"] is True
    assert features["news_scraping"] is True
    assert features["document_upload"] is True
    assert features["keyword_suggestions"] is True
    assert features["mind_map_visualization"] is True
