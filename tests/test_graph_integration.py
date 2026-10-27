
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from tests.test_final_agent import load_backend_without_database


def test_complete_travel_graph_with_mocked_services():
    backend = load_backend_without_database()

    flight_calls = []
    hotel_calls = []
    llm_calls = []

    def mock_flight_agent(state):
        flight_calls.append(state["user_query"])
        return {
            "flight_results": (
                "Mock flight result: Delhi to New York. "
                "Fare and booking availability not verified."
            ),
            "messages": [AIMessage(content="Mock flights fetched.")],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    def mock_hotel_agent(state):
        hotel_calls.append(state["user_query"])
        return {
            "hotel_results": (
                "Mock hotel result: New York accommodation options. "
                "Prices and availability not verified."
            ),
            "messages": [AIMessage(content="Mock hotels fetched.")],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    def mock_itinerary_agent(state):
        llm_calls.append(
            {
                "flight_results": state["flight_results"],
                "hotel_results": state["hotel_results"],
            }
        )

        return {
            "itinerary": (
                "Mock itinerary for New York.\n"
                "Flight details: not verified.\n"
                "Hotel prices: not verified."
            ),
            "messages": [
                AIMessage(content="Mock itinerary generated.")
            ],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    graph = StateGraph(backend.TravelState)

    graph.add_node("flight_agent", mock_flight_agent)
    graph.add_node("hotel_agent", mock_hotel_agent)
    graph.add_node("itinerary_agent", mock_itinerary_agent)
    graph.add_node("final_agent", backend.final_agent)

    graph.add_edge(START, "flight_agent")
    graph.add_edge("flight_agent", "hotel_agent")
    graph.add_edge("hotel_agent", "itinerary_agent")
    graph.add_edge("itinerary_agent", "final_agent")
    graph.add_edge("final_agent", END)

    travel_graph = graph.compile(checkpointer=InMemorySaver())

    user_query = "Plan a US trip under 2 lakhs"
    config = {
        "configurable": {
            "thread_id": "integration-test-us-trip",
        }
    }

    result = travel_graph.invoke(
        {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0,
        },
        config=config,
    )

    final_response = result["messages"][-1].content

    # Verify that each mocked service stage ran exactly once.
    assert flight_calls == [user_query]
    assert hotel_calls == [user_query]
    assert len(llm_calls) == 1

    # Verify that the itinerary agent received both search results.
    assert "Mock flight result" in llm_calls[0]["flight_results"]
    assert "Mock hotel result" in llm_calls[0]["hotel_results"]

    # Verify that the graph preserved the results in its final state.
    assert "Mock flight result" in result["flight_results"]
    assert "Mock hotel result" in result["hotel_results"]
    assert "Mock itinerary for New York" in result["itinerary"]

    # Verify the final agent appended the budget warning.
    assert "Mock itinerary for New York" in final_response
    assert "Budget limit: ₹200,000.00" in final_response
    assert "Total trip affordability cannot be confirmed" in final_response

    # Three agent steps increment the counter in this mocked graph.
    assert result["llm_calls"] == 3
