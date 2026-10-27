
import pytest
from unittest.mock import patch

from langchain_core.messages import AIMessage

from tests.test_final_agent import load_backend_without_database


@pytest.mark.parametrize(
    ("user_query", "expected_destination"),
    [
        ("Plan a 7-day trip to Japan from Delhi", "Japan"),
        ("Plan a trip from Bangalore to Singapore", "Singapore"),
        ("Plan a US trip under 2 lakhs", "US"),
        ("Find hotels in Tokyo", "Tokyo"),
    ],
)
def test_extract_hotel_destination(user_query, expected_destination):
    backend = load_backend_without_database()

    assert backend.extract_hotel_destination(user_query) == expected_destination


def test_hotel_agent_searches_destination_and_preserves_result():
    backend = load_backend_without_database()

    state = {
        "user_query": "Plan a 7-day trip to Japan from Delhi",
        "llm_calls": 0,
    }

    with patch(
        "backend.tavily_search",
        return_value="Mock hotel results",
    ) as search:
        result = backend.hotel_agent(state)

    search.assert_called_once_with(
        "actual hotels and accommodation properties in Japan; "
        "hotel names, locations, official hotel websites, "
        "and booking pages in Japan; "
        "exclude general travel guides where possible"
    )
    assert result["hotel_results"] == "Mock hotel results"
    assert result["llm_calls"] == 1
    assert isinstance(result["messages"][0], AIMessage)

def test_hotel_agent_uses_a_destination_specific_search_query():
    backend = load_backend_without_database()

    state = {
        "user_query": "Find hotels in Tokyo",
        "llm_calls": 0,
    }

    with patch(
        "backend.tavily_search",
        return_value="Tokyo hotel search results",
    ) as search:
        result = backend.hotel_agent(state)

    search.assert_called_once_with(
        "actual hotels and accommodation properties in Tokyo; "
        "hotel names, locations, official hotel websites, "
        "and booking pages in Tokyo; "
        "exclude general travel guides where possible"
    )
    assert result["hotel_results"] == "Tokyo hotel search results"
