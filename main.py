"""
✈️  Airline Reservation System
Uses: AviationStack API (real flight data) + SQLite (local database)
"""

import os
from dotenv import load_dotenv
from database import init_db
from flight_search import search_flights
from reservations import (
    make_reservation,
    view_reservation,
    cancel_reservation,
    list_my_reservations,
)

load_dotenv()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print("=" * 60)
    print("       ✈️   AIRLINE RESERVATION SYSTEM   ✈️")
    print("=" * 60)


def main_menu():
    print_banner()
    print("\n  1. Search Flights")
    print("  2. Make a Reservation")
    print("  3. View a Reservation")
    print("  4. Cancel a Reservation")
    print("  5. My Reservations")
    print("  6. Exit")
    print()
    return input("  Choose an option (1-6): ").strip()


def run_search_flow():
    print("\n── SEARCH FLIGHTS ──────────────────────────────────")
    dep = input("  Departure airport IATA code (e.g. JFK): ").strip().upper()
    arr = input("  Arrival airport IATA code  (e.g. LAX): ").strip().upper()

    if not dep or not arr:
        print("  ❌  Both fields are required.")
        return

    print(f"\n  Searching flights from {dep} → {arr} ...\n")
    flights = search_flights(dep, arr)

    if not flights:
        print("  No flights found. Try different airport codes.")
        return

    print(f"  {'#':<4} {'Flight':<10} {'Airline':<20} {'Departure':<22} {'Arrival':<22} {'Status'}")
    print("  " + "-" * 90)
    for i, f in enumerate(flights, 1):
        print(
            f"  {i:<4} {f['flight_iata']:<10} {f['airline_name'][:18]:<20} "
            f"{f['departure_scheduled']:<22} {f['arrival_scheduled']:<22} {f['flight_status']}"
        )
    print()
    input("  Press Enter to continue...")


def run_reservation_flow():
    print("\n── MAKE A RESERVATION ──────────────────────────────")
    dep = input("  Departure airport IATA (e.g. JFK): ").strip().upper()
    arr = input("  Arrival airport IATA   (e.g. LAX): ").strip().upper()

    if not dep or not arr:
        print("  ❌  Both fields are required.")
        return

    print(f"\n  Fetching available flights from {dep} → {arr} ...\n")
    flights = search_flights(dep, arr)

    if not flights:
        print("  No flights found. Try different codes.")
        input("\n  Press Enter to continue...")
        return

    print(f"  {'#':<4} {'Flight':<10} {'Airline':<22} {'Departure':<22} {'Arrival'}")
    print("  " + "-" * 80)
    for i, f in enumerate(flights, 1):
        print(
            f"  {i:<4} {f['flight_iata']:<10} {f['airline_name'][:20]:<22} "
            f"{f['departure_scheduled']:<22} {f['arrival_scheduled']}"
        )

    print()
    try:
        choice = int(input("  Select a flight number: ").strip())
        if choice < 1 or choice > len(flights):
            raise ValueError
    except ValueError:
        print("  ❌  Invalid selection.")
        return

    selected = flights[choice - 1]
    print(f"\n  Selected: {selected['flight_iata']}  |  {selected['airline_name']}")

    name = input("\n  Passenger full name : ").strip()
    email = input("  Passenger email     : ").strip()
    seat = input("  Seat class (Economy / Business / First): ").strip().title() or "Economy"

    if not name or not email:
        print("  ❌  Name and email are required.")
        return

    ref = make_reservation(selected, name, email, seat)
    print(f"\n  ✅  Reservation confirmed!")
    print(f"  Booking Reference : {ref}")
    print(f"  Flight            : {selected['flight_iata']}")
    print(f"  Route             : {dep} → {arr}")
    print(f"  Passenger         : {name}")
    print(f"  Seat Class        : {seat}")
    input("\n  Press Enter to continue...")


def run_view_flow():
    print("\n── VIEW RESERVATION ────────────────────────────────")
    ref = input("  Enter booking reference: ").strip().upper()
    if not ref:
        return
    reservation = view_reservation(ref)
    if not reservation:
        print("  ❌  No reservation found with that reference.")
    else:
        print()
        print(f"  Booking Ref  : {reservation['booking_ref']}")
        print(f"  Flight       : {reservation['flight_iata']}")
        print(f"  Route        : {reservation['departure_airport']} → {reservation['arrival_airport']}")
        print(f"  Departure    : {reservation['departure_scheduled']}")
        print(f"  Arrival      : {reservation['arrival_scheduled']}")
        print(f"  Airline      : {reservation['airline_name']}")
        print(f"  Passenger    : {reservation['passenger_name']}")
        print(f"  Email        : {reservation['passenger_email']}")
        print(f"  Seat Class   : {reservation['seat_class']}")
        print(f"  Status       : {reservation['status']}")
        print(f"  Booked At    : {reservation['created_at']}")
    print()
    input("  Press Enter to continue...")


def run_cancel_flow():
    print("\n── CANCEL RESERVATION ──────────────────────────────")
    ref = input("  Enter booking reference to cancel: ").strip().upper()
    if not ref:
        return
    success = cancel_reservation(ref)
    if success:
        print(f"  ✅  Reservation {ref} has been cancelled.")
    else:
        print("  ❌  No active reservation found with that reference.")
    input("\n  Press Enter to continue...")


def run_list_flow():
    print("\n── MY RESERVATIONS ─────────────────────────────────")
    email = input("  Enter your email address: ").strip()
    if not email:
        return
    rows = list_my_reservations(email)
    if not rows:
        print("  No reservations found for this email.")
    else:
        print(f"\n  {'Ref':<12} {'Flight':<10} {'Route':<15} {'Departure':<22} {'Class':<12} {'Status'}")
        print("  " + "-" * 85)
        for r in rows:
            route = f"{r['departure_airport']}→{r['arrival_airport']}"
            print(
                f"  {r['booking_ref']:<12} {r['flight_iata']:<10} {route:<15} "
                f"{r['departure_scheduled']:<22} {r['seat_class']:<12} {r['status']}"
            )
    print()
    input("  Press Enter to continue...")


def main():
    init_db()
    while True:
        clear()
        choice = main_menu()
        clear()
        if choice == "1":
            run_search_flow()
        elif choice == "2":
            run_reservation_flow()
        elif choice == "3":
            run_view_flow()
        elif choice == "4":
            run_cancel_flow()
        elif choice == "5":
            run_list_flow()
        elif choice == "6":
            print("\n  Goodbye! Safe travels ✈️\n")
            break
        else:
            print("  ❌  Invalid option. Try again.")
            input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
