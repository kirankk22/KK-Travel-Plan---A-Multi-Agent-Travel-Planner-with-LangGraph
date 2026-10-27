
from tools.budget_summary import build_budget_summary


def test_summary_shows_known_total_and_remaining_budget():
    result = build_budget_summary(
        200000,
        {"flight": 90000, "hotel": 50000},
    )

    assert "Known expenses total: ₹140,000.00" in result
    assert "Remaining after known costs: ₹60,000.00" in result
    assert "Confirm that all" in result


def test_summary_warns_about_unknown_costs():
    result = build_budget_summary(
        200000,
        {"flight": 90000, "hotel": 50000},
        ["Visa fees", "Local transportation"],
    )

    assert "Unknown or unverified costs:" in result
    assert "- Visa fees" in result
    assert "- Local transportation" in result
    assert "Total trip affordability cannot be confirmed" in result
    assert "Remaining budget: Not established" in result


def test_summary_reports_known_costs_over_budget():
    result = build_budget_summary(
        200000,
        {"flight": 120000, "hotel": 100000},
    )

    assert "Amount over budget from known costs: ₹20,000.00" in result
    assert "Known costs already exceed the budget." in result


def test_empty_expenses_do_not_appear_as_zero_cost_trip():
    result = build_budget_summary(
        200000,
        {},
        ["Flight fare", "Accommodation", "Visa fees"],
    )

    assert "Known expenses total: Not available" in result
    assert "Remaining budget: Not established" in result
    assert "Total trip affordability cannot be confirmed" in result

