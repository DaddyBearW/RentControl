from RentControl.tests.conftest import register, auth, promote

def test_catalog_requires_no_auth_and_returns_empty(client):
    response = client.get("/api/equipment")
    assert response.status_code == 200
    assert response.json() == []

def test_customer_cannot_create_equipment(client):
    token = register(client)
    response = client.post("/api/equipment", headers=auth(token), json={"name":"Drill","category":"Tools","daily_price":500,"quantity":2})
    assert response.status_code == 403

def test_manager_can_create_equipment(client):
    token = register(client)
    promote(client, role="manager")
    response = client.post("/api/equipment", headers=auth(token), json={"name":"Drill","category":"Tools","description":"Power drill","daily_price":500,"quantity":2})
    assert response.status_code == 201
    assert response.json()["name"] == "Drill"
