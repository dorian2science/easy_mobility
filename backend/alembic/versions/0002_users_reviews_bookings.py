"""Add users, reviews, bookings tables; add photo_url + owner_id to vehicles; add renter_id to quotes

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("google_sub", sa.String(100), unique=True, nullable=True),
        sa.Column("email", sa.String(200), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(200), nullable=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("address_street", sa.String(250), nullable=True),
        sa.Column("address_city", sa.String(100), nullable=True),
        sa.Column("address_postal_code", sa.String(20), nullable=True),
        sa.Column("id_doc_type", sa.String(20), nullable=True),
        sa.Column("id_doc_last4", sa.String(10), nullable=True),
        sa.Column("id_doc_verified", sa.Boolean, default=False),
        sa.Column("driver_license_number", sa.String(50), nullable=True),
        sa.Column("driver_license_expiry", sa.Date, nullable=True),
        sa.Column("driver_license_verified", sa.Boolean, default=False),
        sa.Column("notif_whatsapp", sa.Boolean, default=False),
        sa.Column("notif_email", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_admin", sa.Boolean, default=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"])

    # Add new columns to vehicles (no inline FK — SQLite doesn't enforce them; relationships handled by ORM)
    op.add_column("vehicles", sa.Column("photo_url", sa.String(500), nullable=True))
    op.add_column("vehicles", sa.Column("owner_id", sa.Integer, nullable=True))
    op.create_index("ix_vehicles_owner_id", "vehicles", ["owner_id"])

    # Add renter_id to quotes
    op.add_column("quotes", sa.Column("renter_id", sa.Integer, nullable=True))
    op.create_index("ix_quotes_renter_id", "quotes", ["renter_id"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("vehicle_id", sa.Integer, sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("renter_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("quote_id", sa.Integer, sa.ForeignKey("quotes.id"), nullable=True),
        sa.Column("start_time", sa.DateTime, nullable=False),
        sa.Column("end_time", sa.DateTime, nullable=False),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("total_cost", sa.Float, nullable=False),
        sa.Column("extension_requested_end", sa.DateTime, nullable=True),
        sa.Column("extension_status", sa.String(20), nullable=True),
        sa.Column("extension_extra_cost", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_bookings_id", "bookings", ["id"])
    op.create_index("ix_bookings_vehicle_id", "bookings", ["vehicle_id"])
    op.create_index("ix_bookings_renter_id", "bookings", ["renter_id"])

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("vehicle_id", sa.Integer, sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("reviewer_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewee_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("booking_id", sa.Integer, sa.ForeignKey("bookings.id"), nullable=True),
        sa.Column("rating_vehicle", sa.Float, nullable=False),
        sa.Column("rating_owner", sa.Float, nullable=False),
        sa.Column("comment", sa.Text, default=""),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_reviews_id", "reviews", ["id"])
    op.create_index("ix_reviews_vehicle_id", "reviews", ["vehicle_id"])
    op.create_index("ix_reviews_reviewer_id", "reviews", ["reviewer_id"])


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("bookings")
    op.drop_index("ix_quotes_renter_id", "quotes")
    op.drop_column("quotes", "renter_id")
    op.drop_index("ix_vehicles_owner_id", "vehicles")
    op.drop_column("vehicles", "owner_id")
    op.drop_column("vehicles", "photo_url")
    op.drop_table("users")
