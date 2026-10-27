
from tools.budget_validator import validate_budget



def build_budget_summary(
    budget_limit,
    expenses: dict[str, object],
    unknown_costs: list[str] | None = None,
) -> str:
    """Build a budget summary without implying unknown costs are zero."""
    result = validate_budget(budget_limit, expenses)
    unknown_costs = unknown_costs or []

    
    lines = [
        "BUDGET VALIDATION",
        f"Budget limit: ₹{result['budget_limit']:,.2f}",
    ]

    if expenses:
        lines.append(
            f"Known expenses total: ₹{result['known_total']:,.2f}"
        )
    else:
        lines.append("Known expenses total: Not available")


    remaining = result["remaining_before_unknown_costs"]

    if not expenses:
        lines.append(
            "Remaining budget: Not established because no expense "
            "amounts have been supplied."
        )
    elif remaining < 0:
        lines.append(
            f"Amount over budget from known costs: ₹{-remaining:,.2f}"
        )
    elif not unknown_costs:
        lines.append(
            f"Remaining after known costs: ₹{remaining:,.2f}"
        )
    else:
        lines.append(
            "Remaining budget: Not established because some costs "
            "are unknown."
        )

    if remaining < 0:
        lines.append(
            f"Amount over budget from known costs: ₹{-remaining:,.2f}"
        )
    elif not unknown_costs:
        lines.append(
            f"Remaining after known costs: ₹{remaining:,.2f}"
        )
    else:
        lines.append(
            "Remaining budget: Not established because some costs "
            "are unknown."
        )

    if unknown_costs:
        lines.append("Unknown or unverified costs:")
        lines.extend(f"- {item}" for item in unknown_costs)
        lines.append(
            "Total trip affordability cannot be confirmed until "
            "these costs are priced."
        )
    elif not result["within_limit_for_known_costs"]:
        lines.append("Known costs already exceed the budget.")
    else:
        lines.append(
            "Known costs are within the budget. Confirm that all "
            "relevant expenses have been included."
        )

    return "\n".join(lines)

