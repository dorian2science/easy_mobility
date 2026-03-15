from datetime import date
from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Registration
    plate: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    vin: Mapped[str] = mapped_column(String(17), unique=True)
    ct_expiry: Mapped[date] = mapped_column(Date)
    insurance_expiry: Mapped[date] = mapped_column(Date)
    # Vehicle info
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(1))  # A–E
    fuel_type: Mapped[str] = mapped_column(String(30))
    consumption_real: Mapped[float] = mapped_column(Float, default=0.0)
    seats: Mapped[int] = mapped_column(Integer, default=5)
    transmission: Mapped[str] = mapped_column(String(20), default="manuelle")
    # Owner
    member_id: Mapped[str] = mapped_column(String(20))
    owner_name: Mapped[str] = mapped_column(String(100))
    nb_reviews: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=4.0)
    # Current state
    odometer_km: Mapped[int] = mapped_column(Integer, default=0)
    condition: Mapped[str] = mapped_column(String(20), default="bon")
    comfort: Mapped[str] = mapped_column(String(20), default="standard")
    fuel_level_pct: Mapped[int] = mapped_column(Integer, default=100)
    known_defects: Mapped[str] = mapped_column(Text, default="")
    # Pricing params
    age_years: Mapped[float] = mapped_column(Float, default=0.0)
    annual_km_owner: Mapped[int] = mapped_column(Integer, default=0)
    include_fuel_default: Mapped[bool] = mapped_column(Boolean, default=False)
    min_booking_hours: Mapped[float] = mapped_column(Float, default=4.0)
    max_booking_days: Mapped[float] = mapped_column(Float, default=7.0)
    # Availability
    available: Mapped[bool] = mapped_column(Boolean, default=True)

    maintenance_events: Mapped[list["MaintenanceEvent"]] = relationship(  # noqa: F821
        "MaintenanceEvent", back_populates="vehicle", cascade="all, delete-orphan"
    )
    quotes: Mapped[list["Quote"]] = relationship(  # noqa: F821
        "Quote", back_populates="vehicle", cascade="all, delete-orphan"
    )
