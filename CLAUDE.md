# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Rule for Claude:** After any implementation session that adds features, changes architecture, or modifies env vars — update this file (Implementation Status, API endpoints, env vars) **before** suggesting a commit. Do not wait to be asked.

---

## Project Overview

**Club de Mobilité Pierrefontaine** — A P2P car-sharing platform for the Pierrefontaine residential complex in Mulhouse, targeting a 2026 launch. The core value proposition: eliminate platform commissions (Turo ~30%, Getaround ~35%) and provide cost-transparent pricing based on the real cost-per-km (PRK) of each vehicle.

This repository is in **active development** — sprints 2–5 are implemented. The README is the primary architecture blueprint.

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

### REST API (`backend/api.py` + `backend/routers/`)

Key endpoints:
- `POST /quote` — runs the pricing engine
- `GET /vehicles` / `POST /vehicles` / `GET /vehicles/{id}` — CRUD backed by DB; detail includes maintenance_events + reviews
- `PUT /vehicles/{id}/state` — update km, condition, availability after a rental
- `GET /reference/categories` / `GET /reference/parameters` — engine parameters
- `POST /auth/google` / `POST /auth/register` / `POST /auth/login` — JWT auth
- `GET /users/me` / `PUT /users/me` / `GET /users/me/stats` — user profile
- `GET|POST /vehicles/{id}/reviews` — reviews
- `POST /bookings` / `GET /bookings/me` / `GET /bookings/my-vehicles` — bookings
- `PUT /bookings/{id}/cancel|activate|complete` — booking state machine
- `POST /bookings/{id}/extension` / `PUT /bookings/{id}/extension/respond` — extension + WhatsApp
- Auth: API key (`X-Club-Key`) for seed scripts/CI; JWT Bearer for user endpoints

### Database (`backend/models/`)

SQLAlchemy 2.x + Alembic migrations. Six tables:
- `users` — members (Google OAuth + email/password, trust flags)
- `vehicles` — core vehicle data (+ `photo_url`, `owner_id` FK)
- `maintenance_events` — service history log
- `quotes` — audit trail of generated quotes
- `bookings` — reservations with extension fields
- `reviews` — vehicle + owner ratings

SQLite in dev (`DATABASE_URL=sqlite:///./club_mobilite.db`), PostgreSQL on Railway in prod.

### Frontend (`frontend/src/`)

Pages: `Home`, `VehicleDetail`, `Quote`, `Login`, `Profile`, `AddVehicle`

Components: `VehicleCard`, `QuoteForm`, `PriceBreakdown`, `ReviewCard/List/Form`, `BookingHistoryTable`, `StatsDashboard`, `LoginButton`

Hooks/context: `AuthContext` (JWT in localStorage), `useApi` (auto-injects Bearer token)

Mobile-first (members use smartphones on-site).

---

## Environment Variables

Copy `.env.example` to `.env` (already in `.gitignore`):

```bash
DATABASE_URL=sqlite:///./club_mobilite.db
CLUB_API_KEY=dev-secret-key-change-in-prod
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173

# Auth
JWT_SECRET=<openssl rand -hex 32>
GOOGLE_CLIENT_ID=          # console.cloud.google.com
GOOGLE_CLIENT_SECRET=
VITE_GOOGLE_CLIENT_ID=     # same value — exposed to Vite frontend for the Google button

# WhatsApp (Twilio sandbox)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Monitoring (optional)
SENTRY_DSN=
VITE_SENTRY_DSN=

# CI/CD (GitHub Secret, not needed locally)
RAILWAY_TOKEN=
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

## Implementation Status

**Done — Sprint 0–1:**
- ✅ Pricing engine (`backend/pricing_engine.py`) + 13 tests
- ✅ FastAPI base API + 12 API tests
- ✅ SQLAlchemy models + Alembic migration 0001
- ✅ 3 seed vehicles (A, B, D) + seed script
- ✅ React frontend: Home + Quote + 3 components
- ✅ Docker + docker-compose + GitHub Actions CI + Railway deploy

**Done — Sprints 2–5 (2026-03-15):**
- ✅ DB: `users`, `reviews`, `bookings` tables — Alembic migration 0002
- ✅ Auth: Google OAuth + email/password — JWT HS256 7 days
- ✅ 5 new seed vehicles (all categories A–E) + `scripts/seed_reviews.py`
- ✅ Reviews system (backend + frontend components)
- ✅ Vehicle detail page with photo, maintenance timeline, reviews
- ✅ Booking CRUD + state machine (pending → active → completed)
- ✅ Booking extension + WhatsApp notifications (Twilio)
- ✅ User profile dashboard with stats + booking history tabs
- ✅ Add vehicle form (auth-guarded)
- ✅ Sentry (backend + frontend, opt-in via env var)
- ✅ Prometheus + Loki + Grafana monitoring stack (`--profile monitoring`)

**Done — Bug fixes (2026-03-15):**
- ✅ bcrypt 72-byte limit: password length validated before hashing + maxLength=72 on frontend
- ✅ Google OAuth button added to Login/Register page (`VITE_GOOGLE_CLIENT_ID` env var required)
- ✅ `nb_reviews` + `rating` now computed live from DB reviews (was stale JSON value)
- ✅ Plate conflict fixed: 308sw → PQ-789-RS, 5008 → TU-012-VW (were EF-456-GH / IJ-789-KL, clashing with new Yaris/Golf)
- ✅ All 8 vehicles have verified Wikimedia Commons CC-licensed car photos
- ✅ Docker: backend `restart: unless-stopped`, volume `/app/data` → `/app`, Promtail added

**Next:**
- Cartage API integration (Phase 3 insurance)
- E2E tests (Playwright)
- Payment flow (Stripe / Lydia)
- PWA / offline support

---

## Commit Convention

```
feat: / fix: / test: / docs: / refactor:
```
