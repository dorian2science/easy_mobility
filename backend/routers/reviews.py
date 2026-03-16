"""Reviews endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth import get_current_user_id
from backend.database import get_db
from backend.models import Booking, Review, Vehicle

router = APIRouter(tags=["reviews"])


class ReviewCreate(BaseModel):
    rating_vehicle: float
    rating_owner: float
    comment: str = ""
    booking_id: int | None = None


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
        "reviewer_name": r.reviewer.name if r.reviewer else None,
        "reviewer_avatar": r.reviewer.avatar_url if r.reviewer else None,
    }


@router.get("/vehicles/{vehicle_id}/reviews")
def list_vehicle_reviews(vehicle_id: int, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    reviews = (
        db.query(Review)
        .filter(Review.vehicle_id == vehicle_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return [_review_to_dict(r) for r in reviews]


@router.post("/vehicles/{vehicle_id}/reviews", status_code=201)
def create_vehicle_review(
    vehicle_id: int,
    payload: ReviewCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Verify completed booking if booking_id provided
    if payload.booking_id:
        booking = db.query(Booking).filter(
            Booking.id == payload.booking_id,
            Booking.renter_id == user_id,
            Booking.vehicle_id == vehicle_id,
            Booking.status == "completed",
        ).first()
        if not booking:
            raise HTTPException(status_code=403, detail="No completed booking found for this vehicle")
        reviewee_id = v.owner_id
    else:
        reviewee_id = v.owner_id

    if reviewee_id is None:
        raise HTTPException(status_code=400, detail="Vehicle has no registered owner")

    review = Review(
        vehicle_id=vehicle_id,
        reviewer_id=user_id,
        reviewee_id=reviewee_id,
        booking_id=payload.booking_id,
        rating_vehicle=payload.rating_vehicle,
        rating_owner=payload.rating_owner,
        comment=payload.comment,
        created_at=datetime.utcnow(),
    )
    db.add(review)
    db.flush()

    # Recalculate aggregate rating on vehicle
    agg = db.query(func.avg(Review.rating_vehicle), func.count(Review.id)).filter(
        Review.vehicle_id == vehicle_id
    ).first()
    v.rating = round(agg[0] or 0.0, 2)
    v.nb_reviews = agg[1]

    db.commit()
    db.refresh(review)
    return _review_to_dict(review)
