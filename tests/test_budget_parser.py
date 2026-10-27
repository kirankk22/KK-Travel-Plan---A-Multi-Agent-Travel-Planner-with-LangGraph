
from decimal import Decimal

from tools.budget_parser import extract_budget_limit


def test_extracts_budget_with_rupee_symbol():
    assert extract_budget_limit(
        "Plan a US trip under ₹2,00,000"
    ) == Decimal("200000")


def test_extracts_budget_with_rs():
    assert extract_budget_limit(
        "Plan a trip within Rs 150000"
    ) == Decimal("150000")


def test_returns_none_when_budget_is_missing():
    assert extract_budget_limit(
        "Plan a 7-day trip to Japan from Delhi"
    ) is None


def test_extracts_budget_in_lakhs():
    assert extract_budget_limit(
        "Plan a US trip under 2 lakhs"
    ) == Decimal("200000")


def test_extracts_decimal_lakh_budget():
    assert extract_budget_limit(
        "Plan a trip within 1.5 lakhs"
    ) == Decimal("150000")

