import json
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from orchestrator.planner import (
    create_trip_plan,
    create_travel_strategies,
)


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

app = FastAPI(
    title="TripSync AI API",
    description="AI-powered multi-agent travel planning API.",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "tripsync.db"


def get_connection():
    """Create a connection to the local SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def initialize_database():
    """Create the saved trips table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                origin TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                travelers INTEGER NOT NULL,
                budget REAL NOT NULL,
                estimated_total REAL NOT NULL,
                trip_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


initialize_database()


# ==========================================
# REQUEST MODELS
# ==========================================

class TripRequest(BaseModel):
    origin: str = Field(default="Delhi", min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    travelers: int = Field(ge=1, le=6)
    budget: float = Field(gt=0, le=100000000)


class SaveTripRequest(BaseModel):
    trip: dict
    budget: float = Field(gt=0, le=100000000)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def make_json_safe(value):
    """Convert dates and nested objects into JSON-compatible values."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    return value


def row_to_trip(row):
    """Convert a database row into an API response."""
    trip = json.loads(row["trip_json"])

    trip["id"] = row["id"]
    trip["saved_at"] = row["created_at"]
    trip["saved_budget"] = row["budget"]

    return trip


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/api/health")
def health_check():
    return {
        "status": "success",
        "message": "TripSync AI API is running!",
        "database": "connected",
    }


# ==========================================
# GENERATE TRIP PLAN
# ==========================================

@app.post("/api/plan-trip")
def plan_trip(request: TripRequest):
    if request.end_date <= request.start_date:
        raise HTTPException(
            status_code=400,
            detail="Return date must be after the departure date.",
        )

    try:
        trip_plan = create_trip_plan(
            origin=request.origin.strip() or "Delhi",
            destination=request.destination.strip(),
            start_date=request.start_date,
            end_date=request.end_date,
            travelers=request.travelers,
            budget=request.budget,
        )

        safe_trip = make_json_safe(trip_plan)

        return {
            "status": "success",
            "trip": safe_trip,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Trip planning failed. Check the VS Code terminal "
                "for the underlying error."
            ),
        )


# ==========================================
# HYBRID AI TRAVEL DECISION ENGINE
# ==========================================

@app.post("/api/travel-strategies")
def generate_travel_strategies(request: TripRequest):
    """Generate three independent travel-budget strategies."""

    if request.end_date <= request.start_date:
        raise HTTPException(
            status_code=400,
            detail="Return date must be after the departure date.",
        )

    try:
        strategies = create_travel_strategies(
            origin=request.origin.strip() or "Delhi",
            destination=request.destination.strip(),
            start_date=request.start_date,
            end_date=request.end_date,
            travelers=request.travelers,
            budget=request.budget,
        )

        return {
            "status": "success",
            "data": make_json_safe(strategies),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Travel strategy generation failed. "
                "Check the VS Code terminal for the underlying error."
            ),
        )


# ==========================================
# SAVE A GENERATED TRIP
# ==========================================

@app.post("/api/trips")
def save_trip(request: SaveTripRequest):
    trip = make_json_safe(request.trip)

    required_fields = [
        "origin",
        "destination",
        "start_date",
        "end_date",
        "travelers",
    ]

    for field in required_fields:
        if field not in trip:
            raise HTTPException(
                status_code=400,
                detail=f"Trip data is missing the '{field}' field.",
            )

    try:
        start_date = date.fromisoformat(str(trip["start_date"]))
        end_date = date.fromisoformat(str(trip["end_date"]))

        if end_date <= start_date:
            raise HTTPException(
                status_code=400,
                detail="Return date must be after the departure date.",
            )

        destination = str(trip["destination"]).strip()
        origin = str(trip["origin"]).strip() or "Delhi"
        travelers = int(trip["travelers"])

        if not destination:
            raise HTTPException(
                status_code=400,
                detail="Destination cannot be empty.",
            )

        if not 1 <= travelers <= 6:
            raise HTTPException(
                status_code=400,
                detail="Travelers must be between 1 and 6.",
            )

        budget_report = trip.get("budget_report") or {}
        estimated_total = float(
            budget_report.get("estimated_total", 0)
        )

        if estimated_total < 0:
            raise HTTPException(
                status_code=400,
                detail="Estimated trip cost cannot be negative.",
            )

        created_at = datetime.now(timezone.utc).isoformat()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO saved_trips (
                    destination,
                    origin,
                    start_date,
                    end_date,
                    travelers,
                    budget,
                    estimated_total,
                    trip_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    destination,
                    origin,
                    start_date.isoformat(),
                    end_date.isoformat(),
                    travelers,
                    request.budget,
                    estimated_total,
                    json.dumps(trip, ensure_ascii=False),
                    created_at,
                ),
            )

            trip_id = cursor.lastrowid

        return {
            "status": "success",
            "message": "Trip saved successfully!",
            "trip_id": trip_id,
        }

    except HTTPException:
        raise

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trip data: {error}",
        ) from error

    except sqlite3.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Could not save the trip to the database.",
        ) from error


# ==========================================
# GET ALL SAVED TRIPS
# ==========================================

@app.get("/api/trips")
def get_saved_trips():
    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    destination,
                    origin,
                    start_date,
                    end_date,
                    travelers,
                    budget,
                    estimated_total,
                    created_at
                FROM saved_trips
                ORDER BY id DESC
                """
            ).fetchall()

        trips = [
            {
                "id": row["id"],
                "destination": row["destination"],
                "origin": row["origin"],
                "start_date": row["start_date"],
                "end_date": row["end_date"],
                "travelers": row["travelers"],
                "budget": row["budget"],
                "estimated_total": row["estimated_total"],
                "saved_at": row["created_at"],
            }
            for row in rows
        ]

        return {
            "status": "success",
            "count": len(trips),
            "trips": trips,
        }

    except sqlite3.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve saved trips.",
        ) from error


# ==========================================
# GET ONE SAVED TRIP
# ==========================================

@app.get("/api/trips/{trip_id}")
def get_saved_trip(trip_id: int):
    if trip_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid trip ID.",
        )

    try:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM saved_trips WHERE id = ?",
                (trip_id,),
            ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Saved trip not found.",
            )

        return {
            "status": "success",
            "trip": row_to_trip(row),
        }

    except sqlite3.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve the saved trip.",
        ) from error


# ==========================================
# DELETE A SAVED TRIP
# ==========================================

@app.delete("/api/trips/{trip_id}")
def delete_saved_trip(trip_id: int):
    if trip_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid trip ID.",
        )

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM saved_trips WHERE id = ?",
                (trip_id,),
            )

            deleted = cursor.rowcount

        if deleted == 0:
            raise HTTPException(
                status_code=404,
                detail="Saved trip not found.",
            )

        return {
            "status": "success",
            "message": "Saved trip deleted successfully!",
        }

    except HTTPException:
        raise

    except sqlite3.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Could not delete the saved trip.",
        ) from error