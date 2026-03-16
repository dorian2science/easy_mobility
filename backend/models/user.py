from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Auth
    google_sub: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Identity
    name: Mapped[str] = mapped_column(String(150))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Address
    address_street: Mapped[str | None] = mapped_column(String(250), nullable=True)
    address_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address_postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # ID document (store type + last-4 only; full number must NOT be stored)
    id_doc_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    id_doc_last4: Mapped[str | None] = mapped_column(String(10), nullable=True)
    id_doc_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    # Driver licence
    driver_license_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    driver_license_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    driver_license_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    # Preferences
    notif_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False)
    notif_email: Mapped[bool] = mapped_column(Boolean, default=True)
    # Meta
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    vehicles: Mapped[list["Vehicle"]] = relationship(  # noqa: F821
        "Vehicle", back_populates="owner", foreign_keys="Vehicle.owner_id"
    )
    bookings: Mapped[list["Booking"]] = relationship(  # noqa: F821
        "Booking", back_populates="renter", foreign_keys="Booking.renter_id"
    )
    reviews_given: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review", back_populates="reviewer", foreign_keys="Review.reviewer_id"
    )
    reviews_received: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review", back_populates="reviewee", foreign_keys="Review.reviewee_id"
    )
