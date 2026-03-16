from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    renter_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration_hours: Mapped[float] = mapped_column(Float)
    distance_km: Mapped[float] = mapped_column(Float)
    include_fuel: Mapped[bool] = mapped_column(Boolean, default=False)
    total: Mapped[float] = mapped_column(Float)
    breakdown_json: Mapped[str] = mapped_column(Text)  # full JSON from PriceResult.to_json()

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="quotes")  # noqa: F821
    renter: Mapped["User | None"] = relationship("User", foreign_keys=[renter_id])  # noqa: F821
    booking: Mapped["Booking | None"] = relationship("Booking", back_populates="quote")  # noqa: F821
