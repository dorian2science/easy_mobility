import json
import requests
import os
from pathlib import Path

# --- Configuration ---
BACKEND_URL = "http://localhost:8000/vehicles"
# Path to your specific file or folder
DATA_PATH = Path("backend/data/vehicles/")

HEADERS = {
    "x-club-key": "dev-secret-key-change-in-prod",
    "Content-Type": "application/json"
}

def flatten_vehicle_data(nested_data):
    """Maps the nested Mock JSON to the flat API structure."""
    # current_state can sometimes have empty defects
    defects = nested_data.get("current_state", {}).get("known_defects", [])
    defects_str = ", ".join(defects) if isinstance(defects, list) else defects

    return {
        **nested_data["registration"],
        **nested_data["vehicle_info"],
        "member_id": nested_data["owner"]["member_id"],
        "owner_name": nested_data["owner"]["name"],
        "nb_reviews": nested_data["owner"]["nb_reviews"],
        "rating": nested_data["owner"]["rating"],
        "odometer_km": nested_data["current_state"]["odometer_km"],
        "condition": nested_data["current_state"]["condition"],
        "comfort": nested_data["current_state"]["comfort"],
        "fuel_level_pct": nested_data["current_state"]["fuel_level_pct"],
        "known_defects": defects_str,
        "age_years": nested_data["pricing_params"]["age_years"],
        "annual_km_owner": nested_data["pricing_params"]["annual_km_owner"],
        "include_fuel_default": nested_data["pricing_params"]["include_fuel_default"],
        "min_booking_hours": nested_data["pricing_params"]["min_booking_hours"],
        "max_booking_days": nested_data["pricing_params"]["max_booking_days"],
        "available": nested_data.get("availability", {}).get("available", True)
    }

def upload_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        mock_data = json.load(f)
    
    payload = flatten_vehicle_data(mock_data)
    
    print(f"🚀 Uploading {payload['make']} {payload['model']} ({payload['plate']})...")
    response = requests.post(BACKEND_URL, json=payload, headers=HEADERS)
    
    if response.status_code in [200, 201]:
        print(f"✅ Success: Vehicle created with ID {response.json().get('id')}")
    elif response.status_code == 400:
        print(f"⚠️  Skip: Already exists or Bad Request ({response.text})")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    if DATA_PATH.is_file():
        upload_file(DATA_PATH)
    else:
        print(f"Looking for JSON files in {DATA_PATH}...")
        for json_file in DATA_PATH.glob("*.json"):
            upload_file(json_file)