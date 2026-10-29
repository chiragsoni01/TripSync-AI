import json
import uuid
from datetime import datetime
from pathlib import Path


# Store saved trips in the project directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_ROOT / "data"
STORAGE_FILE = STORAGE_DIR / "saved_trips.json"


def _ensure_storage():
    """Create the storage directory and JSON file if needed."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    if not STORAGE_FILE.exists():
        STORAGE_FILE.write_text(
            json.dumps([], indent=2),
            encoding="utf-8",
        )


def get_saved_trips():
    """Return all saved trips."""
    _ensure_storage()

    try:
        with STORAGE_FILE.open("r", encoding="utf-8") as file:
            trips = json.load(file)

        if not isinstance(trips, list):
            return []

        return trips

    except (json.JSONDecodeError, OSError):
        return []


def save_trip(plan, trip_name=None):
    """Save a trip plan and return its unique ID."""
    _ensure_storage()

    trips = get_saved_trips()
    trip_id = str(uuid.uuid4())

    trip = {
        "id": trip_id,
        "name": (
            trip_name.strip()
            if isinstance(trip_name, str) and trip_name.strip()
            else f"{plan.get('origin', 'Unknown')} to "
                 f"{plan.get('destination', 'Unknown')}"
        ),
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "plan": plan,
    }

    trips.append(trip)

    with STORAGE_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            trips,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    return trip_id


def load_trip(trip_id):
    """Return the saved trip matching the supplied ID."""
    for trip in get_saved_trips():
        if trip.get("id") == trip_id:
            return trip

    return None


def delete_trip(trip_id):
    """Delete a saved trip. Return True if one was removed."""
    trips = get_saved_trips()

    remaining_trips = [
        trip for trip in trips
        if trip.get("id") != trip_id
    ]

    if len(remaining_trips) == len(trips):
        return False

    _ensure_storage()

    with STORAGE_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            remaining_trips,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    return True