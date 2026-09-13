"""Tests for authentication endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.security import hash_password
from app.schemas.user import UserRole

# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestRegistration:
    """Tests for user registration"""

    def test_register_success(self):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "SecurePass@123",
                "name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["name"] == "New User"
        assert data["role"] == "viewer"
        assert "password_hash" not in data

    def test_register_weak_password(self):
        """Test registration with weak password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@test.com",
                "password": "weak",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@test.com",
                "password": "SecurePass@123",
                "name": "First User",
            },
        )

        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@test.com",
                "password": "SecurePass@456",
                "name": "Second User",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"]

    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePass@123",
                "name": "Test User",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for user login"""

    def setup_method(self):
        """Create test user before each test"""
        db = TestingSessionLocal()
        user = User(
            email="testuser@test.com",
            password_hash=hash_password("TestPass@123"),
            name="Test User",
            role="analyst",
        )
        db.add(user)
        db.commit()
        db.close()

    def test_login_success(self):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@test.com",
                "password": "TestPass@123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self):
        """Test login with non-existent email"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "TestPass@123",
            },
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_invalid_password(self):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@test.com",
                "password": "WrongPass@123",
            },
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


class TestProtectedEndpoints:
    """Tests for protected endpoints"""

    def setup_method(self):
        """Create test user and get token before each test"""
        db = TestingSessionLocal()
        user = User(
            email="protectedtest@test.com",
            password_hash=hash_password("TestPass@123"),
            name="Protected Test User",
            role="analyst",
        )
        db.add(user)
        db.commit()
        db.close()

        # Login to get token
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "protectedtest@test.com",
                "password": "TestPass@123",
            },
        )
        self.token = response.json()["access_token"]

    def test_get_current_user_with_token(self):
        """Test getting current user with valid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "protectedtest@test.com"
        assert data["name"] == "Protected Test User"

    def test_get_current_user_without_token(self):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401


class TestTokenValidation:
    """Tests for token validation"""

    def test_token_includes_user_info(self):
        """Test that token contains user information"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "tokentest@test.com",
                "password": "TokenPass@123",
                "name": "Token Test",
            },
        )

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "tokentest@test.com",
                "password": "TokenPass@123",
            },
        )

        assert response.status_code == 200
        token = response.json()["access_token"]

        # Verify token can be used
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
