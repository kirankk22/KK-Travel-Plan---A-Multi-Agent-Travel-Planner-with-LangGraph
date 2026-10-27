
from tools.budget_summary import build_budget_summary


def test_structured_budget_data_produces_deterministic_summary():
    budget_data = {
        "budget_limit": 200000,
        "known_expenses": {
            "flight": 90000,
            "hotel": 50000,
        },
        "unknown_costs": [
            "Visa fees",
            "Local transportation",
        ],
    }

    summary = build_budget_summary(
        budget_limit=budget_data["budget_limit"],
        expenses=budget_data["known_expenses"],
        unknown_costs=budget_data["unknown_costs"],
    )

    assert "Budget limit: ₹200,000.00" in summary
    assert "Known expenses total: ₹140,000.00" in summary
    assert "Remaining budget: Not established" in summary
    assert "- Visa fees" in summary
    assert "- Local transportation" in summary
    assert "Total trip affordability cannot be confirmed" in summary
