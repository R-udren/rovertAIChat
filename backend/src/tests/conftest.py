import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.auth.jwt import create_access_token
from src.database import Base, get_db
from src.main import app
from src.models.user import User

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
def test_db():
    """Return a testing database session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


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
