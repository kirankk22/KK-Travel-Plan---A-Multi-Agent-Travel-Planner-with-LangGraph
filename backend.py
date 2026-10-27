
import os
import uuid
import operator
from typing import TypedDict, Annotated

import certifi
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from tools.budget_response import add_budget_summary


import re


def extract_hotel_destination(user_query: str) -> str:
    """Extract a destination from common travel requests without guessing."""
    query = user_query.strip()

    # Prefer explicit "from X to Y" routes.
    match = re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)"
        r"(?=\s+(?:on|for|under|including|with|in|at|within)\b|[.!?]|$)",
        query,
        flags=re.IGNORECASE,
    )
    if match:
        destination = match.group(2).strip(" ,.")
        if destination:
            return destination

    # Handle requests such as "trip to Japan" or "hotels in Singapore".
    match = re.search(
        r"\b(?:trip|travel|holiday|vacation|hotels?|accommodation)"
        r"\s+(?:to|in)\s+(.+?)"
        r"(?=\s+(?:from|on|for|under|including|with|within|budget)\b|[.!?]|$)",
        query,
        flags=re.IGNORECASE,
    )
    if match:
        destination = match.group(1).strip(" ,.")
        if destination:
            return destination

    # Handle simpler requests such as "Plan a trip to Japan".
    match = re.search(
        r"\bto\s+([A-Za-z][A-Za-z\s-]*?)"
        r"(?=\s+(?:from|on|for|under|including|with|within|budget)\b|[.!?]|$)",
        query,
        flags=re.IGNORECASE,
    )
    if match:
        destination = match.group(1).strip(" ,.")
        if destination:
            return destination

    # Handle requests such as "Plan a US trip under 2 lakhs".
    match = re.search(
        r"\b(?:a|an)\s+([A-Za-z][A-Za-z\s-]*?)\s+trip\b",
        query,
        flags=re.IGNORECASE,
    )
    if match:
        destination = match.group(1).strip(" ,.")
        if destination and destination.lower() not in {
            "budget", "cheap", "luxury", "short", "long"
        }:
            return destination

    # If we cannot confidently extract a destination, preserve the query.
    return query



# =========================
# Environment Configuration
# =========================

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL is missing. "
            "Please add your Render PostgreSQL External Database URL to .env"
        )

    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"

    return database_url


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Please add it to your .env file."
    )


# =========================
# LLM
# =========================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY,
)


# =========================
# State
# =========================

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


# =========================
# Flight Agent
# =========================

def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight results fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Hotel Agent
# =========================



def hotel_agent(state: TravelState):
    destination = extract_hotel_destination(state["user_query"])
    query = f"hotels and resorts in {destination} official websites booking"

    hotel_results = tavily_search(query)

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }




# =========================
# Itinerary Agent
# =========================

def itinerary_agent(state: TravelState):
    prompt = f"""
Create a practical travel itinerary using the information provided below.

User Query:
{state['user_query']}

Flight Results:
{state['flight_results']}

Hotel Results:
{state['hotel_results']}

STRICT ACCURACY RULES:
1. Use only facts explicitly supported by the supplied results.
2. Never invent flight numbers, departure or arrival times, dates,
   terminals, gates, delays, layovers, or flight durations.
3. AviationStack flight-status results do not establish ticket prices
   or guarantee that a flight can be booked.
4. Never present estimated flight fares as live or confirmed prices.
5. Never invent hotel prices, ratings, reviews, availability,
   amenities, or booking confirmations.
6. If information is missing, say "Not verified" or
   "Price/availability not confirmed".
7. Clearly distinguish verified information from estimates.
8. Do not assume that an international traveller is eligible for
   visa-free entry or an electronic travel authorization.
   Flag visa requirements for verification using official sources.
9. Do not invent travel dates. If dates are missing, ask the user
   to confirm them or clearly state any proposed dates as assumptions.
10. Calculate the budget using explicitly stated amounts. Show
    the arithmetic and identify costs that remain unknown.
11. Never claim the trip fits the user's budget if the known costs
    and unpriced items do not support that conclusion.
12. Do not invent API results to make the itinerary look complete.

Produce:
- Trip overview
- Flight information supported by the results
- Accommodation options supported by the results
- Day-by-day sightseeing plan
- Itemized estimated budget, with assumptions
- Missing information and items requiring verification

A useful, honest partial itinerary is better than a complete
itinerary containing unsupported details.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content="You are an expert travel planner."
            ),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Final Response Agent
# =========================

def final_agent(state: TravelState):
    """Return the itinerary with a deterministic budget summary."""

    itinerary = state.get("itinerary", "").strip()

    if not itinerary:
        final_response = (
            "I could not generate a reliable itinerary from the "
            "available information. Please try again."
        )
    else:
        final_response = itinerary

    final_response = add_budget_summary(
        user_query=state.get("user_query", ""),
        itinerary=final_response,
    )

    return {
        "messages": [AIMessage(content=final_response)],
        "llm_calls": state.get("llm_calls", 0),
    }


# =========================
# Build Graph
# =========================

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


# =========================
# PostgreSQL Checkpointer
# =========================

DATABASE_URL = get_database_url()

_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row,
)

checkpointer = PostgresSaver(_conn)
checkpointer.setup()

travel_graph = graph.compile(checkpointer=checkpointer)


# =========================
# Function for FastAPI / CLI
# =========================

def run_travel_agent(
    user_input: str,
    thread_id: str | None = None,
):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = travel_graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0,
        },
        config=config,
    )

    final_answer = result["messages"][-1].content

    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }
