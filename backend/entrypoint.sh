#!/bin/sh
set -e
cd /app
alembic -c backend/alembic.ini upgrade head
python scripts/seed_db.py
python scripts/seed_reviews.py
exec uvicorn backend.api:app --host 0.0.0.0 --port "${PORT:-8000}"
