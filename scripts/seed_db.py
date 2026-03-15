#!/usr/bin/env python3
"""Seed the database from all vehicle JSON files in backend/data/vehicles/."""

import json
import os
import sys
from datetime import date
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal, engine
from backend.database import Base
from backend.models import MaintenanceEvent, Vehicle
from backend.pricing_engine import vehicle_from_json


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
            print(f"  skip {plate} (already in DB)")
            continue

        reg = raw["registration"]
        vi = raw["vehicle_info"]
        o = raw["owner"]
        s = raw["current_state"]
        p = raw["pricing_params"]

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

        print(f"  inserted {plate} ({vi['make']} {vi['model']})")

    db.commit()
    db.close()
    print("Seed complete.")


if __name__ == "__main__":
    seed()
