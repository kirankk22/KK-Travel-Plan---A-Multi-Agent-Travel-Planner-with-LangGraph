
from tools.budget_parser import extract_budget_limit
from tools.budget_summary import build_budget_summary


UNKNOWN_TRAVEL_COSTS = [
    "International flight fares and booking availability",
    "Accommodation prices and availability",
    "Visa fees and travel insurance",
    "Meals and local transportation",
    "Sightseeing tickets and other trip expenses",
]


def add_budget_summary(user_query: str, itinerary: str) -> str:
    """Append a cautious budget summary when the request states a budget."""
    budget_limit = extract_budget_limit(user_query)

    if budget_limit is None:
        return itinerary

    summary = build_budget_summary(
        budget_limit=budget_limit,
        expenses={},
        unknown_costs=UNKNOWN_TRAVEL_COSTS,
    )

    if itinerary.strip():
        return f"{itinerary.strip()}\n\n{summary}"

    return summary
