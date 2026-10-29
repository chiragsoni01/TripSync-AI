
def run_activities_agent(destination, travelers, days):
    current_cost = 800 * travelers * days
    cheaper_cost = 600 * travelers * days

    return {
        "agent": "Activities Agent",
        "recommendation": (
            f"Explore sightseeing, local attractions and "
            f"outdoor activities in {destination}."
        ),
        "estimated_cost": current_cost,
        "cost_type": "Illustrative activity estimate",
        "alternative": {
            "recommendation": (
                f"Prioritize free attractions, public beaches "
                f"and lower-cost activities in {destination}."
            ),
            "estimated_cost": cheaper_cost,
            "cost_type": "Illustrative economical activity estimate",
        },
        "alternative_used": False,
    }