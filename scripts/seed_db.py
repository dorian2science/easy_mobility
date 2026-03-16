#!/usr/bin/env python3
"""Seed the database from all vehicle JSON files in backend/data/vehicles/.

Also creates synthetic User rows for each owner (member_id → user) and
back-fills Vehicle.owner_id so the auth/booking system can work.
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal, engine
from backend.database import Base
from backend.models import MaintenanceEvent, User, Vehicle
from backend.pricing_engine import vehicle_from_json


# Synthetic email/phone mapping for seed owners (keyed by member_id)
OWNER_EXTRAS = {
    "MBR-001": {"email": "dupont@club-mobilite.test", "phone": "+33767944910"},
    "MBR-002": {"email": "martin@club-mobilite.test", "phone": None},
    "MBR-003": {"email": "bernard@club-mobilite.test", "phone": None},
    "MBR-004": {"email": "lefevre@club-mobilite.test", "phone": None},
    "MBR-005": {"email": "rousseau@club-mobilite.test", "phone": None},
    "MBR-006": {"email": "petit@club-mobilite.test", "phone": None},
    "MBR-007": {"email": "simon@club-mobilite.test", "phone": "+447934021694"},
    "MBR-008": {"email": "lambert@club-mobilite.test", "phone": None},
}


def _get_or_create_user(db, member_id: str, owner_name: str) -> User:
    extras = OWNER_EXTRAS.get(member_id, {})
    email = extras.get("email") or f"{member_id.lower()}@club-mobilite.test"
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(
        email=email,
        name=owner_name,
        phone=extras.get("phone"),
        notif_whatsapp=bool(extras.get("phone")),
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()
    return user


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    data_dir = Path(__file__).parent.parent / "backend" / "data" / "vehicles"

    for json_path in sorted(data_dir.glob("*.json")):
        with open(json_path) as f:
            raw = json.load(f)

        plate = raw["registration"]["plate"]
        existing = db.query(Vehicle).filter(Vehicle.plate == plate).first()
        if existing:
            # Back-fill owner_id if missing
            if existing.owner_id is None:
                o = raw["owner"]
                user = _get_or_create_user(db, o["member_id"], o["name"])
                existing.owner_id = user.id
                db.flush()
            print(f"  skip {plate} (already in DB)")
            continue

        reg = raw["registration"]
        vi = raw["vehicle_info"]
        o = raw["owner"]
        s = raw["current_state"]
        p = raw["pricing_params"]

        user = _get_or_create_user(db, o["member_id"], o["name"])

        photo_url = raw.get("photo_url")

        v = Vehicle(
            plate=reg["plate"],
            vin=reg["vin"],
            ct_expiry=date.fromisoformat(reg["ct_expiry"]),
            insurance_expiry=date.fromisoformat(reg["insurance_expiry"]),
            make=vi["make"],
            model=vi["model"],
            year=vi["year"],
            category=vi["category"],
            fuel_type=vi["fuel_type"],
            consumption_real=vi.get("consumption_real", 0.0),
            seats=vi.get("seats", 5),
            transmission=vi.get("transmission", "manuelle"),
            member_id=o["member_id"],
            owner_name=o["name"],
            nb_reviews=o["nb_reviews"],
            rating=o["rating"],
            odometer_km=s["odometer_km"],
            condition=s["condition"],
            comfort=s["comfort"],
            fuel_level_pct=s.get("fuel_level_pct", 100),
            known_defects="; ".join(s.get("known_defects", [])),
            age_years=p["age_years"],
            annual_km_owner=p["annual_km_owner"],
            include_fuel_default=p.get("include_fuel_default", False),
            min_booking_hours=p.get("min_booking_hours", 4.0),
            max_booking_days=p.get("max_booking_days", 7.0),
            available=raw["availability"]["available"],
            photo_url=photo_url,
            owner_id=user.id,
        )
        db.add(v)
        db.flush()  # get v.id

        for mh in s.get("maintenance_history", []):
            db.add(MaintenanceEvent(
                vehicle_id=v.id,
                date=date.fromisoformat(mh["date"]),
                type=mh["type"],
                km=mh["km"],
                description=mh.get("description", ""),
            ))

        print(f"  inserted {plate} ({vi['make']} {vi['model']}) — owner: {user.email}")

    db.commit()
    db.close()
    print("Seed complete.")


if __name__ == "__main__":
    seed()
