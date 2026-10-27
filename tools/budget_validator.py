
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
