
from tools.flight_tool import API_KEY, BASE_URL, parse_route
import requests

query = "Plan a 7 days Japan trip from Delhi"
dep_iata, arr_iata = parse_route(query)

params = {
    "access_key": API_KEY,
    "limit": 10,
    "dep_iata": dep_iata,
    "arr_iata": arr_iata,
}

response = requests.get(BASE_URL, params=params, timeout=30)
response.raise_for_status()
data = response.json()

if "error" in data:
    print("API error:", data["error"])
else:
    for flight in data.get("data", []):
        airline = flight.get("airline") or {}
        details = flight.get("flight") or {}
        departure = flight.get("departure") or {}
        arrival = flight.get("arrival") or {}

        print({
            "airline": airline.get("name"),
            "flight_number": details.get("iata"),
            "codeshared": flight.get("flight", {}).get("codeshared"),
            "status": flight.get("flight_status"),
            "departure": departure.get("scheduled"),
            "arrival": arrival.get("scheduled"),
            "departure_iata": departure.get("iata"),
            "arrival_iata": arrival.get("iata"),
        })
