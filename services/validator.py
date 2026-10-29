
def run_budget_agent(budget, agent_reports):
    total_cost = sum(
        report["estimated_cost"]
        for report in agent_reports
    )

    remaining = budget - total_cost
    within_budget = remaining >= 0

    if within_budget:
        status = "Within budget"
        message = "The estimated trip fits the available budget."
    else:
        status = "Over budget"
        message = (
            f"The plan exceeds the budget by "
            f"₹{abs(remaining):,}."
        )

    return {
        "agent": "Budget Agent",
        "budget": budget,
        "estimated_total": total_cost,
        "remaining": remaining,
        "within_budget": within_budget,
        "status": status,
        "message": message,
    }