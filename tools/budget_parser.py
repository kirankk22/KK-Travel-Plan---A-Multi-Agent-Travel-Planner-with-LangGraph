
import re
from decimal import Decimal


def extract_budget_limit(user_query: str) -> Decimal | None:
    """Extract an explicitly stated rupee budget, including lakh notation."""
    text = user_query.lower().replace(",", "")

    patterns = [
        (
            r"(?:under|below|within|budget(?:\s+of)?|upto|up to)"
            r"\s*(?:₹|rs\.?\s*)?"
            r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs)\b",
            Decimal("100000"),
        ),
        (
            r"(?:under|below|within|budget(?:\s+of)?|upto|up to)"
            r"\s*(?:₹|rs\.?\s*)"
            r"(\d+(?:\.\d{1,2})?)",
            Decimal("1"),
        ),
        (
            r"(?:₹|rs\.?\s*)"
            r"(\d+(?:\.\d{1,2})?)"
            r"\s*(?:budget)?",
            Decimal("1"),
        ),
    ]

    for pattern, multiplier in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = Decimal(match.group(1)) * multiplier
            if value.is_finite() and value >= 0:
                return value

    return None
