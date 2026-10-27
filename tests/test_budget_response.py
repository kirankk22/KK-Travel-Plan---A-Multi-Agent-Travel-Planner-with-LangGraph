
from tools.budget_response import add_budget_summary


def test_budget_request_appends_budget_summary():
    result = add_budget_summary(
        "Plan a US trip under 2 lakhs",
        "Here is a preliminary itinerary.",
    )

    assert "Here is a preliminary itinerary." in result
    assert "Budget limit: ₹200,000.00" in result
    assert "Known expenses total: Not available" in result
    assert "Remaining budget: Not established" in result
    assert "Total trip affordability cannot be confirmed" in result


def test_request_without_budget_keeps_itinerary_unchanged():
    itinerary = "Here is a Japan itinerary."

    result = add_budget_summary(
        "Plan a 7-day trip to Japan from Delhi",
        itinerary,
    )

    assert result == itinerary


def test_empty_itinerary_still_returns_budget_warning():
    result = add_budget_summary(
        "Plan a US trip under 2 lakhs",
        "",
    )

    assert "BUDGET VALIDATION" in result
    assert "Remaining budget: Not established" in result
