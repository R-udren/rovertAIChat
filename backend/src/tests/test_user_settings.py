import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.auth.jwt import create_access_token
from src.database import Base, get_db
from src.main import app
from src.models.user import User
from src.models.user_settings import UserSettings

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Set up test database with tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(setup_database):
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        id="12345678-1234-5678-1234-567812345678",
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role="user",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    # Create access token for the user
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )

    return {"user": user, "token": access_token}


@pytest.fixture
def test_admin(setup_database):
    """Create a test admin user"""
    db = TestingSessionLocal()
    admin = User(
        id="87654321-8765-4321-8765-432187654321",
        username="admin",
        email="admin@example.com",
        password_hash="hashed_password",
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()

    # Create access token for the admin
    access_token = create_access_token(
        data={"sub": str(admin.id), "username": admin.username, "role": admin.role}
    )

    return {"user": admin, "token": access_token}


def test_get_my_settings_not_found(test_user):
    """Test getting user settings when they don't exist yet"""
    response = client.get(
        "/api/user-settings/me",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user["user"].id)
    assert data["display_name"] == test_user["user"].username
    assert data["avatar_url"] is None
    assert data["preferences"] is None


def test_update_my_settings(test_user):
    """Test updating user settings"""
    settings_data = {
        "display_name": "Updated Name",
        "avatar_url": "https://example.com/avatar.jpg",
        "preferences": {"theme": "dark", "language": "en"},
    }

    response = client.put(
        "/api/user-settings/me",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json=settings_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user["user"].id)
    assert data["display_name"] == "Updated Name"
    assert data["avatar_url"] == "https://example.com/avatar.jpg"
    assert data["preferences"] == {"theme": "dark", "language": "en"}


def test_get_settings_by_id_as_admin(test_admin, test_user):
    """Test admin accessing other user's settings"""
    # First, create settings for the test user
    db = TestingSessionLocal()
    settings = UserSettings(
        user_id=test_user["user"].id,
        display_name="Test User",
        avatar_url="https://example.com/avatar.jpg",
    )
    db.add(settings)
    db.commit()
    db.close()

    # Now test admin accessing these settings
    response = client.get(
        f"/api/user-settings/{test_user['user'].id}",
        headers={"Authorization": f"Bearer {test_admin['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user["user"].id)
    assert data["display_name"] == "Test User"


def test_get_settings_by_id_unauthorized(test_user):
    """Test regular user trying to access another user's settings"""
    # Create another user ID
    other_user_id = "11111111-1111-1111-1111-111111111111"

    response = client.get(
        f"/api/user-settings/{other_user_id}",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_delete_settings_as_admin(test_admin, test_user):
    """Test admin deleting user settings"""
    # First, create settings for the test user
    db = TestingSessionLocal()
    settings = UserSettings(
        user_id=test_user["user"].id,
        display_name="Test User",
    )
    db.add(settings)
    db.commit()
    db.close()

    # Now test admin deleting these settings
    response = client.delete(
        f"/api/user-settings/{test_user['user'].id}",
        headers={"Authorization": f"Bearer {test_admin['token']}"},
    )

    assert response.status_code == 204

    # Verify settings are deleted
    db = TestingSessionLocal()
    settings = (
        db.query(UserSettings)
        .filter(UserSettings.user_id == test_user["user"].id)
        .first()
    )
    db.close()
    assert settings is None
