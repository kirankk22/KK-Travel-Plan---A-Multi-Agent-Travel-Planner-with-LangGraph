
import pytest

from tools.budget_validator import validate_budget


def test_budget_total_is_calculated_correctly():
    result = validate_budget(
        200000,
        {
            "flight": 90000,
            "visa": 13300,
            "hotel": 84000,
            "food": 17640,
        },
    )

    assert result["known_total"] == 204940
    assert result["remaining_before_unknown_costs"] == -4940
    assert result["within_limit_for_known_costs"] is False


def test_budget_within_limit_for_known_costs():
    result = validate_budget(
        200000,
        {
            "hotel": 50000,
            "food": 20000,
        },
    )

    assert result["known_total"] == 70000
    assert result["remaining_before_unknown_costs"] == 130000
    assert result["within_limit_for_known_costs"] is True


def test_negative_expense_is_rejected():
    with pytest.raises(ValueError):
        validate_budget(200000, {"hotel": -1000})


def test_invalid_budget_is_rejected():
    with pytest.raises(ValueError):
        validate_budget("not-a-number", {})

from decimal import Decimal, InvalidOperation


def validate_budget(
    budget_limit,
    expenses: dict[str, object],
) -> dict:
    """
    Validate a budget using explicitly supplied expense amounts.

    Unknown expenses should be omitted from `expenses` and listed
    separately by the caller. This function does not estimate costs.
    """
    try:
        limit = Decimal(str(budget_limit))
    except (InvalidOperation, ValueError):
        raise ValueError("Budget limit must be a valid number.")

    if not limit.is_finite() or limit < 0:
        raise ValueError("Budget limit must be finite and non-negative.")

    normalized_expenses = {}

    for category, amount in expenses.items():
        try:
            value = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            raise ValueError(
                f"Invalid expense amount for category: {category}"
            )

        if not value.is_finite() or value < 0:
            raise ValueError(
                f"Expense for {category} must be finite and non-negative."
            )

        normalized_expenses[category] = value

    known_total = sum(normalized_expenses.values(), Decimal("0"))
    remaining = limit - known_total

    return {
        "budget_limit": float(limit),
        "known_expenses": {
            category: float(amount)
            for category, amount in normalized_expenses.items()
        },
        "known_total": float(known_total),
        "remaining_before_unknown_costs": float(remaining),
        "within_limit_for_known_costs": known_total <= limit,
    }

def test_empty_expenses_leave_full_budget_remaining():
    result = validate_budget(200000, {})

    assert result["known_total"] == 0
    assert result["remaining_before_unknown_costs"] == 200000
    assert result["within_limit_for_known_costs"] is True


def test_decimal_expenses_are_added_correctly():
    result = validate_budget(
        "5000.00",
        {
            "hotel": "1250.50",
            "food": "749.25",
        },
    )

    assert result["known_total"] == 1999.75
    assert result["remaining_before_unknown_costs"] == 3000.25
    assert result["within_limit_for_known_costs"] is True


def test_known_costs_within_budget_do_not_prove_total_affordability():
    result = validate_budget(
        200000,
        {
            "flight": 90000,
            "hotel": 50000,
        },
    )

    assert result["known_total"] == 140000
    assert result["remaining_before_unknown_costs"] == 60000
    assert result["within_limit_for_known_costs"] is True

