import os
import re
import certifi
import airportsdata
import pycountry
from dotenv import load_dotenv
import requests

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# Default origin when user says only destination, example "Japan trip"
# Change this if your default origin is not Delhi (DEL). You can set it in the .env file as well.
DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "DEL")

BASE_URL = "http://api.aviationstack.com/v1/flights"
AIRPORTS = airportsdata.load("IATA")

COUNTRY_ALIASES = {
    "usa": "US",
    "u.s.a": "US",
    "u.s.": "US",
    "america": "US",
    "united states": "US",
    "uk": "GB",
    "u.k.": "GB",
    "britain": "GB",
    "england": "GB",
    "uae": "AE",
    "dubai": "AE",
    "south korea": "KR",
    "korea": "KR",
    "russia": "RU",
    "vietnam": "VN",
    "bangladesh": "BD",
    "india": "IN",
    "japan": "JP",
    "china": "CN",
    "singapore": "SG",
    "malaysia": "MY",
    "thailand": "TH",
    "indonesia": "ID",
    "nepal": "NP",
    "qatar": "QA",
    "saudi arabia": "SA",
    "turkey": "TR",
    "canada": "CA",
    "australia": "AU",
    "germany": "DE",
    "france": "FR",
    "italy": "IT",
    "spain": "ES",
}


# Preferred main airport for country-level search
COUNTRY_MAIN_AIRPORT = {
    "BD": "DAC",
    "IN": "DEL",
    "JP": "NRT",
    "US": "JFK",
    "GB": "LHR",
    "AE": "DXB",
    "SG": "SIN",
    "MY": "KUL",
    "TH": "BKK",
    "ID": "CGK",
    "CN": "PEK",
    "KR": "ICN",
    "NP": "KTM",
    "QA": "DOH",
    "SA": "JED",
    "TR": "IST",
    "CA": "YYZ",
    "AU": "SYD",
    "DE": "FRA",
    "FR": "CDG",
    "IT": "FCO",
    "ES": "MAD",
}




CITY_MAIN_AIRPORT = {
    "dhaka": "DAC",
    "delhi": "DEL",
    "new delhi": "DEL",
    "mumbai": "BOM",
    "kolkata": "CCU",
    "chennai": "MAA",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "tokyo": "NRT",
    "osaka": "KIX",
    "kyoto": "KIX",
    "new york": "JFK",
    "london": "LHR",
    "dubai": "DXB",
    "singapore": "SIN",
    "kuala lumpur": "KUL",
    "bangkok": "BKK",
    "doha": "DOH",
    "istanbul": "IST",
    "toronto": "YYZ",
    "sydney": "SYD",
    "paris": "CDG",
    "rome": "FCO",
    "madrid": "MAD",
    "frankfurt": "FRA",
}

def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    stop_words = [
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"
    ]
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words).strip()



def country_name_to_code(text: str):
    text = clean_text(text)

    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]

    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass

    # Detect country name inside longer text
    for country in pycountry.countries:
        country_name = country.name.lower()
        if country_name in text:
            return country.alpha_2

    for alias, code in COUNTRY_ALIASES.items():
        if alias in text:
            return code

    return None



def airport_country_matches(airport: dict, country_code: str) -> bool:
    airport_country = str(airport.get("country", "")).upper().strip()

    if airport_country == country_code:
        return True

    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country and airport_country.lower() == country.name.lower():
            return True
    except Exception:
        pass

    return False




def get_best_airport_for_country(country_code: str):
    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)

    if preferred and preferred in AIRPORTS:
        return preferred

    candidates = []

    for iata, airport in AIRPORTS.items():
        if not iata:
            continue

        if airport_country_matches(airport, country_code):
            name = str(airport.get("name", "")).lower()
            city = str(airport.get("city", "")).lower()

            score = 0

            if "international" in name:
                score += 50
            if "intl" in name:
                score += 40
            if "capital" in name:
                score += 20
            if city:
                score += 5

            candidates.append((score, iata))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]




def resolve_location_to_iata(location: str):
    """
    Converts country/city/airport/IATA into IATA code.

    Examples:
    Delhi -> DEL
    Japan -> NRT
    Delhi -> DEL
    Tokyo -> NRT
    DEL -> DEL
    """

    if not location:
        return None

    raw_location = location.strip()

    # Direct IATA code
    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)

    if not location_clean:
        return None

    # City preferred airport
    if location_clean in CITY_MAIN_AIRPORT:
        return CITY_MAIN_AIRPORT[location_clean]

    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
        if airport:
            return airport

    # Exact city match from airport database
    city_matches = []

    for iata, airport in AIRPORTS.items():
        city = str(airport.get("city", "")).lower().strip()
        name = str(airport.get("name", "")).lower().strip()

        score = 0

        if city == location_clean:
            score += 100
        elif location_clean in city:
            score += 70

        if location_clean in name:
            score += 50

        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]

    return None




def find_location_mentions(query: str):
    """
    Finds country or city names inside a natural language query.
    """

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", q):
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"\b{re.escape(name)}\b", q):
            mentions.append(name)

    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORT:
        if re.search(rf"\b{re.escape(city)}\b", q):
            mentions.append(city)

    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions



def parse_route(query: str):
    """
    Returns (departure_iata, arrival_iata).

    Examples:
        Japan trip from Delhi -> DEL, NRT
        Japan trip -> DEL, NRT
        Flights from Delhi -> DEL, None
        Flights to Tokyo -> None, NRT
        DEL to NRT -> DEL, NRT
        All country flight info -> None, None
    """
    q = query.strip()
    q_lower = q.lower()

    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]

    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # 1. Explicit airport route, such as DEL to NRT.
    code_match = re.search(
        r"\b([A-Z]{3})\s+to\s+([A-Z]{3})\b", q
    )
    if code_match:
        dep = resolve_location_to_iata(code_match.group(1))
        arr = resolve_location_to_iata(code_match.group(2))
        if dep and arr:
            return dep, arr

    # 2. Find recognized city/country mentions in the full query.
    mentions = find_location_mentions(q)
    locations = []

    for mention in mentions:
        iata = resolve_location_to_iata(mention)
        if iata and iata not in locations:
            locations.append(iata)

    # 3. Handle "from X to Y".
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)"
        r"(?=\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )
    if match:
        dep = resolve_location_to_iata(match.group(1))
        arr = resolve_location_to_iata(match.group(2))
        return dep, arr

    # 4. Handle "to Y from X".
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)"
        r"(?=\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )
    if match:
        arr = resolve_location_to_iata(match.group(1))
        dep = resolve_location_to_iata(match.group(2))
        return dep, arr

    # 5. Handle an explicit origin, while still detecting
    # a destination mentioned elsewhere in the query.
    origin_match = re.search(
        r"\bfrom\s+([a-z][a-z\s-]*?)(?=\s+(?:including|with|under|for|on|"
        r"budget|flights?|hotels?|and)\b|[.!?,]|$)",
        q_lower,
    )
    if origin_match:
        dep = resolve_location_to_iata(origin_match.group(1))

        if dep:
            for arr in locations:
                if arr != dep:
                    return dep, arr

            return dep, None

    # 6. Handle an explicit destination.
    to_match = re.search(
        r"\bto\s+([a-z][a-z\s-]*?)(?=\s+(?:from|including|with|under|"
        r"for|on|budget|flights?|hotels?|and)\b|[.!?,]|$)",
        q_lower,
    )
    if to_match:
        arr = resolve_location_to_iata(to_match.group(1))
        if arr:
            return DEFAULT_ORIGIN_IATA, arr

    # 7. Fallback: use recognized locations.
    if len(locations) >= 2:
        return locations[0], locations[1]

    if len(locations) == 1:
        return DEFAULT_ORIGIN_IATA, locations[0]

    return None, None



def format_flight(flight: dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()



def deduplicate_flights(flights: list[dict]) -> list[dict]:
    """
    Remove exact duplicate records and suppress codeshare listings
    when the primary marketed flight is present.
    """
    # First, retain only the first record for each exact flight identity.
    unique_flights = []
    seen = set()

    for flight in flights:
        flight_info = flight.get("flight") or {}
        departure = flight.get("departure") or {}
        arrival = flight.get("arrival") or {}

        key = (
            flight_info.get("iata"),
            departure.get("iata"),
            arrival.get("iata"),
            departure.get("scheduled"),
            flight.get("flight_status"),
        )

        if not all(key):
            unique_flights.append(flight)
            continue

        if key not in seen:
            seen.add(key)
            unique_flights.append(flight)

    # Identify primary flight identities that are present in the results.
    primary_flights = set()

    for flight in unique_flights:
        flight_info = flight.get("flight") or {}
        departure = flight.get("departure") or {}
        arrival = flight.get("arrival") or {}

        codeshared = flight_info.get("codeshared")

        if not codeshared:
            primary_flights.add((
                (flight_info.get("iata") or "").upper(),
                departure.get("iata"),
                arrival.get("iata"),
                departure.get("scheduled"),
            ))

    # Suppress a codeshare record only when its primary flight is present.
    results = []

    for flight in unique_flights:
        flight_info = flight.get("flight") or {}
        departure = flight.get("departure") or {}
        arrival = flight.get("arrival") or {}
        codeshared = flight_info.get("codeshared") or {}

        if codeshared:
            marketed_flight = (
                (codeshared.get("flight_iata") or "").upper(),
                departure.get("iata"),
                arrival.get("iata"),
                departure.get("scheduled"),
            )

            if marketed_flight in primary_flights:
                continue

        results.append(flight)

    return results


def search_flights(query: str, limit: int = 10):
    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(query)

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        print("AviationStack request parameters:", {
            key: value for key, value in params.items() if key != "access_key"
        })
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed: {e}"
    except ValueError:
        return "Flight API returned invalid JSON."

    if "error" in data:
        error = data["error"]
        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    flight_data = data.get("data", [])

    if not flight_data:
        route_text = ""

        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"

        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )

    route_info = "Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Live flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Live flights to {arr_iata}"

    
    unique_flights = deduplicate_flights(flight_data)
    formatted_flights = [
        format_flight(flight)
        for flight in unique_flights[:limit]
    ]

    if not formatted_flights:
        return f"No flight records available: {route_info}"

    return f"{route_info}\n\n" + "\n\n---\n\n".join(formatted_flights)



if __name__ == "__main__":
    print(search_flights("Plan a 7 days Japan trip from Delhi"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info"))

