#!/usr/bin/env python3
"""Validate a vehicle JSON file against the vehicle schema."""

import json
import sys
from pathlib import Path

import jsonschema


def validate(json_path: str) -> bool:
    schema_path = Path(__file__).parent.parent / "backend" / "schemas" / "vehicle_schema.json"
    with open(schema_path) as f:
        schema = json.load(f)
    with open(json_path) as f:
        data = json.load(f)

    try:
        jsonschema.validate(instance=data, schema=schema)
        print(f"✓ {json_path} is valid")
        return True
    except jsonschema.ValidationError as e:
        print(f"✗ {json_path} is INVALID: {e.message}")
        print(f"  Path: {' → '.join(str(p) for p in e.absolute_path)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_vehicle_json.py <path/to/vehicle.json> [...]")
        sys.exit(1)

    all_valid = all(validate(p) for p in sys.argv[1:])
    sys.exit(0 if all_valid else 1)
