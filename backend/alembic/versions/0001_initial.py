"""Initial schema: vehicles, maintenance_events, quotes

Revision ID: 0001
Revises:
Create Date: 2026-03-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plate", sa.String(10), unique=True, nullable=False),
        sa.Column("vin", sa.String(17), unique=True, nullable=False),
        sa.Column("ct_expiry", sa.Date, nullable=False),
        sa.Column("insurance_expiry", sa.Date, nullable=False),
        sa.Column("make", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("category", sa.String(1), nullable=False),
        sa.Column("fuel_type", sa.String(30), nullable=False),
        sa.Column("consumption_real", sa.Float, default=0.0),
        sa.Column("seats", sa.Integer, default=5),
        sa.Column("transmission", sa.String(20), default="manuelle"),
        sa.Column("member_id", sa.String(20), nullable=False),
        sa.Column("owner_name", sa.String(100), nullable=False),
        sa.Column("nb_reviews", sa.Integer, default=0),
        sa.Column("rating", sa.Float, default=4.0),
        sa.Column("odometer_km", sa.Integer, default=0),
        sa.Column("condition", sa.String(20), default="bon"),
        sa.Column("comfort", sa.String(20), default="standard"),
        sa.Column("fuel_level_pct", sa.Integer, default=100),
        sa.Column("known_defects", sa.Text, default=""),
        sa.Column("age_years", sa.Float, default=0.0),
        sa.Column("annual_km_owner", sa.Integer, default=0),
        sa.Column("include_fuel_default", sa.Boolean, default=False),
        sa.Column("min_booking_hours", sa.Float, default=4.0),
        sa.Column("max_booking_days", sa.Float, default=7.0),
        sa.Column("available", sa.Boolean, default=True),
    )
    op.create_index("ix_vehicles_plate", "vehicles", ["plate"])
    op.create_index("ix_vehicles_id", "vehicles", ["id"])

    op.create_table(
        "maintenance_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("vehicle_id", sa.Integer, sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("km", sa.Integer, nullable=False),
        sa.Column("description", sa.Text, default=""),
    )
    op.create_index("ix_maintenance_events_id", "maintenance_events", ["id"])
    op.create_index("ix_maintenance_events_vehicle_id", "maintenance_events", ["vehicle_id"])

    op.create_table(
        "quotes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("vehicle_id", sa.Integer, sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("duration_hours", sa.Float, nullable=False),
        sa.Column("distance_km", sa.Float, nullable=False),
        sa.Column("include_fuel", sa.Boolean, default=False),
        sa.Column("total", sa.Float, nullable=False),
        sa.Column("breakdown_json", sa.Text, nullable=False),
    )
    op.create_index("ix_quotes_id", "quotes", ["id"])
    op.create_index("ix_quotes_vehicle_id", "quotes", ["vehicle_id"])


def downgrade() -> None:
    op.drop_table("quotes")
    op.drop_table("maintenance_events")
    op.drop_table("vehicles")
