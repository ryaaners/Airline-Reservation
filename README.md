# ✈️ Airline Reservation System
**Real flight data · SQLite database · Python · VS Code**

---

## What This Does

A fully functional command-line airline reservation app that:
- Searches **real flights** from AviationStack's live API
- Caches results in a local **SQLite database** (no extra server needed)
- Lets you **book, view, and cancel** reservations with unique booking references
- Works completely offline after the first search (cached data)

---

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| Flight data | [AviationStack API](https://aviationstack.com) | Free (100 req/month) |
| Database | SQLite (built into Python) | Free, zero setup |
| HTTP client | `requests` library | Free |
| Env vars | `python-dotenv` | Free |

---

## Project Structure

```
airline_reservation/
├── main.py           ← Entry point / menus
├── database.py       ← SQLite setup & connection helper
├── flight_search.py  ← AviationStack API calls + DB cache
├── reservations.py   ← Book / view / cancel reservations
├── requirements.txt  ← pip dependencies
├── .env.example      ← Template for your API key
└── .env              ← YOUR key goes here
```


Your folder should look like:
```
airline_reservation/
├── main.py
├── database.py
├── flight_search.py
├── reservations.py
├── requirements.txt
└── .env.example
```

Run the App
```bash
python main.py
```

You should see the main menu:
```
============================================================
       ✈️   AIRLINE RESERVATION SYSTEM   ✈️
============================================================

  1. Search Flights
  2. Make a Reservation
  3. View a Reservation
  4. Cancel a Reservation
  5. My Reservations
  6. Exit
```

The **airline.db** file is created automatically on first run.


## Common Airport IATA Codes

| Code | Airport |
|------|---------|
| JFK | New York John F. Kennedy |
| LAX | Los Angeles |
| ORD | Chicago O'Hare |
| ATL | Atlanta Hartsfield |
| LHR | London Heathrow |
| CDG | Paris Charles de Gaulle |
| DXB | Dubai International |
| SIN | Singapore Changi |
| YYZ | Toronto Pearson |
| YVR | Vancouver |
