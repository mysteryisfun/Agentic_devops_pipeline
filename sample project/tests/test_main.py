"""
Test cases for the Sample API
These tests verify the API endpoints work correctly
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import app
from src.database import db_manager


# Test client for synchronous tests
client = TestClient(app)


class TestAPI:
    """Test class for API endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_get_users_empty(self):
        """Test getting users when database is empty"""
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_user(self):
        """Test creating a new user"""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "age": 25,
            "city": "Test City",
            "password": "testpassword123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "id" in data
    
    def test_get_stats(self):
        """Test statistics endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "api_version" in data
        assert data["status"] == "operational"
    
    def test_invalid_user_data(self):
        """Test creating user with invalid data"""
        invalid_data = {
            "email": "not-an-email",  # Invalid email
            "name": "",  # Empty name
            "password": "123"  # Too short password
        }
        response = client.post("/users", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_nonexistent_user(self):
        """Test getting a user that doesn't exist"""
        response = client.get("/users/999999")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestAsyncAPI:
    """Async test class for database operations"""
    
    async def test_database_operations(self):
        """Test database operations work correctly"""
        # This test verifies that the database can be initialized
        await db_manager.init_database()
        
        # Count users should work
        count = await db_manager.count_users()
        assert isinstance(count, int)
        assert count >= 0


def test_application_startup():
    """Test that the application starts up correctly"""
    # This test ensures the FastAPI app can be imported and created
    assert app is not None
    assert hasattr(app, 'routes')
    assert len(app.routes) > 0


def test_imports():
    """Test that all modules can be imported correctly"""
    try:
        from src.main import app
        from src.models import User, UserCreate, UserUpdate
        from src.database import db_manager, init_db, get_db
        from src.config import settings
        assert True  # If we get here, all imports worked
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


if __name__ == "__main__":
    # Run tests if this file is executed directly
    pytest.main([__file__, "-v"])
