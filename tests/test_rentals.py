from datetime import date, timedelta
from RentControl.tests.conftest import register, auth, promote

def setup_equipment(client):
    token = register(client)
    promote(client, role="manager")
    client.post("/api/equipment", headers=auth(token), json={"name":"Camera","category":"Photo","daily_price":1000,"quantity":1})
    promote(client, role="customer")
    return token

def test_rental_price_is_calculated_inclusive_of_dates(client):
    token = setup_equipment(client)
    start = date.today() + timedelta(days=2)
    end = start + timedelta(days=2)
    response = client.post("/api/rentals", headers=auth(token), json={"equipment_id":1,"start_date":str(start),"end_date":str(end)})
    assert response.status_code == 201
    assert response.json()["total_price"] == 3000

def test_overlapping_rental_is_rejected_when_quantity_is_one(client):
    token = setup_equipment(client)
    start = date.today() + timedelta(days=3)
    end = start + timedelta(days=1)
    payload={"equipment_id":1,"start_date":str(start),"end_date":str(end)}
    assert client.post("/api/rentals", headers=auth(token), json=payload).status_code == 201
    assert client.post("/api/rentals", headers=auth(token), json=payload).status_code == 409

def test_end_date_before_start_date_is_rejected(client):
    token = setup_equipment(client)
    start = date.today() + timedelta(days=5)
    response = client.post("/api/rentals", headers=auth(token), json={"equipment_id":1,"start_date":str(start),"end_date":str(start-timedelta(days=1))})
    assert response.status_code == 400
