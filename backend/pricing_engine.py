"""
Pricing engine for Club de Mobilité Pierrefontaine.

Formula:
  PRICE = PRK × km + time_cost + optional_fuel + cartage_insurance + owner_margin (5%)

PRK is calibrated per vehicle category (A–E) and adjusted for:
  - Vehicle age (>6 years: +1.5%/yr)
  - Condition factor (excellent=0.92 … acceptable=1.22)

Owner margin is 5% of subtotal, with a bonus for comfort level.
Cartage/Omocom insurance is always at the renter's expense (~5 €/day).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Category parameters
# ---------------------------------------------------------------------------

CATEGORY_PARAMS: dict[str, dict] = {
    "A": {"prk": 0.38, "insurance_yr": 680, "depreciation_yr": 1312, "cartage_day": 5.00},
    "B": {"prk": 0.44, "insurance_yr": 820, "depreciation_yr": 2125, "cartage_day": 5.00},
    "C": {"prk": 0.52, "insurance_yr": 950, "depreciation_yr": 2800, "cartage_day": 5.00},
    "D": {"prk": 0.60, "insurance_yr": 1100, "depreciation_yr": 3500, "cartage_day": 5.50},
    "E": {"prk": 0.65, "insurance_yr": 1200, "depreciation_yr": 3800, "cartage_day": 6.50},
}

CONDITION_FACTOR: dict[str, float] = {
    "excellent": 0.92,
    "bon": 1.00,
    "correct": 1.10,
    "acceptable": 1.22,
}

COMFORT_FACTOR: dict[str, float] = {
    "basique": 0.80,
    "standard": 1.00,
    "confort": 1.20,
    "premium": 1.40,
}

OWNER_MARGIN_DEFAULT = 0.05
RATING_MIN_REVIEWS = 3
RATING_NEUTRAL = 4.0
MIN_BOOKING_HOURS_DEFAULT = 4
MAX_BOOKING_DAYS_DEFAULT = 7
FUEL_RETURN_MIN_PCT = 25
FUEL_PRICE_PER_LITER = 1.80   # €/L — approximate; for cost calculation when fuel is included


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class PriceResult:
    # Inputs (summary)
    category: str
    duration_hours: float
    distance_km: float
    include_fuel: bool
    fuel_type: str

    # Computed items
    prk_base: float
    age_factor: float
    condition_factor: float
    prk_adjusted: float
    km_cost: float
    time_cost: float
    fuel_cost: float
    cartage_days: int
    cartage_cost: float
    subtotal: float
    owner_margin_rate: float
    owner_margin: float
    comfort_factor: float
    total: float

    # Suggested floor/ceiling
    floor: float
    ceiling: float

    # Warnings
    warnings: list[str] = field(default_factory=list)

    def print_receipt(self) -> None:
        print("=" * 52)
        print("  DEVIS — Club de Mobilité Pierrefontaine")
        print("=" * 52)
        print(f"  Catégorie véhicule  : {self.category}")
        print(f"  Durée               : {self.duration_hours:.1f} h")
        print(f"  Distance            : {self.distance_km:.0f} km")
        print(f"  Carburant inclus    : {'Oui' if self.include_fuel else 'Non'}")
        print("-" * 52)
        print(f"  PRK de base         : {self.prk_base:.4f} €/km")
        print(f"  Facteur âge         : ×{self.age_factor:.4f}")
        print(f"  Facteur état        : ×{self.condition_factor:.4f}")
        print(f"  PRK ajusté          : {self.prk_adjusted:.4f} €/km")
        print("-" * 52)
        print(f"  Coût kilométrique   : {self.km_cost:.2f} €")
        print(f"  Coût temporel       : {self.time_cost:.2f} €")
        if self.include_fuel:
            print(f"  Carburant           : {self.fuel_cost:.2f} €")
        print(f"  Assurance cartage   : {self.cartage_cost:.2f} € ({self.cartage_days}j)")
        print(f"  Sous-total          : {self.subtotal:.2f} €")
        print(f"  Marge propriétaire  : {self.owner_margin:.2f} € ({self.owner_margin_rate*100:.0f}% × ×{self.comfort_factor:.2f} confort)")
        print("=" * 52)
        print(f"  TOTAL SUGGÉRÉ       : {self.total:.2f} €")
        print(f"  Plancher            : {self.floor:.2f} €")
        print(f"  Plafond             : {self.ceiling:.2f} €")
        if self.warnings:
            print("-" * 52)
            for w in self.warnings:
                print(f"  ⚠ {w}")
        print("=" * 52)

    def to_json(self) -> dict[str, Any]:
        return {
            "input": {
                "category": self.category,
                "duration_hours": self.duration_hours,
                "distance_km": self.distance_km,
                "include_fuel": self.include_fuel,
                "fuel_type": self.fuel_type,
            },
            "breakdown": {
                "prk_base": round(self.prk_base, 4),
                "age_factor": round(self.age_factor, 4),
                "condition_factor": round(self.condition_factor, 4),
                "prk_adjusted": round(self.prk_adjusted, 4),
                "km_cost": round(self.km_cost, 2),
                "time_cost": round(self.time_cost, 2),
                "fuel_cost": round(self.fuel_cost, 2),
                "cartage_days": self.cartage_days,
                "cartage_cost": round(self.cartage_cost, 2),
                "subtotal": round(self.subtotal, 2),
                "owner_margin_rate": round(self.owner_margin_rate, 4),
                "comfort_factor": round(self.comfort_factor, 4),
                "owner_margin": round(self.owner_margin, 2),
            },
            "result": {
                "total": round(self.total, 2),
                "floor": round(self.floor, 2),
                "ceiling": round(self.ceiling, 2),
            },
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def _age_factor(age_years: float) -> float:
    """Vehicles older than 6 years incur +1.5%/yr additional factor."""
    if age_years <= 6:
        return 1.0
    extra_years = age_years - 6
    return 1.0 + extra_years * 0.015


def _time_cost(category: str, duration_hours: float) -> float:
    """Hourly time cost derived from annual fixed costs (insurance + depreciation)."""
    params = CATEGORY_PARAMS[category]
    annual_fixed = params["insurance_yr"] + params["depreciation_yr"]
    hourly_rate = annual_fixed / (365 * 24)
    return hourly_rate * duration_hours


def _cartage_days(duration_hours: float) -> int:
    """Cartage is billed per started day (ceiling)."""
    import math
    return math.ceil(duration_hours / 24)


def price_from_dict(data: dict[str, Any]) -> PriceResult:
    """
    Main entry point. Takes a dict with keys: vehicle, owner, request.

    vehicle keys: category, condition, comfort, fuel_type, consumption_real,
                  age_years, annual_km_owner, include_fuel_default,
                  min_booking_hours, max_booking_days
    owner keys: nb_reviews, rating, owner_margin_override (optional)
    request keys: duration_hours, distance_km, include_fuel (optional, overrides default)
    """
    vehicle = data["vehicle"]
    owner = data.get("owner", {})
    request = data["request"]

    category = vehicle["category"]
    condition = vehicle.get("condition", "bon")
    comfort = vehicle.get("comfort", "standard")
    fuel_type = vehicle.get("fuel_type", "essence")
    consumption_real = vehicle.get("consumption_real", 7.0)
    age_years = float(vehicle.get("age_years", 0))
    min_booking_hours = float(vehicle.get("min_booking_hours", MIN_BOOKING_HOURS_DEFAULT))
    max_booking_days = float(vehicle.get("max_booking_days", MAX_BOOKING_DAYS_DEFAULT))
    include_fuel_default = vehicle.get("include_fuel_default", False)

    nb_reviews = int(owner.get("nb_reviews", 0))
    rating = float(owner.get("rating", 4.0))
    owner_margin_override = owner.get("owner_margin_override")

    duration_hours = float(request["duration_hours"])
    distance_km = float(request["distance_km"])
    include_fuel = bool(request.get("include_fuel", include_fuel_default))

    # --- Warnings ---
    warnings: list[str] = []
    if distance_km == 0:
        warnings.append("Distance nulle : vérifiez la demande.")
    if duration_hours < min_booking_hours:
        warnings.append(
            f"Durée {duration_hours:.1f}h inférieure au minimum ({min_booking_hours:.0f}h)."
        )
    if duration_hours > max_booking_days * 24:
        warnings.append(
            f"Durée {duration_hours/24:.1f}j dépasse le maximum ({max_booking_days:.0f}j)."
        )

    # --- Rating neutralization ---
    if nb_reviews < RATING_MIN_REVIEWS:
        rating = RATING_NEUTRAL

    # Rating bonus: above 4.0 gives small margin uplift (up to +10% at 5.0)
    rating_bonus = max(0.0, (rating - 4.0) / 10.0)  # 0 … 0.10

    # --- PRK calculation ---
    params = CATEGORY_PARAMS[category]
    prk_base = params["prk"]
    age_f = _age_factor(age_years)
    cond_f = CONDITION_FACTOR[condition]
    prk_adjusted = prk_base * age_f * cond_f

    # --- Cost items ---
    km_cost = prk_adjusted * distance_km
    time_cost = _time_cost(category, duration_hours)

    # Fuel cost — only for thermal vehicles
    if include_fuel and fuel_type not in ("electrique",):
        fuel_cost = (consumption_real / 100) * distance_km * FUEL_PRICE_PER_LITER
    else:
        fuel_cost = 0.0
        if include_fuel and fuel_type == "electrique":
            warnings.append("Véhicule électrique : pas de coût carburant inclus.")

    cartage_d = _cartage_days(duration_hours)
    cartage_cost = cartage_d * params["cartage_day"]

    subtotal = km_cost + time_cost + fuel_cost + cartage_cost

    # --- Owner margin ---
    comfort_f = COMFORT_FACTOR[comfort]
    base_margin_rate = owner_margin_override if owner_margin_override is not None else OWNER_MARGIN_DEFAULT
    effective_margin_rate = base_margin_rate * comfort_f * (1 + rating_bonus)
    owner_margin = subtotal * effective_margin_rate

    total = subtotal + owner_margin
    floor = subtotal * 0.90  # −10%
    ceiling = total * 1.30   # +30%

    return PriceResult(
        category=category,
        duration_hours=duration_hours,
        distance_km=distance_km,
        include_fuel=include_fuel,
        fuel_type=fuel_type,
        prk_base=prk_base,
        age_factor=age_f,
        condition_factor=cond_f,
        prk_adjusted=prk_adjusted,
        km_cost=km_cost,
        time_cost=time_cost,
        fuel_cost=fuel_cost,
        cartage_days=cartage_d,
        cartage_cost=cartage_cost,
        subtotal=subtotal,
        owner_margin_rate=effective_margin_rate,
        owner_margin=owner_margin,
        comfort_factor=comfort_f,
        total=total,
        floor=floor,
        ceiling=ceiling,
        warnings=warnings,
    )


def vehicle_from_json(path: str | Path) -> dict[str, Any]:
    """Load a vehicle JSON seed file and return a flat dict compatible with price_from_dict."""
    with open(path) as f:
        raw = json.load(f)

    v = raw["vehicle_info"]
    o = raw["owner"]
    s = raw["current_state"]
    p = raw["pricing_params"]

    return {
        "vehicle": {
            "category": v["category"],
            "fuel_type": v["fuel_type"],
            "consumption_real": v.get("consumption_real", 0),
            "condition": s["condition"],
            "comfort": s["comfort"],
            "age_years": p["age_years"],
            "annual_km_owner": p["annual_km_owner"],
            "include_fuel_default": p.get("include_fuel_default", False),
            "min_booking_hours": p.get("min_booking_hours", MIN_BOOKING_HOURS_DEFAULT),
            "max_booking_days": p.get("max_booking_days", MAX_BOOKING_DAYS_DEFAULT),
        },
        "owner": {
            "member_id": o["member_id"],
            "name": o["name"],
            "nb_reviews": o["nb_reviews"],
            "rating": o["rating"],
        },
    }
