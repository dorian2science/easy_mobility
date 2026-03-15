from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class MaintenanceEvent(Base):
    __tablename__ = "maintenance_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    date: Mapped[date] = mapped_column(Date)
    type: Mapped[str] = mapped_column(String(50))
    km: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, default="")

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="maintenance_events")  # noqa: F821
