from copy import deepcopy

from services.ai_client import get_ai_recommendations

from agents.transport_agent import run_transport_agent
from agents.stay_agent import run_stay_agent
from agents.activities_agent import run_activities_agent
from agents.food_agent import run_food_agent

from services.validator import run_budget_agent


MAX_REPLANNING_ROUNDS = 4


def create_trip_plan(
    origin,
    destination,
    start_date,
    end_date,
    travelers,
    budget,
):
    if end_date <= start_date:
        raise ValueError("End date must be after start date.")

    nights = (end_date - start_date).days
    days = nights + 1

    # Phase 1: Collect reports from four Python agents.
    reports = [
        run_transport_agent(origin, destination, travelers),
        run_stay_agent(travelers, nights),
        run_activities_agent(destination, travelers, days),
        run_food_agent(travelers, days),
    ]

    # Phase 2: Make ONE shared Gemini request.
    ai_recommendations = get_ai_recommendations(
        destination=destination,
        travelers=travelers,
        days=days,
        budget=budget,
        agent_reports=reports,
    )

    ai_enabled_count = 0

    for report in reports:
        agent_name = report["agent"]

        report["ai_recommendation"] = None
        report["ai_status"] = "Python fallback"

        if ai_recommendations:
            suggestion = ai_recommendations.get(agent_name)

            if suggestion:
                report["ai_recommendation"] = suggestion
                report["ai_status"] = "Gemini AI"
                ai_enabled_count += 1

    # Phase 3: Calculate the initial budget.
    initial_budget_report = run_budget_agent(budget, reports)
    initial_total = initial_budget_report["estimated_total"]

    activity_log = [
        f"Orchestrator collected reports from {len(reports)} specialist agents.",
        (
            f"Shared Gemini recommendations available for "
            f"{ai_enabled_count} of {len(reports)} agents."
        ),
        f"Budget Agent calculated the initial total: ₹{initial_total:,}.",
    ]

    rounds = 0

    # Phase 4: Select cheaper alternatives while over budget.
    while rounds < MAX_REPLANNING_ROUNDS:
        budget_report = run_budget_agent(budget, reports)

        if budget_report["within_budget"]:
            activity_log.append("Budget Agent approved the current plan.")
            break

        candidates = []

        for index, report in enumerate(reports):
            alternative = report.get("alternative")

            if (
                not alternative
                or report.get("alternative_used", False)
            ):
                continue

            saving = (
                report["estimated_cost"]
                - alternative["estimated_cost"]
            )

            if saving > 0:
                candidates.append((saving, index))

        if not candidates:
            activity_log.append(
                "No cheaper alternatives remain. "
                "The plan is still over budget."
            )
            break

        saving, index = max(candidates)

        report = reports[index]
        alternative = report["alternative"]
        old_cost = report["estimated_cost"]

        report["recommendation"] = alternative["recommendation"]
        report["estimated_cost"] = alternative["estimated_cost"]
        report["cost_type"] = alternative["cost_type"]
        report["alternative_used"] = True

        rounds += 1

        activity_log.append(
            f"Orchestrator selected a cheaper option from "
            f"{report['agent']}: ₹{old_cost:,} → "
            f"₹{report['estimated_cost']:,} (saved ₹{saving:,})."
        )

        updated_budget_report = run_budget_agent(budget, reports)

        activity_log.append(
            f"Budget Agent rechecked the plan: "
            f"₹{updated_budget_report['estimated_total']:,} total."
        )

    # Phase 5: Validate the final budget.
    budget_report = run_budget_agent(budget, reports)

    if not budget_report["within_budget"]:
        activity_log.append(
            "Replanning finished, but available alternatives "
            "could not meet the budget target."
        )

    return {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "days": days,
        "nights": nights,
        "reports": reports,
        "initial_total": initial_total,
        "replanning_rounds": rounds,
        "ai_enabled_count": ai_enabled_count,
        "activity_log": activity_log,
        "budget_report": budget_report,
    }


def create_travel_strategies(
    origin,
    destination,
    start_date,
    end_date,
    travelers,
    budget,
):
    """
    Compare three independent travel strategies.

    Python agents calculate all costs.
    The existing budget validator checks each strategy.
    """

    if end_date <= start_date:
        raise ValueError("End date must be after start date.")

    if travelers < 1:
        raise ValueError("Travelers must be at least 1.")

    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    nights = (end_date - start_date).days
    days = nights + 1

    # Build the reports once, then make independent copies.
    base_reports = [
        run_transport_agent(origin, destination, travelers),
        run_stay_agent(travelers, nights),
        run_activities_agent(destination, travelers, days),
        run_food_agent(travelers, days),
    ]

    strategies = [
        {
            "strategy": "Budget Explorer",
            "description": (
                "Prioritizes economical options to reduce "
                "the estimated trip cost."
            ),
            "mode": "economical",
        },
        {
            "strategy": "Balanced Traveller",
            "description": (
                "Balances the original recommendations with "
                "economical alternatives when needed."
            ),
            "mode": "balanced",
        },
        {
            "strategy": "Comfort Seeker",
            "description": (
                "Keeps the original recommendations where "
                "possible and clearly checks affordability."
            ),
            "mode": "comfort",
        },
    ]

    results = []

    for strategy in strategies:
        reports = deepcopy(base_reports)
        mode = strategy["mode"]
        activity_log = []

        # Budget Explorer: use every available cheaper option.
        if mode == "economical":
            for report in reports:
                alternative = report.get("alternative")

                if (
                    alternative
                    and alternative["estimated_cost"]
                    < report["estimated_cost"]
                ):
                    report["recommendation"] = (
                        alternative["recommendation"]
                    )
                    report["estimated_cost"] = (
                        alternative["estimated_cost"]
                    )
                    report["cost_type"] = alternative["cost_type"]
                    report["alternative_used"] = True

            activity_log.append(
                "Selected economical alternatives where available."
            )

        # Balanced Traveller: reduce costs only as much as needed.
        elif mode == "balanced":
            rounds = 0

            while rounds < MAX_REPLANNING_ROUNDS:
                budget_report = run_budget_agent(budget, reports)

                if budget_report["within_budget"]:
                    break

                candidates = []

                for index, report in enumerate(reports):
                    alternative = report.get("alternative")

                    if (
                        not alternative
                        or report.get("alternative_used", False)
                    ):
                        continue

                    saving = (
                        report["estimated_cost"]
                        - alternative["estimated_cost"]
                    )

                    if saving > 0:
                        candidates.append((saving, index))

                if not candidates:
                    break

                saving, index = max(candidates)
                report = reports[index]
                alternative = report["alternative"]

                report["recommendation"] = (
                    alternative["recommendation"]
                )
                report["estimated_cost"] = (
                    alternative["estimated_cost"]
                )
                report["cost_type"] = alternative["cost_type"]
                report["alternative_used"] = True

                rounds += 1

                activity_log.append(
                    f"Changed {report['agent']} to an economical "
                    f"option, saving ₹{saving:,}."
                )

            if rounds == 0:
                activity_log.append(
                    "Original recommendations already fit the budget "
                    "or no economical change was available."
                )

        # Comfort Seeker deliberately retains original choices.
        else:
            activity_log.append(
                "Retained the original agent recommendations."
            )

        # Validate the strategy independently.
        budget_report = run_budget_agent(budget, reports)

        results.append({
            "strategy": strategy["strategy"],
            "description": strategy["description"],
            "origin": origin,
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "travelers": travelers,
            "days": days,
            "nights": nights,
            "reports": reports,
            "budget_report": budget_report,
            "estimated_total": budget_report["estimated_total"],
            "remaining_budget": budget_report["remaining"],
            "within_budget": budget_report["within_budget"],
            "activity_log": activity_log,
        })

    # Compare results without changing any strategy's reports.
    results.sort(key=lambda item: item["estimated_total"])

    return {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "days": days,
        "nights": nights,
        "budget": budget,
        "strategies": results,
        "strategy_count": len(results),
        "costs_are_illustrative": True,
    }