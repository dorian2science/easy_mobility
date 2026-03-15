"""Pricing engine tests — ≥10 test cases."""

import json
from pathlib import Path

import pytest

from backend.pricing_engine import (
    CATEGORY_PARAMS,
    price_from_dict,
    vehicle_from_json,
)

DATA_DIR = Path(__file__).parent.parent / "data" / "vehicles"


def _base_request(duration_hours=4.0, distance_km=60.0, include_fuel=False):
    return {"duration_hours": duration_hours, "distance_km": distance_km, "include_fuel": include_fuel}


def _vehicle(category="A", condition="bon", comfort="standard", fuel_type="essence",
             consumption_real=6.0, age_years=3, include_fuel_default=False,
             min_booking_hours=4, max_booking_days=7):
    return {
        "category": category, "condition": condition, "comfort": comfort,
        "fuel_type": fuel_type, "consumption_real": consumption_real,
        "age_years": age_years, "annual_km_owner": 12000,
        "include_fuel_default": include_fuel_default,
        "min_booking_hours": min_booking_hours, "max_booking_days": max_booking_days,
    }


def _owner(nb_reviews=5, rating=4.5):
    return {"nb_reviews": nb_reviews, "rating": rating}


# --- Test 1: Citadine 4h 60km no fuel — price in expected range ---
def test_citadine_short_no_fuel():
    result = price_from_dict({
        "vehicle": _vehicle("A"),
        "owner": _owner(),
        "request": _base_request(4.0, 60.0, False),
    })
    assert result.total > 0
    assert result.cartage_days == 1
    assert result.fuel_cost == 0.0
    assert result.floor <= result.total <= result.ceiling
    # Rough range: PRK=0.38 × 60 = 22.8 + time + cartage + margin, should be ~35–55€
    assert 20 < result.total < 80


# --- Test 2: SUV 7pl 48h 350km with fuel — cartage = 2 days ---
def test_suv7_48h_fuel():
    result = price_from_dict({
        "vehicle": _vehicle("D", comfort="confort", fuel_type="diesel",
                            consumption_real=7.0, include_fuel_default=True),
        "owner": _owner(nb_reviews=10, rating=4.8),
        "request": _base_request(48.0, 350.0, True),
    })
    assert result.cartage_days == 2
    assert result.cartage_cost == 2 * CATEGORY_PARAMS["D"]["cartage_day"]
    assert result.fuel_cost > 0
    assert result.total > 100


# --- Test 3: Owner with <3 reviews → rating neutralized to 4.0 ---
def test_rating_neutralized_below_3_reviews():
    # With 1 review, rating 2.0 should be neutralized to 4.0 → no negative margin
    result_low = price_from_dict({
        "vehicle": _vehicle("B"),
        "owner": {"nb_reviews": 1, "rating": 2.0},
        "request": _base_request(8.0, 100.0),
    })
    # Same vehicle, owner with 5 reviews and rating 4.0 (what the neutralized case becomes)
    result_neutral = price_from_dict({
        "vehicle": _vehicle("B"),
        "owner": {"nb_reviews": 5, "rating": 4.0},
        "request": _base_request(8.0, 100.0),
    })
    assert abs(result_low.total - result_neutral.total) < 0.01


# --- Test 4: distance = 0 → warning ---
def test_zero_distance_warning():
    result = price_from_dict({
        "vehicle": _vehicle("A"),
        "owner": _owner(),
        "request": _base_request(4.0, 0.0),
    })
    assert any("Distance nulle" in w for w in result.warnings)


# --- Test 5: duration < min_booking_hours → warning ---
def test_duration_below_minimum_warning():
    result = price_from_dict({
        "vehicle": _vehicle("A", min_booking_hours=4),
        "owner": _owner(),
        "request": _base_request(2.0, 30.0),
    })
    assert any("minimum" in w for w in result.warnings)


# --- Test 6: duration > max_booking_days → warning ---
def test_duration_above_maximum_warning():
    result = price_from_dict({
        "vehicle": _vehicle("A", max_booking_days=7),
        "owner": _owner(),
        "request": _base_request(8 * 24, 500.0),  # 8 days
    })
    assert any("maximum" in w for w in result.warnings)


# --- Test 7: Electric vehicle — no fuel cost, warning if include_fuel requested ---
def test_electric_vehicle_no_fuel_cost():
    result = price_from_dict({
        "vehicle": _vehicle("B", fuel_type="electrique", consumption_real=15.0),
        "owner": _owner(),
        "request": _base_request(6.0, 80.0, True),
    })
    assert result.fuel_cost == 0.0
    assert any("électrique" in w.lower() for w in result.warnings)


# --- Test 8: JSON round-trip consistency ---
def test_json_round_trip():
    data = {
        "vehicle": _vehicle("C"),
        "owner": _owner(),
        "request": _base_request(24.0, 200.0),
    }
    result = price_from_dict(data)
    j = result.to_json()
    assert j["result"]["total"] == round(result.total, 2)
    assert j["result"]["floor"] == round(result.floor, 2)
    assert j["result"]["ceiling"] == round(result.ceiling, 2)
    assert isinstance(j["warnings"], list)
    # Should be valid JSON-serializable
    json.dumps(j)


# --- Test 9: Age factor applies at >6 years ---
def test_age_factor_above_6_years():
    result_young = price_from_dict({
        "vehicle": _vehicle("A", age_years=3),
        "owner": _owner(),
        "request": _base_request(8.0, 100.0),
    })
    result_old = price_from_dict({
        "vehicle": _vehicle("A", age_years=10),
        "owner": _owner(),
        "request": _base_request(8.0, 100.0),
    })
    assert result_old.age_factor > result_young.age_factor
    assert result_old.age_factor == pytest.approx(1.0 + 4 * 0.015)
    assert result_young.age_factor == 1.0
    assert result_old.km_cost > result_young.km_cost


# --- Test 10: Condition "excellent" vs "acceptable" price difference ---
def test_condition_excellent_vs_acceptable():
    result_excellent = price_from_dict({
        "vehicle": _vehicle("B", condition="excellent"),
        "owner": _owner(),
        "request": _base_request(24.0, 200.0),
    })
    result_acceptable = price_from_dict({
        "vehicle": _vehicle("B", condition="acceptable"),
        "owner": _owner(),
        "request": _base_request(24.0, 200.0),
    })
    assert result_excellent.condition_factor == 0.92
    assert result_acceptable.condition_factor == 1.22
    assert result_acceptable.km_cost > result_excellent.km_cost
    diff = result_acceptable.total - result_excellent.total
    assert diff > 0


# --- Test 11: vehicle_from_json loads clio5 seed file correctly ---
def test_vehicle_from_json_clio5():
    path = DATA_DIR / "clio5_2022_dupont.json"
    d = vehicle_from_json(path)
    assert d["vehicle"]["category"] == "A"
    assert d["vehicle"]["fuel_type"] == "essence"
    assert d["owner"]["name"] == "Dupont"
    assert d["owner"]["nb_reviews"] == 7


# --- Test 12: vehicle_from_json all three seed files ---
@pytest.mark.parametrize("filename,expected_category", [
    ("clio5_2022_dupont.json", "A"),
    ("308sw_2021_martin.json", "B"),
    ("5008_2020_bernard.json", "D"),
])
def test_vehicle_from_json_all_seeds(filename, expected_category):
    d = vehicle_from_json(DATA_DIR / filename)
    assert d["vehicle"]["category"] == expected_category


# --- Test 13: print_receipt doesn't raise ---
def test_print_receipt(capsys):
    result = price_from_dict({
        "vehicle": _vehicle("A"),
        "owner": _owner(),
        "request": _base_request(4.0, 60.0),
    })
    result.print_receipt()
    captured = capsys.readouterr()
    assert "DEVIS" in captured.out
    assert "TOTAL" in captured.out
