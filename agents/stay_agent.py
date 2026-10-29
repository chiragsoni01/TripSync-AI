
import math

def run_stay_agent(travelers, nights):
    rooms = math.ceil(travelers / 2)

    current_cost = rooms * nights * 2500
    cheaper_cost = rooms * nights * 2000

    return {
        "agent": "Stay Agent",
        "rooms": rooms,
        "nights": nights,
        "recommendation": (
            f"Look for accommodation with {rooms} room(s) "
            f"for {nights} night(s)."
        ),
        "estimated_cost": current_cost,
        "cost_type": "Illustrative accommodation estimate",
        "alternative": {
            "recommendation": (
                f"Prioritize budget stays for {rooms} room(s) "
                f"over {nights} night(s)."
            ),
            "estimated_cost": cheaper_cost,
            "cost_type": "Illustrative budget-stay estimate",
        },
        "alternative_used": False,
    }