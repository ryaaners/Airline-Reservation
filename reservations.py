"""
reservations.py – Create, read, and cancel flight reservations in SQLite.
"""

import random
import string
from database import get_connection


def _generate_ref(length: int = 8) -> str:
    """Generate a random alphanumeric booking reference, e.g. AB3X9KQ2."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


def make_reservation(flight: dict, passenger_name: str, passenger_email: str, seat_class: str = "Economy") -> str:
    """
    Store a new reservation and return the unique booking reference.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure uniqueness
    while True:
        ref = _generate_ref()
        cursor.execute("SELECT 1 FROM reservations WHERE booking_ref = ?", (ref,))
        if not cursor.fetchone():
            break

    cursor.execute("""
        INSERT INTO reservations (
            booking_ref, flight_iata, airline_name,
            departure_airport, arrival_airport,
            departure_scheduled, arrival_scheduled,
            passenger_name, passenger_email, seat_class
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ref,
        flight["flight_iata"],
        flight["airline_name"],
        flight["departure_iata"] or flight["departure_airport"],
        flight["arrival_iata"] or flight["arrival_airport"],
        flight["departure_scheduled"],
        flight["arrival_scheduled"],
        passenger_name,
        passenger_email,
        seat_class,
    ))
    conn.commit()
    conn.close()
    return ref


def view_reservation(booking_ref: str):
    """Return a reservation dict by booking reference, or None if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reservations WHERE booking_ref = ?",
        (booking_ref.upper(),)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def cancel_reservation(booking_ref: str) -> bool:
    """
    Mark a reservation as Cancelled.
    Returns True if a row was updated, False if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reservations
        SET status = 'Cancelled'
        WHERE booking_ref = ? AND status = 'Confirmed'
    """, (booking_ref.upper(),))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def list_my_reservations(email: str):
    """Return all reservations for a given email address."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM reservations
        WHERE LOWER(passenger_email) = LOWER(?)
        ORDER BY created_at DESC
    """, (email,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]