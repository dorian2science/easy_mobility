from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    reviewee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    booking_id: Mapped[int | None] = mapped_column(ForeignKey("bookings.id"), nullable=True)
    rating_vehicle: Mapped[float] = mapped_column(Float)
    rating_owner: Mapped[float] = mapped_column(Float)
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="reviews")  # noqa: F821
    reviewer: Mapped["User"] = relationship("User", back_populates="reviews_given", foreign_keys=[reviewer_id])  # noqa: F821
    reviewee: Mapped["User"] = relationship("User", back_populates="reviews_received", foreign_keys=[reviewee_id])  # noqa: F821
    booking: Mapped["Booking | None"] = relationship("Booking", back_populates="reviews")  # noqa: F821
