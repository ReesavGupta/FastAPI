# Ticket Booking System API & Web UI

This is a comprehensive FastAPI application for managing ticket bookings, events, venues, ticket types, and bookings with advanced database relationships and a feature-rich web UI.

## Features
- **API Endpoints:**
  - **Events:**
    - `POST /events` — Create new event
    - `GET /events` — Get all events
    - `GET /events/{event_id}/bookings` — Get all bookings for a specific event
    - `GET /events/{event_id}/available-tickets` — Get available tickets for an event
  - **Venues:**
    - `POST /venues` — Create new venue
    - `GET /venues` — Get all venues
    - `GET /venues/{venue_id}/events` — Get all events at a specific venue
  - **Ticket Types:**
    - `POST /ticket-types` — Create new ticket type (VIP, Standard, Economy)
    - `GET /ticket-types` — Get all ticket types
    - `GET /ticket-types/{type_id}/bookings` — Get all bookings for a specific ticket type
  - **Bookings:**
    - `POST /bookings` — Create new booking (requires existing event_id, venue_id, ticket_type_id)
    - `GET /bookings` — Get all bookings with event, venue, and ticket type details
    - `PUT /bookings/{booking_id}` — Update booking details
    - `DELETE /bookings/{booking_id}` — Cancel a booking
    - `PATCH /bookings/{booking_id}/status` — Update booking status (confirmed, cancelled, pending)
  - **Advanced Queries:**
    - `GET /bookings/search?event=name&venue=name&ticket_type=type` — Search bookings by event, venue, and/or ticket type
    - `GET /booking-system/stats` — Get booking statistics (total bookings, events, venues, available tickets)
    - `GET /events/{event_id}/revenue` — Calculate total revenue for a specific event
    - `GET /venues/{venue_id}/occupancy` — Get venue occupancy statistics

- **Database Relationships:**
  - One-to-Many: Event → Bookings, Venue → Events, Ticket Type → Bookings
  - Many-to-One: Bookings → Event, Events → Venue, Bookings → Ticket Type
  - Foreign Key Constraints: Prevent invalid bookings
  - Cascade Operations: Understand effects of deleting related entities
  - Join Operations: Fetch bookings with related data in a single query
  - Capacity Management: Enforce venue capacity limits
  - Availability Tracking: Real-time ticket availability
  - Pricing Logic: Calculate booking cost based on ticket type and quantity

- **Web UI:**
  - **Events Section:** Add/view events, booking counts, revenue
  - **Venues Section:** Add/view venues, event counts, capacity
  - **Ticket Types Section:** Add/view ticket types, pricing, booking counts
  - **Bookings Section:** Create/view bookings, dropdowns for event/venue/ticket type
  - **Search Interface:** Filter bookings by event, venue, ticket type
  - **Statistics Dashboard:** Show total counts, revenue, occupancy rates
  - **Relationship Display:** Show booking details with event, venue, ticket type
  - **Calendar View:** Display events by date with booking availability

- **Additional Features:**
  - Capacity management and enforcement
  - Pricing logic and revenue reporting
  - Real-time ticket availability
  - Booking confirmation codes

## Getting Started

### Prerequisites
- Python 3.7+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Running the Application
1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
2. Open your browser and go to [http://localhost:8000/](http://localhost:8000/) to access the web UI.
3. API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Details

### Example Entities
- **Event:**
  ```json
  {
    "id": 1,
    "name": "Concert Night",
    "venue_id": 2,
    "date": "2025-08-15",
    "capacity": 500
  }
  ```
- **Venue:**
  ```json
  {
    "id": 2,
    "name": "Grand Hall",
    "capacity": 500
  }
  ```
- **Ticket Type:**
  ```json
  {
    "id": 1,
    "type": "VIP",
    "price": 150.00
  }
  ```
- **Booking:**
  ```json
  {
    "id": 1,
    "event_id": 1,
    "venue_id": 2,
    "ticket_type_id": 1,
    "quantity": 2,
    "status": "confirmed",
    "confirmation_code": "ABC123"
  }
  ```

### Error Handling
- Returns 404 for invalid IDs or relationships
- Returns appropriate status codes for each operation (200, 201, 204, 404)
- Prevents bookings with invalid event/venue/ticket type IDs

## Notes
- All data is stored in `ticket_booking.db` (SQLite)
- Database tables are created automatically on startup
- The UI is a simple HTML/CSS page served from the `static/` directory
- Sample data may be added for testing

---

**Manage your events, venues, tickets, and bookings with ease!** 