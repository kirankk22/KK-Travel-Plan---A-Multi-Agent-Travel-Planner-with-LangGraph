
from tools.flight_tool import parse_route, deduplicate_flights


def test_japan_trip_from_delhi():
    assert parse_route("Plan a 7 days Japan trip from Delhi") == (
        "DEL",
        "NRT",
    )


def test_bangalore_to_singapore():
    assert parse_route("Flights from Bangalore to Singapore") == (
        "BLR",
        "SIN",
    )


def test_destination_only():
    assert parse_route("Plan a trip to Japan") == (
        "DEL",
        "NRT",
    )


def test_duplicate_flight_is_removed():
    flight = {
        "flight": {"iata": "JL740"},
        "departure": {
            "iata": "DEL",
            "scheduled": "2026-10-27T04:35:00+00:00",
        },
        "arrival": {"iata": "NRT"},
        "flight_status": "active",
    }

    result = deduplicate_flights([flight, flight.copy()])

    assert len(result) == 1


def test_different_dates_are_preserved():
    today = {
        "flight": {"iata": "JL740"},
        "departure": {
            "iata": "DEL",
            "scheduled": "2026-10-27T04:35:00+00:00",
        },
        "arrival": {"iata": "NRT"},
        "flight_status": "active",
    }

    yesterday = {
        **today,
        "departure": {
            "iata": "DEL",
            "scheduled": "2026-10-26T04:35:00+00:00",
        },
        "flight_status": "landed",
    }

    result = deduplicate_flights([today, yesterday])

    assert len(result) == 2
