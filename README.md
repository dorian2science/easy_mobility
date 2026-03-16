# 🚗 Club de Mobilité Pierrefontaine — Plateforme P2P

> **Mulhouse 2026** — Autopartage entre voisins, sans commission plateforme, prix transparents, assurance à l'usage.

---

## 🗂️ TABLE DES MATIÈRES

1. [Concept & Objectifs](#concept)
2. [Architecture du Projet](#architecture)
3. [Stack Technique](#stack)
4. [Tâches & Spécifications](#taches)
   - [T1 — Schéma JSON Véhicule (Vehicle Identity Card)](#t1)
   - [T2 — Moteur de Pricing (Pricing Engine)](#t2)
   - [T3 — API REST (Backend FastAPI)](#t3)
   - [T4 — Interface Web (Frontend)](#t4)
   - [T5 — Base de données (ORM SQLite → PostgreSQL)](#t5)
   - [T6 — Tests & CI/CD](#t6)
   - [T7 — Déploiement Production (Railway)](#t7)
5. [Modèle Financier de Référence](#modele-financier)
6. [Démarrage Rapide](#demarrage)
7. [Variables d'Environnement](#env)
8. [Roadmap](#roadmap)
9. [Règlement Club V1](#reglement)

---

## 1. Concept & Objectifs <a name="concept"></a>

Transformer le parc automobile statique de la Résidence Pierrefontaine en un réseau d'autopartage P2P :

- **Supprimer les commissions** des plateformes géantes (Turo ~30%, Getaround ~35%)
- **Redistribuer la valeur** entre voisins : le propriétaire gagne plus, l'emprunteur paye moins
- **Pricing transparent** basé sur le coût de revient réel (PRK grand rouleur + coûts fixes + Cartage)
- **Confiance automatisée** via assurance à l'usage (Cartage/Omocom ~5 €/jour)
- **Phase pilote** : 15 membres maximum, Mulhouse 2026

### Objectif tarifaire vs marché
| Véhicule | Club (grand rouleur) | Turo estimé | Économie |
|---|---|---|---|
| Citadine (Clio / 208) | ~19 €/j | ~38 €/j | **-50%** |
| Berline/Break (308 / Golf) | ~23 €/j | ~52 €/j | **-56%** |
| SUV 7pl (5008 / Sorento) | ~31 €/j | ~78 €/j | **-60%** |

---

## 2. Architecture du Projet <a name="architecture"></a>

```
club-mobilite-pierrefontaine/
│
├── backend/
│   ├── pricing_engine.py       # Moteur de calcul (PRK, coûts fixes, Cartage, marge)
│   ├── api.py                  # Endpoints FastAPI principaux + montage routers
│   ├── auth.py                 # JWT utilities (HS256, 7 jours)
│   ├── notifications.py        # WhatsApp via Twilio
│   ├── routers/
│   │   ├── auth.py             # /auth/google | /auth/register | /auth/login | /auth/me
│   │   ├── users.py            # /users/me | /users/me/stats
│   │   ├── reviews.py          # /vehicles/{id}/reviews
│   │   └── bookings.py         # /bookings CRUD + extension
│   ├── models/
│   │   ├── user.py             # User (OAuth + email/password, trust flags)
│   │   ├── vehicle.py          # Vehicle (+ photo_url, owner_id FK)
│   │   ├── maintenance_event.py
│   │   ├── quote.py            # Quote (+ renter_id FK)
│   │   ├── review.py           # Review (vehicle + owner ratings)
│   │   └── booking.py          # Booking (+ extension fields)
│   ├── alembic/versions/
│   │   ├── 0001_initial.py
│   │   └── 0002_users_reviews_bookings.py
│   ├── schemas/
│   │   └── vehicle_schema.json
│   ├── data/vehicles/          # 8 fiches JSON seed (catégories A–E)
│   ├── tests/
│   │   ├── test_pricing.py     # 15 tests
│   │   └── test_api.py         # 12 tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/src/
│   ├── context/AuthContext.jsx # JWT localStorage + login/logout
│   ├── hooks/useApi.js         # fetch wrapper avec Bearer token
│   ├── pages/
│   │   ├── Home.jsx            # Liste véhicules
│   │   ├── VehicleDetail.jsx   # Photo + état + historique + avis
│   │   ├── Quote.jsx           # Formulaire devis
│   │   ├── Login.jsx           # Email/password + Google OAuth
│   │   ├── Profile.jsx         # Dashboard membre
│   │   └── AddVehicle.jsx      # Ajout véhicule (auth-guarded)
│   └── components/
│       ├── VehicleCard.jsx     # Carte véhicule avec photo
│       ├── QuoteForm.jsx / PriceBreakdown.jsx
│       ├── ReviewCard.jsx / ReviewList.jsx / ReviewForm.jsx
│       ├── BookingHistoryTable.jsx / StatsDashboard.jsx
│       └── LoginButton.jsx
│
├── scripts/
│   ├── seed_db.py              # Charge véhicules + crée users propriétaires
│   └── seed_reviews.py         # 13 avis mock pour démo
│
├── monitoring/                 # docker-compose --profile monitoring
│   ├── prometheus.yml
│   ├── loki/loki-config.yaml
│   └── grafana/provisioning/   # Datasources + dashboard auto-provisionné
│
├── .github/workflows/ci.yml    # Tests + lint + deploy Railway
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 3. Stack Technique <a name="stack"></a>

| Couche | Technologie | Justification |
|---|---|---|
| **Backend** | Python 3.12 + FastAPI | Async, Pydantic natif, OpenAPI auto-généré |
| **Pricing Engine** | Python pur (dataclasses) | Lisible, testable, JSON-serialisable |
| **Auth** | JWT HS256 + Google OAuth + passlib bcrypt | Double chemin signup, tokens 7 jours |
| **ORM** | SQLAlchemy 2.x + Alembic | Migrations propres, compatible SQLite & PostgreSQL |
| **DB locale** | SQLite (dev) | Zéro config, fichier versionnable |
| **DB prod** | PostgreSQL (Railway) | Robustesse, Railway managed |
| **Frontend** | React 18 + Vite + TailwindCSS | Rapide à bootstrapper, composants clairs |
| **Notifications** | Twilio WhatsApp API | Extensions de réservation, alertes proprio |
| **Assurance** | Cartage/Omocom API | ~5 €/jour, substitution assurance P2P _(Phase 3)_ |
| **Paiement** | Stripe / Lydia / Revolut | Flux directs entre membres _(Phase 4)_ |
| **Monitoring** | Sentry + Prometheus + Loki + Grafana | Erreurs temps réel + métriques + logs |
| **CI/CD** | GitHub Actions | Tests + lint + deploy Railway sur push `main` |
| **Déploiement** | Railway.app | Free tier suffisant pour POC, PostgreSQL inclus |
| **Containerisation** | Docker + docker-compose | Reproductibilité locale et prod |

---

## 4. Tâches & Spécifications <a name="taches"></a>

---

### T1 — Schéma JSON Véhicule (Vehicle Identity Card) <a name="t1"></a>

**Objectif** : Définir le format de la "carte d'identité" d'un véhicule, stocké en JSON pour le seed data puis migré en DB.

#### Schéma de référence (`vehicle_schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VehicleIdentityCard",
  "description": "Fiche d'identité complète d'un véhicule inscrit au Club de Mobilité Pierrefontaine",
  "type": "object",
  "required": ["id", "owner", "registration", "vehicle_info", "current_state", "pricing_params"],
  "properties": {
    "id": {
      "type": "string",
      "description": "UUID v4 unique du véhicule dans le club",
      "example": "veh_a1b2c3d4-..."
    },
    "owner": {
      "type": "object",
      "required": ["name", "phone", "member_since"],
      "properties": {
        "name":           { "type": "string", "example": "Jean-Marie Dupont" },
        "phone":          { "type": "string", "example": "+33 6 12 34 56 78" },
        "email":          { "type": "string", "format": "email" },
        "member_since":   { "type": "string", "format": "date", "example": "2026-01-15" },
        "rating":         { "type": "number", "minimum": 0, "maximum": 5, "default": 4.0 },
        "nb_reviews":     { "type": "integer", "minimum": 0, "default": 0 },
        "nb_rentals":     { "type": "integer", "minimum": 0, "default": 0 }
      }
    },
    "registration": {
      "type": "object",
      "required": ["plate", "vin"],
      "properties": {
        "plate":       { "type": "string", "example": "AB-123-CD" },
        "vin":         { "type": "string", "description": "Numéro de série (17 caractères)" },
        "first_registration_date": { "type": "string", "format": "date" },
        "ct_valid_until": { "type": "string", "format": "date", "description": "Contrôle Technique valide jusqu'au" },
        "insurance_valid_until": { "type": "string", "format": "date" }
      }
    },
    "vehicle_info": {
      "type": "object",
      "required": ["make", "model", "year", "category", "fuel_type"],
      "properties": {
        "make":            { "type": "string", "example": "Peugeot" },
        "model":           { "type": "string", "example": "308 SW" },
        "year":            { "type": "integer", "minimum": 2000 },
        "color":           { "type": "string" },
        "category": {
          "type": "string",
          "enum": ["A", "B", "C", "D", "E"],
          "description": "A=Citadine | B=Berline/Break | C=SUV5pl | D=SUV7pl | E=Utilitaire"
        },
        "fuel_type": {
          "type": "string",
          "enum": ["essence", "diesel", "hybride", "electrique"]
        },
        "transmission":    { "type": "string", "enum": ["manuelle", "automatique"] },
        "seats":           { "type": "integer", "minimum": 2, "maximum": 9 },
        "consumption_real":{ "type": "number", "description": "L/100km ou kWh/100km mesuré réellement" },
        "photos":          { "type": "array", "items": { "type": "string", "format": "uri" } }
      }
    },
    "current_state": {
      "type": "object",
      "description": "État à la date snapshot_date — mis à jour après chaque location",
      "required": ["snapshot_date", "odometer_km", "condition", "fuel_level_pct"],
      "properties": {
        "snapshot_date":   { "type": "string", "format": "date-time" },
        "odometer_km":     { "type": "integer", "minimum": 0 },
        "fuel_level_pct":  { "type": "integer", "minimum": 0, "maximum": 100, "description": "Niveau carburant en %" },
        "condition": {
          "type": "string",
          "enum": ["excellent", "bon", "correct", "acceptable"],
          "description": "excellent=<50k entretien parfait | bon=standard | correct=>100k | acceptable=ancien"
        },
        "comfort": {
          "type": "string",
          "enum": ["basique", "standard", "confort", "premium"],
          "description": "basique=clim+vitres | standard=GPS+BT | confort=caméra+cuir | premium=full options"
        },
        "known_defects": {
          "type": "array",
          "description": "Défauts connus déclarés par le propriétaire (vice caché → responsabilité)",
          "items": { "type": "string" }
        },
        "maintenance_history": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "date":        { "type": "string", "format": "date" },
              "type":        { "type": "string", "description": "vidange | pneus | freins | courroie | autre" },
              "km_at_event": { "type": "integer" },
              "cost_eur":    { "type": "number" },
              "garage":      { "type": "string" },
              "notes":       { "type": "string" }
            }
          }
        }
      }
    },
    "pricing_params": {
      "type": "object",
      "description": "Paramètres de pricing propres à ce véhicule (overrides du moteur)",
      "properties": {
        "age_years":               { "type": "number", "description": "Âge réel (calculé auto depuis first_registration_date)" },
        "annual_km_owner":         { "type": "integer", "description": "Km/an du propriétaire hors locations" },
        "consumption_override":    { "type": ["number", "null"], "description": "Override conso réelle si connue" },
        "include_fuel_default":    { "type": "boolean", "default": false },
        "owner_notes":             { "type": "string", "description": "Conditions spéciales : animaux, fumeur, km max, etc." },
        "min_booking_hours":       { "type": "number", "default": 4, "description": "Durée min de réservation (règlement V1)" },
        "max_booking_days":        { "type": "number", "default": 7 }
      }
    },
    "availability": {
      "type": "object",
      "description": "Disponibilité déclarée par le propriétaire",
      "properties": {
        "available":           { "type": "boolean", "default": true },
        "unavailable_periods": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "from": { "type": "string", "format": "date" },
              "to":   { "type": "string", "format": "date" },
              "reason": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

#### Exemple de fiche véhicule réel (seed data)

```json
{
  "id": "veh_clio5-dupont-2026",
  "owner": {
    "name": "Jean-Marie Dupont",
    "phone": "+33 6 12 34 56 78",
    "member_since": "2026-01-15",
    "rating": 4.8,
    "nb_reviews": 3,
    "nb_rentals": 3
  },
  "registration": {
    "plate": "AB-123-CD",
    "vin": "VF1RFB00061234567",
    "first_registration_date": "2022-03-10",
    "ct_valid_until": "2026-03-10",
    "insurance_valid_until": "2026-12-31"
  },
  "vehicle_info": {
    "make": "Renault", "model": "Clio 5", "year": 2022,
    "color": "Gris Platine",
    "category": "A", "fuel_type": "essence",
    "transmission": "manuelle", "seats": 5,
    "consumption_real": 5.8
  },
  "current_state": {
    "snapshot_date": "2026-03-14T09:00:00Z",
    "odometer_km": 42500,
    "fuel_level_pct": 75,
    "condition": "bon",
    "comfort": "standard",
    "known_defects": ["Légère rayure pare-choc arrière gauche (photo ref. IMG_002)"],
    "maintenance_history": [
      { "date": "2025-11-20", "type": "vidange", "km_at_event": 38000, "cost_eur": 120, "garage": "Renault Mulhouse" }
    ]
  },
  "pricing_params": {
    "age_years": 4.0,
    "annual_km_owner": 8000,
    "consumption_override": null,
    "include_fuel_default": false,
    "owner_notes": "Pas d'animaux. Retour propre demandé. Km max/location : 300 km."
  },
  "availability": {
    "available": true,
    "unavailable_periods": [
      { "from": "2026-04-05", "to": "2026-04-12", "reason": "Vacances famille" }
    ]
  }
}
```

**Livrables T1 :**
- [ ] `backend/schemas/vehicle_schema.json` (JSON Schema validé)
- [ ] `backend/data/vehicles/` : ≥ 3 fiches exemples (citadine, berline, SUV)
- [ ] Script de validation : `python scripts/validate_vehicle_json.py <fichier>`

---

### T2 — Moteur de Pricing (Pricing Engine) <a name="t2"></a>

**Objectif** : À partir de la fiche JSON véhicule + paramètres de location, produire un breakdown de coûts complet, transparent et justifiable.


```
COÛT KILOMÉTRIQUE
  PRK = PRK_base[catégorie]
        × facteur_age (>6 ans : +1.5%/an)
        × facteur_condition [0.92 - 1.22]
  cout_km = PRK × km_estimés

COÛT TEMPS (immobilisation)
  taux_horaire = (assurance_annuelle + décote_annuelle) / 8760
  cout_temps = taux_horaire × heures_facturées

CARBURANT (optionnel, +10% si inclus par le proprio)
  cout_carburant = (conso/100) × km × prix_unité × 1.10

ASSURANCE CARTAGE (toujours à la charge de l'emprunteur)
  cout_cartage = tarif_cartage[catégorie] × jours_ceil(durée)

SOUS-TOTAL = cout_km + cout_temps + cout_carburant + cout_cartage

MARGE PROPRIO (5% du sous-total)
  marge = sous_total × 0.05
  bonus_confort = marge × (comfort_factor - 1)   [basique:0.8 → premium:1.4]
  bonus_réputation = marge × (rep_factor - 1)     [note 0-5, crédibilisé ≥3 avis]

PRIX SUGGÉRÉ = max(sous_total + marge + bonus, plancher_catégorie)
```

#### Paramètres calibrés (source : modèle Excel Club Pierrefontaine V2)

| Catégorie | PRK (€/km) | Assurance (€/an) | Décote moy (€/an) | Cartage (€/j) |
|---|---|---|---|---|
| A — Citadine | 0,38 | 680 | 1 312 | 5,00 |
| B — Berline/Break | 0,44 | 820 | 2 125 | 5,00 |
| C — SUV 5pl | 0,52 | 950 | 2 800 | 5,00 |
| D — SUV 7pl | 0,60 | 1 100 | 3 500 | 5,50 |
| E — Utilitaire | 0,65 | 1 200 | 3 800 | 6,50 |

> **Note** : PRK calibré grand rouleur (20 000 km/an) — un véhicule partagé roule davantage, ce qui abaisse le coût unitaire et rend les tarifs compétitifs.

#### Interface publique

```python
# Usage programmatique
from pricing_engine import price_from_dict

result = price_from_dict({
  "vehicle": { "category": "B", "fuel_type": "essence", "age_years": 3, ... },
  "owner":   { "name": "Ahmed B.", "rating": 4.6, "nb_reviews": 12 },
  "request": { "duration_hours": 8, "estimated_km": 120, "include_fuel": False }
})
result.print_receipt()  # Affiche le dévis formaté console
result.to_json()        # Retourne le JSON complet
```

#### Output (exemple réel — Berline 8h 120km)

```
══════════════════════════════════════════════════════════
  DEVIS LOCATION — Club de Mobilité Pierrefontaine
══════════════════════════════════════════════════════════
  Véhicule  : Peugeot 308 SW 2022
  Durée     : 8.0h facturées  ─  Distance : ~120 km
  ──────────────────────────────────────────────────────
  Usure km  (120 km × 0.44 €/km) .............. 15.80 €
  Temps     (8h × 0.336 €/h)   ................ 2.69 €
  Cartage   (1j × 5.00 €/j)    ................ 5.00 €
  ──────────────────────────────────────────────────────
  Sous-total coûts              .............. 22.49 €
  Marge proprio (5%)            ............... 2.02 €
  Prime réputation (×1.04)      ............... 0.12 €
══════════════════════════════════════════════════════════
  ⭐  PRIX SUGGÉRÉ  ......................  30.76 €
      Plancher minimum ...................  28.20 €
      Plafond raisonnable ................  35.27 €
  ──────────────────────────────────────────────────────
  → Proprio reçoit (hors Cartage) ......   25.76 €
  → Cartage/Omocom ......................    5.00 €
══════════════════════════════════════════════════════════
```

**Livrables T2 :**
- [ ] `backend/pricing_engine.py` — Moteur complet
- [ ] Ajouter chargement depuis fiche JSON véhicule (`vehicle_from_json()`)
- [ ] `backend/tests/test_pricing.py` — ≥ 10 cas de test couvrant tous les scénarios

---

### T3 — API REST (Backend FastAPI) <a name="t3"></a>

**Objectif** : Exposer le moteur de pricing via une API REST documentée (OpenAPI/Swagger).

#### Endpoints

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | Statut du service |
| `GET` | `/vehicles` | Liste des véhicules disponibles |
| `GET` | `/vehicles/{id}` | Détail d'un véhicule |
| `POST` | `/vehicles` | Ajouter un véhicule (admin) |
| `PUT` | `/vehicles/{id}/state` | Mettre à jour l'état (km, condition, dispo) |
| `POST` | `/quote` | **Calculer un devis** ← endpoint principal |
| `GET` | `/reference/categories` | Paramètres par catégorie |
| `GET` | `/reference/parameters` | Tous les paramètres du moteur |

#### Exemple appel `/quote`

```bash
curl -X POST http://localhost:8000/quote \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle": {"category": "B", "fuel_type": "essence", "age_years": 3,
                "condition": "bon", "comfort": "standard", "label": "308 SW 2022"},
    "owner":   {"name": "Ahmed B.", "rating": 4.6, "nb_reviews": 12},
    "request": {"duration_hours": 8, "estimated_km": 120, "include_fuel": false}
  }'
```

**Livrables T3 :**
- [ ] `backend/api.py` — API de base
- [ ] Endpoint `GET /vehicles` → lecture depuis DB
- [ ] Endpoint `POST /vehicles` → insertion en DB
- [ ] Middleware auth simple (clé API header `X-Club-Key`)
- [ ] Documentation Swagger auto sur `/docs`

---

### T4 — Interface Web (Frontend React) <a name="t4"></a>

**Objectif** : Interface simple pour sélectionner un véhicule et obtenir un devis instantané avec breakdown visible.

#### Composants principaux

**`VehicleCard`** — Carte d'un véhicule disponible
```
┌─────────────────────────────────────────┐
│  📷  [Photo véhicule]                   │
│  Peugeot 308 SW 2022 · Diesel           │
│  👤 Ahmed B.  ★ 4.6 (12 avis)          │
│  📍 Bât. B · Disponible                 │
│  [Calculer un devis →]                  │
└─────────────────────────────────────────┘
```

**`QuoteForm`** — Formulaire de devis
```
Durée estimée :  [4h ▼]   ou  [ __ ] heures
Km estimés :     [ 80  ] km
Carburant inclus : [☐] (le proprio inclut le plein, +10%)
[Calculer →]
```

**`PriceBreakdown`** — Résultat du devis
```
┌─────────────────────────────────────────┐
│  DEVIS — Peugeot 308 SW                 │
│  8h · 120 km · sans carburant           │
├─────────────────────────────────────────┤
│  Usure km   120 × 0,44 €    →   52,80 € │
│  Temps      8h × 0,34 €     →    2,69 € │
│  Cartage    1j × 5,00 €     →    5,00 € │
│  Marge      5%              →    3,02 € │
├─────────────────────────────────────────┤
│  ⭐ Prix suggéré             →  23,76 € │
│  Fourchette : 20,20 € – 27,27 €         │
└─────────────────────────────────────────┘
```

**Livrables T4 :**
- [ ] Bootstrapper projet : `npm create vite@latest frontend -- --template react`
- [ ] Configurer TailwindCSS
- [ ] `VehicleCard.jsx` — liste des véhicules depuis `GET /vehicles`
- [ ] `QuoteForm.jsx` — formulaire avec validation
- [ ] `PriceBreakdown.jsx` — affichage breakdown détaillé
- [ ] Responsive mobile-first (usage terrain depuis smartphone)

---

### T5 — Base de Données (ORM SQLAlchemy) <a name="t5"></a>

**Objectif** : Remplacer les JSON statiques par une DB proper, migrée proprement.

#### Schéma de tables

```sql
-- Véhicule
vehicles (
  id            TEXT PRIMARY KEY,      -- UUID
  owner_name    TEXT NOT NULL,
  owner_phone   TEXT,
  owner_rating  REAL DEFAULT 4.0,
  owner_reviews INTEGER DEFAULT 0,
  plate         TEXT UNIQUE NOT NULL,
  make          TEXT NOT NULL,
  model         TEXT NOT NULL,
  year          INTEGER,
  category      TEXT NOT NULL,         -- A/B/C/D/E
  fuel_type     TEXT NOT NULL,
  odometer_km   INTEGER,
  condition     TEXT DEFAULT 'bon',
  comfort       TEXT DEFAULT 'standard',
  available     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMP DEFAULT NOW(),
  updated_at    TIMESTAMP DEFAULT NOW()
)

-- Historique maintenance
maintenance_events (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id  TEXT REFERENCES vehicles(id),
  event_date  DATE,
  event_type  TEXT,
  km_at_event INTEGER,
  cost_eur    REAL,
  notes       TEXT
)

-- Devis générés (audit trail)
quotes (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id     TEXT REFERENCES vehicles(id),
  requested_at   TIMESTAMP DEFAULT NOW(),
  duration_hours REAL,
  estimated_km   INTEGER,
  include_fuel   BOOLEAN,
  prix_suggere   REAL,
  prix_minimum   REAL,
  breakdown_json TEXT   -- JSON complet du breakdown
)
```

**Livrables T5 :**
- [ ] `backend/models/` — modèles SQLAlchemy
- [ ] Migration Alembic initiale : `alembic upgrade head`
- [ ] Script de seed : `python scripts/seed_db.py` (charge les JSON de `data/vehicles/`)
- [ ] SQLite en dev, PostgreSQL en prod (variable `DATABASE_URL`)

---

### T6 — Tests & CI/CD <a name="t6"></a>

**Objectif** : Garantir la non-régression du moteur de pricing et automatiser le déploiement.

#### Tests

```bash
# Lancer tous les tests
pytest backend/tests/ -v --cov=backend --cov-report=term

# Tests pricing uniquement
pytest backend/tests/test_pricing.py -v
```

**Cas de test obligatoires :**
- Citadine 4h 60km sans carburant → prix dans fourchette attendue
- SUV 7pl 48h 350km avec carburant → vérifier décomposition Cartage (2 jours)
- Berline avec proprio < 3 avis → vérifier neutralisation note à 4.0
- Distance = 0 → warning attendu
- Durée < 4h → warning règlement V1
- Véhicule électrique sans recharge → suggestion explicite
- JSON round-trip → résultat identique input/output

#### Pipeline CI/CD (`.github/workflows/ci.yml`)

```yaml
name: CI/CD Club Mobilité

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v --cov=backend

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install ruff
      - run: ruff check backend/

  deploy:
    needs: [test, lint]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: club-mobilite-backend
```

**Livrables T6 :**
- [ ] `backend/tests/test_pricing.py` — ≥ 10 tests unitaires
- [ ] `backend/tests/test_api.py` — tests endpoints FastAPI (TestClient)
- [ ] `.github/workflows/ci.yml` — pipeline complet
- [ ] Badge CI dans le README

---

### T7 — Déploiement Production (Railway) <a name="t7"></a>

**Objectif** : Mettre en ligne le backend sur Railway (free tier suffisant pour POC).

#### Procédure

```bash
# 1. Installer Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialiser le projet
railway init --name club-mobilite-pierrefontaine

# 4. Ajouter PostgreSQL
railway add --plugin postgresql

# 5. Déployer
railway up

# 6. Obtenir l'URL publique
railway domain
```

#### Variables d'environnement production
```
DATABASE_URL=postgresql://...   # auto-injectée par Railway
CLUB_API_KEY=<secret>           # clé d'accès API admin
ENVIRONMENT=production
CORS_ORIGINS=https://club-mobilite.railway.app
```

**Livrables T7 :**
- [ ] `backend/Dockerfile` — image de production
- [ ] `railway.json` — config Railway
- [ ] Variables d'environnement documentées dans `.env.example`
- [ ] URL de prod fonctionnelle (Swagger accessible)

---

## 5. Modèle Financier de Référence <a name="modele-financier"></a>

> Source : `Club_Mobilite_Pierrefontaine_Model.xlsx` — calibré sur données marché France 2024-2026

### Coûts annuels par catégorie (grand rouleur 20 000 km/an)

| Poste | Citadine (Clio/208) | Berline (308/Golf) | SUV 7pl (5008) |
|---|---|---|---|
| Prix achat occasion 2-3 ans | 10 500 € | 17 000 € | 28 000 € |
| Décote annuelle moy. | 522 € | 846 € | 1 252 € |
| Assurance tous risques | 680 € | 820 € | 1 100 € |
| Entretien & révisions | 700 € | 850 € | 1 050 € |
| Majorations occasion | 200 € | 300 € | 450 € |
| Pneumatiques (proraté) | 160 € | 190 € | 263 € |
| Contrôle technique | 43 € | 43 € | 45 € |
| Carburant (20 000 km) | 2 111 € | 2 475 € | 3 094 € |
| **TOTAL annuel** | **4 416 €** | **5 523 €** | **7 255 €** |
| **PRK (€/km)** | **0,221** | **0,276** | **0,363** |
| **Coût/jour réel** | **22,1 €** | **27,6 €** | **36,3 €** |

### Tarifs recommandés vs marché

| Véhicule | Plancher club | Fourchette haute | Turo estimé | Getaround estimé |
|---|---|---|---|---|
| Citadine | 19 €/j | 26 €/j | 38 €/j | 35 €/j |
| Berline/Break | 23 €/j | 33 €/j | 52 €/j | 48 €/j |
| SUV 7 places | 31 €/j | 43 €/j | 78 €/j | 72 €/j |

**Économie emprunteur vs Turo : -50% à -60%.**

---

## 6. Démarrage Rapide <a name="demarrage"></a>

### Prérequis
- Python 3.12+
- Node.js 20+
- Docker (optionnel)
- Git

### Installation locale

```bash
# Cloner le repo
git clone https://github.com/<votre-org>/club-mobilite-pierrefontaine.git
cd club-mobilite-pierrefontaine

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Initialiser la base de données
alembic upgrade head
python scripts/seed_db.py   # Charge les véhicules de démonstration

# Lancer l'API
uvicorn api_v2:app --reload --port 8000
# → http://localhost:8000/docs (Swagger)

# Frontend (autre terminal)
cd ../frontend
npm install
npm run dev
# → http://localhost:5173
```

### Avec Docker Compose

```bash
docker-compose up --build
# Backend → http://localhost:8000
# Frontend → http://localhost:5173
```

### Tests

```bash
cd backend
pytest tests/ -v
```

---

## 7. Variables d'Environnement <a name="env"></a>

Copier `.env.example` en `.env` et renseigner :

```bash
# Backend
DATABASE_URL=sqlite:///./club_mobilite.db   # SQLite local
# DATABASE_URL=postgresql://user:pass@localhost/clubmobilite  # PostgreSQL prod
CLUB_API_KEY=dev-secret-key-change-in-prod
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173

# Cartage/Omocom (à renseigner quand accès API obtenu)
CARTAGE_API_KEY=
CARTAGE_API_URL=https://api.cartage.fr/v1

# Railway (CI/CD)
RAILWAY_TOKEN=    # Généré dans le dashboard Railway
```

---

## 8. Roadmap <a name="roadmap"></a>

### ✅ Phase 1 — POC Local (Sprint 0–1) _terminé_
- [x] Moteur de pricing + 13 tests unitaires
- [x] API FastAPI de base (CRUD véhicules, devis, référentiels)
- [x] Schéma JSON véhicule + 3 fiches seed (A, B, D)
- [x] ORM SQLAlchemy + Alembic migration 0001
- [x] Frontend React : liste véhicules + devis
- [x] Docker + docker-compose

### ✅ Phase 2 — CI/CD & Auth & Réservations (Sprints 2–5) _terminé_
- [x] GitHub Actions CI/CD + déploiement Railway
- [x] Auth : Google OAuth + email/password + JWT
- [x] 5 véhicules seed supplémentaires (catégories A–E avec photos)
- [x] Système d'avis (backend + composants React)
- [x] Page détail véhicule (photo, état, historique entretien)
- [x] Réservations : CRUD complet + machine à états
- [x] Extension de réservation + notifications WhatsApp (Twilio)
- [x] Dashboard profil utilisateur (stats, historique)
- [x] Sentry (erreurs) + Prometheus/Grafana (métriques)

### Phase 3 — Intégration métier _(à venir)_
- [ ] Intégration Cartage API (souscription assurance en ligne)
- [ ] États des lieux avec photos (avant/après location)
- [ ] Calendrier de disponibilité interactif
- [ ] Tests E2E (Playwright)

### Phase 4 — Scale _(à venir)_
- [ ] Paiement Stripe (split automatique proprio / Cartage)
- [ ] PWA / mode offline
- [ ] Extension à d'autres résidences

---

## 9. Règlement Club V1 <a name="reglement"></a>

Voir le document complet : `Cloud-Mobility-Pierrefontaine-V1.docx`

**Points clés pour le développement :**
- Durée minimum : **pas de minimum imposé** (V1 — à convenir entre membres)
- Durée maximum : **pas de maximum imposé** (V1)
- Assurance Cartage : **obligatoire, souscrite avant la prise des clés**
- Carburant retour : **jauge minimum 25%**, sinon refacturé à l'emprunteur
- État des lieux : **photos obligatoires départ ET retour** (4 faces + tableau de bord)
- Paiement : **direct entre membres** (virement, Lydia, Revolut, espèces + reçu)
- Vote d'admission : **majorité des 2/3**
- Phase pilote : **15 membres maximum**

> ⚠️ Le règlement V1 ne fixe pas de durée min/max — le moteur de pricing applique une alerte si durée < 4h (conservé de V1 initial) et > 7 jours (plafond pratique). Ces valeurs sont configurables dans `pricing_params.min_booking_hours` et `max_booking_days` de la fiche véhicule.

---

## Contribuer

```bash
git checkout -b feature/ma-fonctionnalite
# ... coder ...
git commit -m "feat: description claire"
git push origin feature/ma-fonctionnalite
# Ouvrir une Pull Request
```

Convention de commits : `feat:` / `fix:` / `test:` / `docs:` / `refactor:`

---

*Club de Mobilité Pierrefontaine · Mulhouse 2026 · Licence MIT*
