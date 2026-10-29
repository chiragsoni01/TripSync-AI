import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = "gemini-3.5-flash"

AGENT_NAMES = [
    "Transport Agent",
    "Stay Agent",
    "Activities Agent",
    "Food Agent",
]

MAX_RETRIES = 3
RETRY_DELAYS = [2, 5]


def parse_gemini_json(response_text):
    """Parse Gemini's JSON response safely."""

    cleaned = response_text.strip()

    # Remove Markdown code fences.
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # Extract the JSON object.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("Gemini did not return a JSON object.")

    cleaned = cleaned[start:end + 1]

    # Remove trailing commas.
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    return json.loads(cleaned)


def get_ai_recommendations(
    destination,
    travelers,
    days,
    budget,
    agent_reports,
):
    """
    Generate recommendations for all four agents
    using one Gemini request, with limited retries.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Gemini: API key missing. Using Python fallback.")
        return None

    agent_details = []

    for report in agent_reports:
        agent_details.append({
            "agent": report["agent"],
            "estimated_cost_inr": report["estimated_cost"],
            "current_recommendation": report["recommendation"],
            "cost_type": report.get(
                "cost_type",
                "Illustrative estimate",
            ),
        })

    prompt = f"""
You are the shared AI advisor for TripSync AI.

TRIP DETAILS
Destination: {destination}
Travelers: {travelers}
Duration: {days} days
Total trip budget: INR {budget}

PYTHON AGENT REPORTS
{json.dumps(agent_details, ensure_ascii=False, indent=2)}

TASK
Generate practical recommendations for these four specialist agents:
1. Transport Agent
2. Stay Agent
3. Activities Agent
4. Food Agent

RULES
- Respect each agent's existing estimated cost.
- Treat costs as illustrative estimates, not live prices.
- Do not claim you checked live prices or availability.
- Do not claim any bookings have been made.
- Do not invent precise prices or guarantees.
- Suggest practical ways to stay within the overall budget.
- Keep each recommendation concise and specific to its agent.
- If the plan exceeds the budget, suggest reasonable savings.
- Do not change or recalculate the Python agents' costs.
- Return valid JSON only, without Markdown code fences.
- Do not include trailing commas.
- Use exactly these four keys, each with a string value.

Required JSON structure:
{{
    "Transport Agent": "Recommendation",
    "Stay Agent": "Recommendation",
    "Activities Agent": "Recommendation",
    "Food Agent": "Recommendation"
}}
"""

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=120000),
        )

        for attempt in range(MAX_RETRIES):
            try:
                print(
                    f"Gemini: Request attempt "
                    f"{attempt + 1}/{MAX_RETRIES}..."
                )

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                )

                response_text = getattr(response, "text", None)

                if not response_text or not response_text.strip():
                    print("Gemini returned an empty response.")
                    return None

                recommendations = parse_gemini_json(response_text)

                if not isinstance(recommendations, dict):
                    print("Gemini returned an invalid response.")
                    return None

                result = {}

                for agent_name in AGENT_NAMES:
                    suggestion = recommendations.get(agent_name)

                    if isinstance(suggestion, str) and suggestion.strip():
                        result[agent_name] = suggestion.strip()

                if len(result) != len(AGENT_NAMES):
                    print(
                        "Gemini response was incomplete. "
                        "Using Python fallback."
                    )
                    return None

                print(
                    "Gemini: One shared request succeeded "
                    "for all four agents."
                )

                return result

            except Exception as error:
                error_message = str(error)
                is_temporary_error = (
                    "503" in error_message
                    or "504" in error_message
                    or "UNAVAILABLE" in error_message.upper()
                    or "DEADLINE_EXCEEDED" in error_message.upper()
                )

                if not is_temporary_error:
                    print(f"Gemini request failed: {error}")
                    return None

                if attempt == MAX_RETRIES - 1:
                    print(
                        "Gemini remained unavailable after "
                        f"{MAX_RETRIES} attempts. "
                        "Using Python fallback."
                    )
                    print(f"Last error: {error}")
                    return None

                delay = RETRY_DELAYS[attempt]

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {delay} seconds..."
                )

                time.sleep(delay)

        return None

    except Exception as error:
        print(f"Gemini client initialization failed: {error}")
        return None