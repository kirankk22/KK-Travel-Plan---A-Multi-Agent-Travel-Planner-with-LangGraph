
import importlib
import sys
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver


def load_backend_without_database():
    """Import backend without opening a real PostgreSQL connection."""

    sys.modules.pop("backend", None)

    
    with (
        patch("psycopg.connect", return_value=MagicMock()),
        patch(
            "langgraph.checkpoint.postgres.PostgresSaver"
        ) as saver_class,
    ):
        saver = InMemorySaver()
        saver.setup = MagicMock()
        saver_class.return_value = saver

        backend = importlib.import_module("backend")


    return backend


def test_final_agent_appends_budget_summary_when_budget_is_provided():
    backend = load_backend_without_database()

    state = {
        "user_query": "Plan a US trip under 2 lakhs",
        "itinerary": "Here is a preliminary itinerary.",
        "llm_calls": 3,
    }

    result = backend.final_agent(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert "Here is a preliminary itinerary." in result["messages"][0].content
    assert "Budget limit: ₹200,000.00" in result["messages"][0].content
    assert "Total trip affordability cannot be confirmed" in result["messages"][0].content
    assert result["llm_calls"] == 3


def test_final_agent_does_not_add_budget_summary_without_budget():
    backend = load_backend_without_database()

    state = {
        "user_query": "Plan a 7-day trip to Japan from Delhi",
        "itinerary": "Here is a Japan itinerary.",
        "llm_calls": 2,
    }

    result = backend.final_agent(state)

    assert result["messages"][0].content == "Here is a Japan itinerary."
    assert "BUDGET VALIDATION" not in result["messages"][0].content
    assert result["llm_calls"] == 2


def test_final_agent_handles_empty_itinerary_with_budget():
    backend = load_backend_without_database()

    state = {
        "user_query": "Plan a US trip under 2 lakhs",
        "itinerary": "",
        "llm_calls": 1,
    }

    result = backend.final_agent(state)

    assert "I could not generate a reliable itinerary" in result["messages"][0].content
    assert "Budget limit: ₹200,000.00" in result["messages"][0].content
    assert "Total trip affordability cannot be confirmed" in result["messages"][0].content
