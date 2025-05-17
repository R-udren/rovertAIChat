from fastapi.testclient import TestClient

from src.main import app
from src.models.user import User

client = TestClient(app)


def test_get_me(test_user):
    """Test getting current user information"""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["user"].username
    assert data["email"] == test_user["user"].email
    assert data["id"] == str(test_user["user"].id)


def test_update_me(test_user):
    """Test updating current user information"""
    update_data = {"username": "updatedusername", "email": "updated@example.com"}

    response = client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json=update_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["email"] == update_data["email"]
    assert data["id"] == str(test_user["user"].id)


def test_get_users_as_admin(test_admin):
    """Test admin getting list of users"""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {test_admin['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_users_as_regular_user(test_user):
    """Test regular user trying to get list of users"""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_get_user_by_id(test_user, test_admin):
    """Test getting user by ID"""
    # Admin can access any user
    response = client.get(
        f"/api/users/{test_user['user'].id}",
        headers={"Authorization": f"Bearer {test_admin['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["user"].username

    # User can access their own info
    response = client.get(
        f"/api/users/{test_user['user'].id}",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["user"].username


def test_get_user_by_id_unauthorized(test_user, test_admin):
    """Test user trying to access another user's info"""
    response = client.get(
        f"/api/users/{test_admin['user'].id}",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_deactivate_user(test_user, test_admin, test_db):
    """Test admin deactivating a user"""
    response = client.delete(
        f"/api/users/{test_user['user'].id}",
        headers={"Authorization": f"Bearer {test_admin['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False

    # Verify in database
    updated_user = test_db.query(User).filter(User.id == test_user["user"].id).first()
    assert updated_user.is_active is False


def test_activate_user(test_user, test_admin, test_db):
    """Test admin activating a user"""
    # First deactivate the user
    test_user["user"].is_active = False
    test_db.commit()

    response = client.post(
        f"/api/users/{test_user['user'].id}/activate",
        headers={"Authorization": f"Bearer {test_admin['token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True

    # Verify in database
    updated_user = test_db.query(User).filter(User.id == test_user["user"].id).first()
    assert updated_user.is_active is True


def test_deactivate_user_unauthorized(test_user, test_admin):
    """Test regular user trying to deactivate another user"""
    response = client.delete(
        f"/api/users/{test_admin['user'].id}",
        headers={"Authorization": f"Bearer {test_user['token']}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
