"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_query_endpoint(self):
        """Test query endpoint."""
        request_data = {
            "question": "What were the revenues?",
            "company": "Apple",
            "year": 2024,
            "top_k": 3
        }
        
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "metrics" in data
    
    def test_query_invalid_request(self):
        """Test query with invalid data."""
        request_data = {
            "question": "Hi",  # Too short (min 5 chars)
            "year": 2050  # Out of range
        }
        
        response = client.post("/api/query", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_stats_endpoint(self):
        """Test statistics endpoint."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "collection_stats" in data
        assert "cost_summary" in data
    
    def test_example_queries_endpoint(self):
        """Test example queries endpoint."""
        response = client.get("/api/example-queries")
        assert response.status_code == 200
        
        data = response.json()
        assert "examples" in data
        assert len(data["examples"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
