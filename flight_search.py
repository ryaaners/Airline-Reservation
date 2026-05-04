"""
flight_search.py – Fetch real flight data from AviationStack API.

Free plan:  100 requests / month, HTTP only (HTTPS needs paid plan).
Docs:       https://aviationstack.com/documentation
"""

import os
import requests
from database import get_connection

AVIATIONSTACK_BASE = "http://api.aviationstack.com/v1"


def _api_key():
    key = os.getenv("AVIATIONSTACK_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "\n  ❌  AVIATIONSTACK_API_KEY not set.\n"
            "  Add it to your .env file:  AVIATIONSTACK_API_KEY=your_key_here\n"
            "  Get a free key at: https://aviationstack.com/signup/free\n"
        )
    return key


def search_flights(dep_iata: str, arr_iata: str, limit: int = 10) -> list[dict]:
    """
    Query AviationStack for flights between two airports.
    Falls back to cached DB results if the API is unavailable.
    """
    try:
        params = {
            "access_key": _api_key(),
            "dep_iata": dep_iata,
            "arr_iata": arr_iata,
            "limit": limit,
        }
        resp = requests.get(f"{AVIATIONSTACK_BASE}/flights", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            err = data["error"]
            print(f"\n  ⚠️  API error: {err.get('info', err)}")
            return _load_from_cache(dep_iata, arr_iata)

        raw_flights = data.get("data", [])
        if not raw_flights:
            print(f"  ℹ️  No live flights found for {dep_iata} → {arr_iata}.")
            return _load_from_cache(dep_iata, arr_iata)

        flights = [_normalise(f) for f in raw_flights if _normalise(f)]
        _save_to_cache(flights)
        return flights

    except requests.exceptions.RequestException as exc:
        print(f"\n  ⚠️  Network error: {exc}")
        print("  Falling back to cached results...\n")
        return _load_from_cache(dep_iata, arr_iata)


def _normalise(raw: dict):
    """Extract only the fields we care about from the raw API response."""
    try:
        dep = raw.get("departure") or {}
        arr = raw.get("arrival") or {}
        airline = raw.get("airline") or {}
        flight = raw.get("flight") or {}

        iata = (flight.get("iata") or "").strip()
        if not iata:
            return None   # skip records without a flight number

        return {
            "flight_iata":         iata,
            "flight_icao":         (flight.get("icao") or "").strip(),
            "airline_name":        (airline.get("name") or "Unknown Airline").strip(),
            "airline_iata":        (airline.get("iata") or "").strip(),
            "departure_airport":   (dep.get("airport") or dep.get("iata") or "N/A").strip(),
            "departure_iata":      (dep.get("iata") or "").strip(),
            "arrival_airport":     (arr.get("airport") or arr.get("iata") or "N/A").strip(),
            "arrival_iata":        (arr.get("iata") or "").strip(),
            "departure_scheduled": (dep.get("scheduled") or "N/A").strip(),
            "arrival_scheduled":   (arr.get("scheduled") or "N/A").strip(),
            "flight_status":       (raw.get("flight_status") or "scheduled").strip(),
        }
    except Exception:
        return None


def _save_to_cache(flights: list[dict]):
    """Persist fetched flights to SQLite for offline / quota-saving fallback."""
    if not flights:
        return
    conn = get_connection()
    cursor = conn.cursor()
    for f in flights:
        cursor.execute("""
            INSERT INTO flights_cache (
                flight_iata, flight_icao, airline_name, airline_iata,
                departure_airport, departure_iata,
                arrival_airport, arrival_iata,
                departure_scheduled, arrival_scheduled, flight_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f["flight_iata"], f["flight_icao"], f["airline_name"], f["airline_iata"],
            f["departure_airport"], f["departure_iata"],
            f["arrival_airport"], f["arrival_iata"],
            f["departure_scheduled"], f["arrival_scheduled"], f["flight_status"],
        ))
    conn.commit()
    conn.close()


def _load_from_cache(dep_iata: str, arr_iata: str) -> list[dict]:
    """Return the most recent cached flights for this route."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM flights_cache
        WHERE departure_iata = ? AND arrival_iata = ?
        ORDER BY fetched_at DESC
        LIMIT 10
    """, (dep_iata, arr_iata))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows] if rows else []
