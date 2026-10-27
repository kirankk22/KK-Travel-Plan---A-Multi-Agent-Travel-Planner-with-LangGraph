
from tools.flight_tool import parse_route, deduplicate_flights
from tools.flight_tool import format_flight



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

def test_format_flight_omits_missing_fields():
    flight = {
        "airline": {"name": "Example Airline"},
        "flight": {"iata": "EX123"},
        "departure": {"iata": "DEL"},
        "arrival": {"iata": "JFK"},
    }

    result = format_flight(flight)

    assert "Example Airline" in result
    assert "EX123" in result
    assert "Departure IATA: DEL" in result
    assert "Arrival IATA: JFK" in result

    assert "Departure terminal:" not in result
    assert "Departure gate:" not in result
    assert "Departure scheduled time:" not in result
    assert "Arrival terminal:" not in result
    assert "Arrival gate:" not in result
    assert "Arrival scheduled time:" not in result


def test_format_flight_includes_available_fields():
    flight = {
        "airline": {"name": "Example Airline"},
        "flight": {"iata": "EX123"},
        "flight_status": "scheduled",
        "departure": {
            "iata": "DEL",
            "terminal": "3",
            "gate": "26",
            "scheduled": "2026-11-15T10:00:00+00:00",
            "delay": 0,
        },
        "arrival": {
            "iata": "JFK",
            "terminal": "8",
            "gate": "6",
            "scheduled": "2026-11-15T16:00:00+00:00",
            "delay": 5,
        },
    }

    result = format_flight(flight)

    assert "Status: scheduled" in result
    assert "Departure terminal: 3" in result
    assert "Departure gate: 26" in result
    assert "Departure delay in minutes: 0" in result
    assert "Arrival terminal: 8" in result
    assert "Arrival gate: 6" in result
    assert "Arrival delay in minutes: 5" in result
    assert "does not establish ticket price" in result
