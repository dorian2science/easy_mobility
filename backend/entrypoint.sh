#!/bin/sh
set -e
export DATABASE_URL="${DATABASE_URL:-sqlite:////app/club_mobilite.db}"
cd /app/backend
alembic upgrade head
cd /app
python scripts/seed_db.py
python scripts/seed_reviews.py
exec uvicorn backend.api:app --host 0.0.0.0 --port "${PORT:-8000}"
