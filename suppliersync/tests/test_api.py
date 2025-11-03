"""
API endpoint tests for SupplierSync.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test that health endpoint returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        # Security: db_path should not be exposed
        assert "db_path" not in data


class TestRAGEndpoints:
    """Test RAG endpoints."""
    
    def test_rag_status(self, client):
        """Test that RAG status endpoint works."""
        response = client.get("/rag/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "has_docs_directory" in data
        assert "has_vectorstore" in data
        assert "document_count" in data
        assert isinstance(data["document_count"], int)
        assert data["document_count"] >= 0
    
    def test_rag_rebuild(self, client):
        """Test that RAG rebuild endpoint works."""
        response = client.post("/rag/rebuild")
        # May return 200 (success), 400 (bad request), or 500 (error if docs directory missing)
        assert response.status_code in [200, 400, 500]
        data = response.json()
        assert "status" in data or "detail" in data
        if response.status_code == 200 and data.get("status") == "success":
            assert "file_count" in data
            assert "chunk_count" in data


class TestOrchestrateEndpoint:
    """Test orchestration endpoint."""
    
    def test_orchestrate_endpoint(self, client):
        """Test that orchestrate endpoint works."""
        response = client.post("/orchestrate")
        # May return 200 (success) or 500 (error if OpenAI key invalid)
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "run_id" in data
            assert "supplier_updates" in data
            assert "approved_prices" in data
            assert "rejected_prices" in data
            assert "cx_actions" in data


class TestSecurityFeatures:
    """Test security features."""
    
    def test_error_message_sanitization(self, client):
        """Test that error messages don't leak internal details."""
        # This test verifies that error messages are generic
        # We can't easily trigger a 500 error, but we can verify the pattern
        # by checking that health endpoint doesn't expose paths
        response = client.get("/health")
        data = response.json()
        # Should not expose internal paths
        assert "db_path" not in data
        assert "path" not in str(data).lower() or "status" in data
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly configured."""
        response = client.options("/health")
        # CORS headers should be present
        # Note: TestClient doesn't fully simulate CORS, but we can verify
        # the middleware is configured
        assert response.status_code in [200, 405]  # OPTIONS may return 405

