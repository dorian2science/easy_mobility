"""User profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth import get_current_user_id
from backend.database import get_db
from backend.models import Booking, Review, User

router = APIRouter(prefix="/users", tags=["users"])


class UserUpdate(BaseModel):
    phone: str | None = None
    notif_whatsapp: bool | None = None
    notif_email: bool | None = None
    address_street: str | None = None
    address_city: str | None = None
    address_postal_code: str | None = None


@router.get("/me")
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_dict(user)


@router.put("/me")
def update_me(
    payload: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, val in payload.model_dump(exclude_none=True).items():
        setattr(user, field, val)

    db.commit()
    db.refresh(user)
    return _user_to_dict(user)


@router.get("/me/stats")
def get_my_stats(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    from backend.models import Vehicle

    earned = (
        db.query(func.sum(Booking.total_cost))
        .join(Vehicle)
        .filter(Vehicle.owner_id == user_id, Booking.status == "completed")
        .scalar()
        or 0.0
    )
    spent = (
        db.query(func.sum(Booking.total_cost))
        .filter(Booking.renter_id == user_id, Booking.status == "completed")
        .scalar()
        or 0.0
    )
    total_rentals = (
        db.query(func.count(Booking.id))
        .filter(Booking.renter_id == user_id, Booking.status == "completed")
        .scalar()
        or 0
    )
    avg_rating = (
        db.query(func.avg(Review.rating_owner))
        .filter(Review.reviewee_id == user_id)
        .scalar()
        or None
    )

    return {
        "earned_eur": round(earned, 2),
        "spent_eur": round(spent, 2),
        "total_rentals_as_renter": total_rentals,
        "avg_rating_as_owner": round(avg_rating, 2) if avg_rating else None,
    }


@router.get("/{user_id}/reviews")
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.reviewee_id == user_id).order_by(Review.created_at.desc()).all()
    return [_review_to_dict(r) for r in reviews]


def _user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "phone": user.phone,
        "notif_whatsapp": user.notif_whatsapp,
        "notif_email": user.notif_email,
        "address_street": user.address_street,
        "address_city": user.address_city,
        "address_postal_code": user.address_postal_code,
        "id_doc_verified": user.id_doc_verified,
        "driver_license_verified": user.driver_license_verified,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat(),
    }


def _review_to_dict(r: Review) -> dict:
    return {
        "id": r.id,
        "vehicle_id": r.vehicle_id,
        "reviewer_id": r.reviewer_id,
        "reviewee_id": r.reviewee_id,
        "booking_id": r.booking_id,
        "rating_vehicle": r.rating_vehicle,
        "rating_owner": r.rating_owner,
        "comment": r.comment,
        "created_at": r.created_at.isoformat(),
    }
