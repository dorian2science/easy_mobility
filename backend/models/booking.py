from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    renter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quote_id: Mapped[int | None] = mapped_column(ForeignKey("quotes.id"), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    # status: pending / active / completed / cancelled
    status: Mapped[str] = mapped_column(String(20), default="pending")
    total_cost: Mapped[float] = mapped_column(Float)
    # Extension fields
    extension_requested_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    extension_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    extension_extra_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="bookings")  # noqa: F821
    renter: Mapped["User"] = relationship("User", back_populates="bookings", foreign_keys=[renter_id])  # noqa: F821
    quote: Mapped["Quote | None"] = relationship("Quote", back_populates="booking")  # noqa: F821
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="booking")  # noqa: F821
