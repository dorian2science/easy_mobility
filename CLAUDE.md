# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Club de Mobilité Pierrefontaine** — A P2P car-sharing platform for the Pierrefontaine residential complex in Mulhouse, targeting a 2026 launch. The core value proposition: eliminate platform commissions (Turo ~30%, Getaround ~35%) and provide cost-transparent pricing based on the real cost-per-km (PRK) of each vehicle.

This repository is currently in **specification + early implementation phase**. The README is the primary architecture blueprint. 

---

## Development Commands

### Backend (Python 3.12 + FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

alembic upgrade head               # Initialize/migrate database
python scripts/seed_db.py         # Load demo vehicle JSON files

uvicorn api:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```

### Frontend (React 18 + Vite + TailwindCSS)

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

### Docker (full stack)

```bash
docker-compose up --build
```

### Tests & Lint

```bash
# All tests with coverage
pytest backend/tests/ -v --cov=backend --cov-report=term

# Pricing engine tests only
pytest backend/tests/test_pricing.py -v

# Lint
ruff check backend/
```

---

## Architecture

### Pricing Engine (`backend/pricing_engine.py`) — Core Logic

The central component. Takes a vehicle JSON + rental request and produces a transparent cost breakdown:

```
PRICE = PRK × km + time_cost + optional_fuel + cartage_insurance + owner_margin (5%)
```

- **PRK** (per-km cost) is calibrated per category and adjusted for vehicle age and condition.
- **Cartage/Omocom** (~5 €/day) is always at the renter's expense — it's the usage-based insurance.
- **Owner margin** is 5% of the subtotal, with bonuses for comfort level and reputation (owner rating ≥ 3 reviews).
- Price output includes: suggested price, floor, ceiling, and itemized receipt.

Public interface:
```python
from pricing_engine import price_from_dict
result = price_from_dict({"vehicle": {...}, "owner": {...}, "request": {...}})
result.print_receipt()  # formatted console output
result.to_json()        # full JSON breakdown
```

### Vehicle Categories & Calibrated Parameters

| Category | PRK (€/km) | Insurance (€/yr) | Depreciation (€/yr) | Cartage (€/day) |
|---|---|---|---|---|
| A — Citadine | 0.38 | 680 | 1 312 | 5.00 |
| B — Berline/Break | 0.44 | 820 | 2 125 | 5.00 |
| C — SUV 5pl | 0.52 | 950 | 2 800 | 5.00 |
| D — SUV 7pl | 0.60 | 1 100 | 3 500 | 5.50 |
| E — Utilitaire | 0.65 | 1 200 | 3 800 | 6.50 |

PRK is calibrated for 20,000 km/year (high-mileage driver) — shared vehicles naturally drive more, which lowers unit cost.

### Vehicle Identity Card (`backend/schemas/vehicle_schema.json`)

The canonical data model for each vehicle. Key fields:
- `registration`: plate, VIN, CT expiry, insurance expiry
- `vehicle_info`: make, model, year, `category` (A–E), fuel_type, consumption_real
- `current_state`: odometer_km, condition (`excellent/bon/correct/acceptable`), comfort (`basique/standard/confort/premium`), known_defects, maintenance_history
- `pricing_params`: age_years, annual_km_owner, include_fuel_default, min_booking_hours, max_booking_days
- `availability`: available boolean + unavailable_periods array

Seed data JSON files live in `backend/data/vehicles/`.

### REST API (`backend/api.py`)

Key endpoints:
- `POST /quote` — main endpoint, runs the pricing engine
- `GET /vehicles` / `POST /vehicles` — CRUD backed by DB
- `PUT /vehicles/{id}/state` — update km, condition, availability after a rental
- `GET /reference/categories` / `GET /reference/parameters` — engine parameters
- Auth: simple API key via `X-Club-Key` header

### Database (`backend/models/`)

SQLAlchemy 2.x + Alembic migrations. Three tables:
- `vehicles` — core vehicle data
- `maintenance_events` — service history log
- `quotes` — audit trail of generated quotes (stores full breakdown JSON)

SQLite in dev (`DATABASE_URL=sqlite:///./club_mobilite.db`), PostgreSQL on Railway in prod.

### Frontend (`frontend/src/`)

Three main components:
- `VehicleCard.jsx` — vehicle listing card with owner rating and availability
- `QuoteForm.jsx` — duration, km, fuel inclusion inputs
- `PriceBreakdown.jsx` — itemized cost breakdown display

Mobile-first (members use smartphones on-site).

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
DATABASE_URL=sqlite:///./club_mobilite.db
CLUB_API_KEY=dev-secret-key-change-in-prod
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173
CARTAGE_API_KEY=          # Required for Phase 3 insurance integration
CARTAGE_API_URL=https://api.cartage.fr/v1
RAILWAY_TOKEN=            # For CI/CD deployment
```

---

## Club Rules (relevant to code behavior)

- Cartage insurance is **mandatory** before key handover
- Fuel return: **minimum 25%** gauge — engine should flag if below
- Owner rating with **< 3 reviews** → neutralize to 4.0 (don't penalize new members)
- Pricing alerts: warn if rental duration < 4h or > 7 days (configurable per vehicle in `pricing_params`)
- Pilot limit: **15 members maximum**
- Payment: **direct P2P** — the platform takes 0% commission

---

## Implementation Status (Roadmap)

**Sprint :**
- `backend/pricing_engine.py` — full pricing engine
- `backend/api.py` — base FastAPI endpoints

**Sprint 1 remaining:**
- T1: Vehicle JSON schema + ≥3 seed files + validation script
- T2: `vehicle_from_json()` loader + ≥10 pricing tests
- T3: `/vehicles` CRUD connected to DB
- T5: SQLAlchemy models + Alembic migration + seed script
- T4: React frontend (VehicleCard, QuoteForm, PriceBreakdown)

**Sprint 2:**
- T6: Full test suite + `.github/workflows/ci.yml`
- T7: Railway deployment + Dockerfile + `railway.json`

---

## Commit Convention

```
feat: / fix: / test: / docs: / refactor:
```
