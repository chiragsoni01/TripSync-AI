from services.trip_storage import (
    save_trip,
    get_saved_trips,
    load_trip,
    delete_trip,
)


# Create a sample trip for testing.
sample_plan = {
    "origin": "Delhi",
    "destination": "Goa",
    "travelers": 2,
    "days": 4,
    "nights": 3,
    "initial_total": 27500,
}

# 1. Save the trip.
trip_id = save_trip(
    sample_plan,
    "My Goa Trip Test",
)

print("1. Trip saved successfully!")
print("Trip ID:", trip_id)

# 2. Retrieve all saved trips.
trips = get_saved_trips()

print("\n2. Total saved trips:", len(trips))

# 3. Load the saved trip.
loaded_trip = load_trip(trip_id)

if loaded_trip:
    print("3. Trip loaded successfully!")
    print("Trip name:", loaded_trip["name"])
    print("Destination:", loaded_trip["plan"]["destination"])
else:
    print("3. Trip loading failed!")

# 4. Delete the test trip.
deleted = delete_trip(trip_id)

print("\n4. Test trip deleted:", deleted)

# 5. Verify deletion.
print(
    "5. Trip still exists:",
    load_trip(trip_id) is not None,
)