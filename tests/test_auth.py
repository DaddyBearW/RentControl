from RentControl.tests.conftest import register, auth

def test_register_and_me(client):
    token = register(client)
    response = client.get("/api/auth/me", headers=auth(token))
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["role"] == "customer"

def test_login_success(client):
    register(client)
    response = client.post("/api/auth/login", json={"email":"test@example.com","password":"password123"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client):
    register(client)
    response = client.post("/api/auth/login", json={"email":"test@example.com","password":"wrong-password"})
    assert response.status_code == 401

def test_duplicate_email(client):
    register(client)
    response = client.post("/api/auth/register", json={"email":"test@example.com","full_name":"Other User","password":"password123"})
    assert response.status_code == 409
