"""FastAPI application — Club de Mobilité Pierrefontaine."""

import json
import os
from datetime import datetime
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Quote, Vehicle
from backend.pricing_engine import CATEGORY_PARAMS, price_from_dict
from backend.routers import auth as auth_router
from backend.routers import bookings as bookings_router
from backend.routers import reviews as reviews_router
from backend.routers import users as users_router

CLUB_API_KEY = os.getenv("CLUB_API_KEY", "dev-secret-key-change-in-prod")

app = FastAPI(
    title="Club de Mobilité Pierrefontaine",
    description="P2P car-sharing API — transparent pricing, zero commission",
    version="2.0.0",
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sentry (optional — only if DSN is set)
_sentry_dsn = os.getenv("SENTRY_DSN", "")
if _sentry_dsn:
    import sentry_sdk
    sentry_sdk.init(dsn=_sentry_dsn, traces_sample_rate=0.1)

# Prometheus metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app)
except ImportError:
    pass

# Mount routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(reviews_router.router)
app.include_router(bookings_router.router)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def require_api_key(x_club_key: str = Header(default="")):
    if x_club_key != CLUB_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class VehicleCreate(BaseModel):
    plate: str
    vin: str
    ct_expiry: str
    insurance_expiry: str
    make: str
    model: str
    year: int
    category: str
    fuel_type: str
    consumption_real: float = 0.0
    seats: int = 5
    transmission: str = "manuelle"
    member_id: str = ""
    owner_name: str
    nb_reviews: int = 0
    rating: float = 4.0
    odometer_km: int = 0
    condition: str = "bon"
    comfort: str = "standard"
    fuel_level_pct: int = 100
    known_defects: str = ""
    age_years: float = 0.0
    annual_km_owner: int = 0
    include_fuel_default: bool = False
    min_booking_hours: float = 4.0
    max_booking_days: float = 7.0
    available: bool = True
    photo_url: str | None = None


class VehicleStateUpdate(BaseModel):
    odometer_km: int | None = None
    condition: str | None = None
    fuel_level_pct: int | None = None
    available: bool | None = None
    known_defects: str | None = None


class QuoteRequest(BaseModel):
    vehicle_id: int
    duration_hours: float
    distance_km: float
    include_fuel: bool = False


def _vehicle_to_dict(v: Vehicle, include_details: bool = False) -> dict:
    d = {
        "id": v.id,
        "plate": v.plate,
        "make": v.make,
        "model": v.model,
        "year": v.year,
        "category": v.category,
        "fuel_type": v.fuel_type,
        "owner_name": v.owner_name,
        "nb_reviews": len(v.reviews),
        "rating": round(sum(r.rating_vehicle for r in v.reviews) / len(v.reviews), 2) if v.reviews else v.rating,
        "odometer_km": v.odometer_km,
        "condition": v.condition,
        "comfort": v.comfort,
        "fuel_level_pct": v.fuel_level_pct,
        "known_defects": v.known_defects,
        "available": v.available,
        "age_years": v.age_years,
        "min_booking_hours": v.min_booking_hours,
        "max_booking_days": v.max_booking_days,
        "include_fuel_default": v.include_fuel_default,
        "photo_url": v.photo_url,
        "owner_id": v.owner_id,
        "ct_expiry": v.ct_expiry.isoformat() if v.ct_expiry else None,
        "insurance_expiry": v.insurance_expiry.isoformat() if v.insurance_expiry else None,
        "seats": v.seats,
        "transmission": v.transmission,
    }
    if include_details:
        d["maintenance_events"] = [
            {
                "id": m.id,
                "date": m.date.isoformat(),
                "type": m.type,
                "km": m.km,
                "description": m.description,
            }
            for m in sorted(v.maintenance_events, key=lambda x: x.date, reverse=True)
        ]
        d["reviews"] = [
            {
                "id": r.id,
                "rating_vehicle": r.rating_vehicle,
                "rating_owner": r.rating_owner,
                "comment": r.comment,
                "created_at": r.created_at.isoformat(),
                "reviewer_name": r.reviewer.name if r.reviewer else None,
            }
            for r in sorted(v.reviews, key=lambda x: x.created_at, reverse=True)
        ]
    return d


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/vehicles", dependencies=[Depends(require_api_key)])
def list_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).all()
    return [_vehicle_to_dict(v) for v in vehicles]


@app.get("/vehicles/{vehicle_id}", dependencies=[Depends(require_api_key)])
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return _vehicle_to_dict(v, include_details=True)


@app.post("/vehicles", status_code=201, dependencies=[Depends(require_api_key)])
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    from datetime import date
    v = Vehicle(
        plate=payload.plate,
        vin=payload.vin,
        ct_expiry=date.fromisoformat(payload.ct_expiry),
        insurance_expiry=date.fromisoformat(payload.insurance_expiry),
        make=payload.make,
        model=payload.model,
        year=payload.year,
        category=payload.category,
        fuel_type=payload.fuel_type,
        consumption_real=payload.consumption_real,
        seats=payload.seats,
        transmission=payload.transmission,
        member_id=payload.member_id,
        owner_name=payload.owner_name,
        nb_reviews=payload.nb_reviews,
        rating=payload.rating,
        odometer_km=payload.odometer_km,
        condition=payload.condition,
        comfort=payload.comfort,
        fuel_level_pct=payload.fuel_level_pct,
        known_defects=payload.known_defects,
        age_years=payload.age_years,
        annual_km_owner=payload.annual_km_owner,
        include_fuel_default=payload.include_fuel_default,
        min_booking_hours=payload.min_booking_hours,
        max_booking_days=payload.max_booking_days,
        available=payload.available,
        photo_url=payload.photo_url,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return _vehicle_to_dict(v)


@app.put("/vehicles/{vehicle_id}/state", dependencies=[Depends(require_api_key)])
def update_vehicle_state(vehicle_id: int, payload: VehicleStateUpdate, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if payload.odometer_km is not None:
        v.odometer_km = payload.odometer_km
    if payload.condition is not None:
        v.condition = payload.condition
    if payload.fuel_level_pct is not None:
        v.fuel_level_pct = payload.fuel_level_pct
    if payload.available is not None:
        v.available = payload.available
    if payload.known_defects is not None:
        v.known_defects = payload.known_defects
    db.commit()
    db.refresh(v)
    return _vehicle_to_dict(v)


@app.post("/quote", dependencies=[Depends(require_api_key)])
def create_quote(payload: QuoteRequest, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    data = {
        "vehicle": {
            "category": v.category,
            "condition": v.condition,
            "comfort": v.comfort,
            "fuel_type": v.fuel_type,
            "consumption_real": v.consumption_real,
            "age_years": v.age_years,
            "annual_km_owner": v.annual_km_owner,
            "include_fuel_default": v.include_fuel_default,
            "min_booking_hours": v.min_booking_hours,
            "max_booking_days": v.max_booking_days,
        },
        "owner": {
            "nb_reviews": v.nb_reviews,
            "rating": v.rating,
        },
        "request": {
            "duration_hours": payload.duration_hours,
            "distance_km": payload.distance_km,
            "include_fuel": payload.include_fuel,
        },
    }

    result = price_from_dict(data)
    breakdown = result.to_json()

    quote = Quote(
        vehicle_id=v.id,
        created_at=datetime.utcnow(),
        duration_hours=payload.duration_hours,
        distance_km=payload.distance_km,
        include_fuel=payload.include_fuel,
        total=result.total,
        breakdown_json=json.dumps(breakdown),
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)

    return {
        "quote_id": quote.id,
        "vehicle_id": v.id,
        "plate": v.plate,
        **breakdown,
    }


@app.get("/reference/categories")
def get_categories():
    return CATEGORY_PARAMS


@app.get("/reference/parameters")
def get_parameters():
    from backend.pricing_engine import (
        CONDITION_FACTOR, COMFORT_FACTOR, OWNER_MARGIN_DEFAULT,
        RATING_MIN_REVIEWS, RATING_NEUTRAL, MIN_BOOKING_HOURS_DEFAULT,
        MAX_BOOKING_DAYS_DEFAULT, FUEL_RETURN_MIN_PCT,
    )
    return {
        "condition_factors": CONDITION_FACTOR,
        "comfort_factors": COMFORT_FACTOR,
        "owner_margin_default": OWNER_MARGIN_DEFAULT,
        "rating_min_reviews": RATING_MIN_REVIEWS,
        "rating_neutral": RATING_NEUTRAL,
        "min_booking_hours_default": MIN_BOOKING_HOURS_DEFAULT,
        "max_booking_days_default": MAX_BOOKING_DAYS_DEFAULT,
        "fuel_return_min_pct": FUEL_RETURN_MIN_PCT,
    }
