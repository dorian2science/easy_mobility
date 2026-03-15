"""API integration tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.api import app, CLUB_API_KEY
from backend.database import Base, get_db
from backend.models import Vehicle

# --- In-memory SQLite for tests ---
TEST_DATABASE_URL = "sqlite:///./test_club_mobilite.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True, scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


HEADERS = {"X-Club-Key": CLUB_API_KEY}

VEHICLE_PAYLOAD = {
    "plate": "AB-123-CD",
    "vin": "VF15RBH0A67890123",
    "ct_expiry": "2026-11-15",
    "insurance_expiry": "2027-01-31",
    "make": "Renault",
    "model": "Clio 5",
    "year": 2022,
    "category": "A",
    "fuel_type": "essence",
    "consumption_real": 5.8,
    "seats": 5,
    "transmission": "manuelle",
    "member_id": "MBR-001",
    "owner_name": "Dupont",
    "nb_reviews": 7,
    "rating": 4.6,
    "odometer_km": 28500,
    "condition": "bon",
    "comfort": "standard",
    "fuel_level_pct": 80,
    "known_defects": "",
    "age_years": 4.0,
    "annual_km_owner": 12000,
    "include_fuel_default": False,
    "min_booking_hours": 4.0,
    "max_booking_days": 7.0,
    "available": True,
}


# --- Test 1: Health endpoint ---
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# --- Test 2: Auth required ---
def test_auth_required(client):
    r = client.get("/vehicles")
    assert r.status_code == 403


# --- Test 3: Auth with wrong key ---
def test_auth_wrong_key(client):
    r = client.get("/vehicles", headers={"X-Club-Key": "wrong-key"})
    assert r.status_code == 403


# --- Test 4: Create vehicle ---
def test_create_vehicle(client, db):
    # Clean up if leftover from previous test
    db.query(Vehicle).filter(Vehicle.plate == "AB-123-CD").delete()
    db.commit()

    r = client.post("/vehicles", json=VEHICLE_PAYLOAD, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["plate"] == "AB-123-CD"
    assert data["category"] == "A"
    assert "id" in data


# --- Test 5: List vehicles ---
def test_list_vehicles(client):
    r = client.get("/vehicles", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


# --- Test 6: Get single vehicle ---
def test_get_vehicle(client):
    r = client.get("/vehicles", headers=HEADERS)
    vehicle_id = r.json()[0]["id"]
    r2 = client.get(f"/vehicles/{vehicle_id}", headers=HEADERS)
    assert r2.status_code == 200
    assert r2.json()["id"] == vehicle_id


# --- Test 7: Get non-existent vehicle ---
def test_get_vehicle_404(client):
    r = client.get("/vehicles/99999", headers=HEADERS)
    assert r.status_code == 404


# --- Test 8: Update vehicle state ---
def test_update_vehicle_state(client):
    r = client.get("/vehicles", headers=HEADERS)
    vehicle_id = r.json()[0]["id"]
    r2 = client.put(
        f"/vehicles/{vehicle_id}/state",
        json={"odometer_km": 30000, "fuel_level_pct": 60, "available": True},
        headers=HEADERS,
    )
    assert r2.status_code == 200
    assert r2.json()["odometer_km"] == 30000
    assert r2.json()["fuel_level_pct"] == 60


# --- Test 9: Create quote ---
def test_create_quote(client):
    r = client.get("/vehicles", headers=HEADERS)
    vehicle_id = r.json()[0]["id"]
    r2 = client.post(
        "/quote",
        json={"vehicle_id": vehicle_id, "duration_hours": 8.0, "distance_km": 120.0, "include_fuel": False},
        headers=HEADERS,
    )
    assert r2.status_code == 200
    data = r2.json()
    assert "quote_id" in data
    assert "result" in data
    assert data["result"]["total"] > 0
    assert "breakdown" in data


# --- Test 10: Quote for non-existent vehicle ---
def test_quote_404(client):
    r = client.post(
        "/quote",
        json={"vehicle_id": 99999, "duration_hours": 4.0, "distance_km": 50.0},
        headers=HEADERS,
    )
    assert r.status_code == 404


# --- Test 11: Reference categories endpoint ---
def test_reference_categories(client):
    r = client.get("/reference/categories")
    assert r.status_code == 200
    data = r.json()
    assert "A" in data
    assert "E" in data
    assert "prk" in data["A"]


# --- Test 12: Reference parameters endpoint ---
def test_reference_parameters(client):
    r = client.get("/reference/parameters")
    assert r.status_code == 200
    data = r.json()
    assert "condition_factors" in data
    assert "comfort_factors" in data
    assert "owner_margin_default" in data
