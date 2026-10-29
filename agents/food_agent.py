
def run_food_agent(travelers, days):
    current_cost = 700 * travelers * days
    cheaper_cost = 600 * travelers * days

    return {
        "agent": "Food Agent",
        "recommendation": (
            "Plan for breakfast, lunch, dinner and local food."
        ),
        "estimated_cost": current_cost,
        "cost_type": "Illustrative food estimate",
        "alternative": {
            "recommendation": (
                "Prioritize affordable local eateries "
                "and economical meal options."
            ),
            "estimated_cost": cheaper_cost,
            "cost_type": "Illustrative economical food estimate",
        },
        "alternative_used": False,
    }