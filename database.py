"""
database.py - SQLite setup for the Airline Reservation System.
The database file (airline.db) is created automatically in the project folder.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "airline.db")


def get_connection():
    """Return a SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets you access columns by name
    return conn


def init_db():
    """Create tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── flights cache ────────────────────────────────────────────────────────
    # We cache API responses here so re-searches don't eat your free quota.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights_cache (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_iata          TEXT,
            flight_icao          TEXT,
            airline_name         TEXT,
            airline_iata         TEXT,
            departure_airport    TEXT,
            departure_iata       TEXT,
            arrival_airport      TEXT,
            arrival_iata         TEXT,
            departure_scheduled  TEXT,
            arrival_scheduled    TEXT,
            flight_status        TEXT,
            fetched_at           DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── reservations ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_ref          TEXT UNIQUE NOT NULL,
            flight_iata          TEXT NOT NULL,
            airline_name         TEXT,
            departure_airport    TEXT,
            arrival_airport      TEXT,
            departure_scheduled  TEXT,
            arrival_scheduled    TEXT,
            passenger_name       TEXT NOT NULL,
            passenger_email      TEXT NOT NULL,
            seat_class           TEXT DEFAULT 'Economy',
            status               TEXT DEFAULT 'Confirmed',
            created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("  ✅  Database ready  →  airline.db")