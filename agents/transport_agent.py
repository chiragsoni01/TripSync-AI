
def run_transport_agent(origin, destination, travelers):
    current_cost = 4000 * travelers
    cheaper_cost = 3000 * travelers

    return {
        "agent": "Transport Agent",
        "origin": origin,
        "destination": destination,
        "recommendation": (
            f"Compare train, bus and flight options "
            f"from {origin} to {destination}."
        ),
        "estimated_cost": current_cost,
        "cost_type": "Illustrative round-trip estimate",
        "alternative": {
            "recommendation": (
                f"Prioritize lower-cost train or bus options "
                f"from {origin} to {destination}."
            ),
            "estimated_cost": cheaper_cost,
            "cost_type": "Illustrative economical transport estimate",
        },
        "alternative_used": False,
    }