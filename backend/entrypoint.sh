#!/bin/sh
set -e
cd /app/backend
alembic upgrade head
cd /app
python scripts/seed_db.py
exec uvicorn backend.api:app --host 0.0.0.0 --port "${PORT:-8000}"
