"""Booking CRUD + extension endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import get_current_user_id
from backend.database import get_db
from backend.models import Booking, User, Vehicle
from backend.notifications import send_whatsapp
from backend.pricing_engine import price_from_dict

router = APIRouter(prefix="/bookings", tags=["bookings"])


class BookingCreate(BaseModel):
    vehicle_id: int
    start_time: str  # ISO datetime
    end_time: str
    distance_km: float
    include_fuel: bool = False


class ExtensionRequest(BaseModel):
    new_end_time: str  # ISO datetime


class ExtensionRespond(BaseModel):
    accept: bool


def _booking_to_dict(b: Booking) -> dict:
    return {
        "id": b.id,
        "vehicle_id": b.vehicle_id,
        "renter_id": b.renter_id,
        "quote_id": b.quote_id,
        "start_time": b.start_time.isoformat(),
        "end_time": b.end_time.isoformat(),
        "status": b.status,
        "total_cost": b.total_cost,
        "extension_requested_end": b.extension_requested_end.isoformat() if b.extension_requested_end else None,
        "extension_status": b.extension_status,
        "extension_extra_cost": b.extension_extra_cost,
        "created_at": b.created_at.isoformat(),
        "updated_at": b.updated_at.isoformat(),
    }


def _check_overlap(db: Session, vehicle_id: int, start: datetime, end: datetime, exclude_id: int | None = None):
    q = db.query(Booking).filter(
        Booking.vehicle_id == vehicle_id,
        Booking.status.in_(["pending", "active"]),
        Booking.start_time < end,
        Booking.end_time > start,
    )
    if exclude_id:
        q = q.filter(Booking.id != exclude_id)
    return q.first()


def _compute_cost(v: Vehicle, start: datetime, end: datetime, distance_km: float, include_fuel: bool) -> float:
    duration_hours = (end - start).total_seconds() / 3600
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
        "owner": {"nb_reviews": v.nb_reviews, "rating": v.rating},
        "request": {
            "duration_hours": duration_hours,
            "distance_km": distance_km,
            "include_fuel": include_fuel,
        },
    }
    return price_from_dict(data).total


@router.post("", status_code=201)
def create_booking(
    payload: BookingCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    v = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if not v.available:
        raise HTTPException(status_code=409, detail="Vehicle is not available")

    start = datetime.fromisoformat(payload.start_time)
    end = datetime.fromisoformat(payload.end_time)
    if end <= start:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    if _check_overlap(db, v.id, start, end):
        raise HTTPException(status_code=409, detail="Vehicle already booked for this period")

    total = _compute_cost(v, start, end, payload.distance_km, payload.include_fuel)
    now = datetime.utcnow()
    booking = Booking(
        vehicle_id=v.id,
        renter_id=user_id,
        start_time=start,
        end_time=end,
        status="pending",
        total_cost=total,
        created_at=now,
        updated_at=now,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return _booking_to_dict(booking)


@router.get("/me")
def my_bookings(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.renter_id == user_id).order_by(Booking.created_at.desc()).all()
    return [_booking_to_dict(b) for b in bookings]


@router.get("/my-vehicles")
def my_vehicle_bookings(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bookings = (
        db.query(Booking)
        .join(Vehicle)
        .filter(Vehicle.owner_id == user_id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return [_booking_to_dict(b) for b in bookings]


@router.get("/{booking_id}")
def get_booking(
    booking_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Renter or vehicle owner can view
    v = db.query(Vehicle).filter(Vehicle.id == b.vehicle_id).first()
    if b.renter_id != user_id and (v is None or v.owner_id != user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return _booking_to_dict(b)


@router.put("/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    if b.renter_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if b.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending bookings can be cancelled")
    b.status = "cancelled"
    b.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(b)
    return _booking_to_dict(b)


@router.put("/{booking_id}/activate")
def activate_booking(
    booking_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    v = db.query(Vehicle).filter(Vehicle.id == b.vehicle_id).first()
    if v is None or v.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Only the vehicle owner can activate")
    if b.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending bookings can be activated")
    b.status = "active"
    b.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(b)
    return _booking_to_dict(b)


@router.put("/{booking_id}/complete")
def complete_booking(
    booking_id: int,
    new_odometer: int | None = None,
    new_fuel_level_pct: int | None = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    v = db.query(Vehicle).filter(Vehicle.id == b.vehicle_id).first()
    if v is None or v.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Only the vehicle owner can complete")
    if b.status != "active":
        raise HTTPException(status_code=409, detail="Only active bookings can be completed")

    b.status = "completed"
    b.updated_at = datetime.utcnow()

    if new_odometer is not None:
        v.odometer_km = new_odometer
    if new_fuel_level_pct is not None:
        v.fuel_level_pct = new_fuel_level_pct

    db.commit()
    db.refresh(b)
    return _booking_to_dict(b)


@router.post("/{booking_id}/extension")
def request_extension(
    booking_id: int,
    payload: ExtensionRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    if b.renter_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if b.status != "active":
        raise HTTPException(status_code=409, detail="Can only extend active bookings")

    new_end = datetime.fromisoformat(payload.new_end_time)
    if new_end <= b.end_time:
        raise HTTPException(status_code=400, detail="New end time must be after current end time")

    if _check_overlap(db, b.vehicle_id, b.end_time, new_end, exclude_id=b.id):
        raise HTTPException(status_code=409, detail="Extension period conflicts with another booking")

    b.extension_requested_end = new_end
    b.extension_status = "pending"
    b.updated_at = datetime.utcnow()
    db.commit()

    # Notify vehicle owner via WhatsApp
    v = db.query(Vehicle).filter(Vehicle.id == b.vehicle_id).first()
    renter = db.query(User).filter(User.id == user_id).first()
    if v and v.owner:
        owner_phone = v.owner.phone
        if owner_phone and v.owner.notif_whatsapp:
            msg = (
                f"Club Mobilité — Extension demandée\n"
                f"Véhicule : {v.make} {v.model} ({v.plate})\n"
                f"Locataire : {renter.name if renter else user_id}\n"
                f"Nouvelle fin souhaitée : {new_end.strftime('%d/%m/%Y %H:%M')}"
            )
            send_whatsapp(owner_phone, msg)

    db.refresh(b)
    return _booking_to_dict(b)


@router.put("/{booking_id}/extension/respond")
def respond_extension(
    booking_id: int,
    payload: ExtensionRespond,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    v = db.query(Vehicle).filter(Vehicle.id == b.vehicle_id).first()
    if v is None or v.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Only the vehicle owner can respond")
    if b.extension_status != "pending":
        raise HTTPException(status_code=409, detail="No pending extension request")

    if payload.accept:
        # Compute extra cost for the additional hours
        extra_cost = _compute_cost(
            v,
            b.end_time,
            b.extension_requested_end,
            distance_km=0,
            include_fuel=False,
        )
        b.end_time = b.extension_requested_end
        b.total_cost += extra_cost
        b.extension_status = "accepted"
        b.extension_extra_cost = extra_cost

        # Notify renter
        renter = db.query(User).filter(User.id == b.renter_id).first()
        if renter and renter.phone and renter.notif_whatsapp:
            msg = (
                f"Club Mobilité — Extension acceptée ✓\n"
                f"Véhicule : {v.make} {v.model}\n"
                f"Nouvelle fin : {b.end_time.strftime('%d/%m/%Y %H:%M')}\n"
                f"Coût supplémentaire : {extra_cost:.2f} €"
            )
            send_whatsapp(renter.phone, msg)
    else:
        b.extension_status = "rejected"

    b.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(b)
    return _booking_to_dict(b)
