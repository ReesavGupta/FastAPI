from fastapi import FastAPI, HTTPException, Depends, Query, Request, Form
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float, Enum, func
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import enum
import random
import string
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import os

DATABASE_URL = "sqlite:///./ticket_booking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Ticket Booking System")

# Set up templates and static files
templates = Jinja2Templates(directory="static/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enum for Booking Status
class BookingStatus(str, enum.Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    pending = "pending"

# MODELS
class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    events = relationship("Event", back_populates="venue", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    date = Column(DateTime, nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    venue = relationship("Venue", back_populates="events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="event", cascade="all, delete-orphan")

class TicketType(Base):
    __tablename__ = "ticket_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # VIP, Standard, Economy
    price = Column(Float, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    event = relationship("Event", back_populates="ticket_types")
    bookings = relationship("Booking", back_populates="ticket_type", cascade="all, delete-orphan")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending, nullable=False)
    confirmation_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    event = relationship("Event", back_populates="bookings")
    ticket_type = relationship("TicketType", back_populates="bookings")
    # venue relationship is not needed directly, as event.venue is available

# SCHEMAS
class VenueBase(BaseModel):
    name: str
    address: str
    capacity: int

class VenueCreate(VenueBase):
    pass

class VenueOut(VenueBase):
    id: int
    class Config:
        orm_mode = True

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    date: datetime
    venue_id: int

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    class Config:
        orm_mode = True

class TicketTypeBase(BaseModel):
    name: str
    price: float
    event_id: int

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketTypeOut(TicketTypeBase):
    id: int
    class Config:
        orm_mode = True

class BookingBase(BaseModel):
    event_id: int
    venue_id: int
    ticket_type_id: int
    quantity: int

class BookingCreate(BookingBase):
    pass

class BookingOut(BookingBase):
    id: int
    status: BookingStatus
    confirmation_code: str
    created_at: datetime
    class Config:
        orm_mode = True

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DB INIT
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# VENUE ENDPOINTS
@app.post("/venues", response_model=VenueOut)
def create_venue(venue: VenueCreate, db: Session = Depends(get_db)):
    db_venue = Venue(**venue.dict())
    db.add(db_venue)
    try:
        db.commit()
        db.refresh(db_venue)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Venue with this name already exists.")
    return db_venue

@app.get("/venues", response_model=List[VenueOut])
def get_venues(db: Session = Depends(get_db)):
    return db.query(Venue).all()

@app.get("/venues/{venue_id}/events", response_model=List[EventOut])
def get_events_at_venue(venue_id: int, db: Session = Depends(get_db)):
    events = db.query(Event).filter(Event.venue_id == venue_id).all()
    return events

# EVENT ENDPOINTS
@app.get("/events", response_class=HTMLResponse)
def events_page(request: Request, db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return templates.TemplateResponse("events.html", {"request": request, "events": events})

@app.post("/events", response_class=HTMLResponse)
def add_event(request: Request, name: str = Form(...), description: str = Form(None), date: str = Form(...), venue_id: int = Form(...), db: Session = Depends(get_db)):
    try:
        event_date = datetime.fromisoformat(date)
    except Exception:
        event_date = datetime.now()
    db_event = Event(name=name, description=description, date=event_date, venue_id=venue_id)
    db.add(db_event)
    db.commit()
    return RedirectResponse(url="/events", status_code=303)

@app.get("/events/{event_id}/bookings", response_model=List[BookingOut])
def get_bookings_for_event(event_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.event_id == event_id).all()
    return bookings

# TICKET TYPE ENDPOINTS
@app.post("/ticket-types", response_model=TicketTypeOut)
def create_ticket_type(ticket_type: TicketTypeCreate, db: Session = Depends(get_db)):
    # Check event exists
    event = db.query(Event).filter(Event.id == ticket_type.event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    db_type = TicketType(**ticket_type.dict())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

@app.get("/ticket-types", response_model=List[TicketTypeOut])
def get_ticket_types(db: Session = Depends(get_db)):
    return db.query(TicketType).all()

@app.get("/ticket-types/{type_id}/bookings", response_model=List[BookingOut])
def get_bookings_for_ticket_type(type_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.ticket_type_id == type_id).all()
    return bookings

# BOOKING ENDPOINTS

def generate_confirmation_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.post("/bookings", response_model=BookingOut)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    # Validate event, venue, ticket type
    event = db.query(Event).filter(Event.id == booking.event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    venue = db.query(Venue).filter(Venue.id == booking.venue_id).first()
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found.")
    ticket_type = db.query(TicketType).filter(TicketType.id == booking.ticket_type_id, TicketType.event_id == booking.event_id).first()
    if ticket_type is None:
        raise HTTPException(status_code=404, detail="Ticket type not found for this event.")
    # Check venue matches event
    if event.venue_id != venue.id:
        raise HTTPException(status_code=400, detail="Venue does not match event.")
    # Check capacity
    total_booked = db.query(func.sum(Booking.quantity)).filter(Booking.event_id == event.id, Booking.status == BookingStatus.confirmed).scalar() or 0
    if total_booked + booking.quantity > venue.capacity:
        raise HTTPException(status_code=400, detail="Venue capacity exceeded.")
    # Check ticket availability (per ticket type)
    type_booked = db.query(func.sum(Booking.quantity)).filter(Booking.ticket_type_id == ticket_type.id, Booking.status == BookingStatus.confirmed).scalar() or 0
    # For now, assume unlimited per type unless you want to set a limit
    # Generate confirmation code
    confirmation_code = generate_confirmation_code()
    db_booking = Booking(**booking.dict(), status=BookingStatus.confirmed, confirmation_code=confirmation_code)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings", response_model=List[BookingOut])
def get_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()

@app.put("/bookings/{booking_id}", response_model=BookingOut)
def update_booking(booking_id: int, booking: BookingCreate, db: Session = Depends(get_db)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    # Only allow update if not cancelled
    if db_booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Cannot update a cancelled booking.")
    # Validate event, venue, ticket type
    event = db.query(Event).filter(Event.id == booking.event_id).first()
    venue = db.query(Venue).filter(Venue.id == booking.venue_id).first()
    ticket_type = db.query(TicketType).filter(TicketType.id == booking.ticket_type_id, TicketType.event_id == booking.event_id).first()
    if event is None or venue is None or ticket_type is None:
        raise HTTPException(status_code=400, detail="Invalid event, venue, or ticket type.")
    if event.venue_id != venue.id:
        raise HTTPException(status_code=400, detail="Venue does not match event.")
    setattr(db_booking, 'event_id', booking.event_id)
    setattr(db_booking, 'venue_id', booking.venue_id)
    setattr(db_booking, 'ticket_type_id', booking.ticket_type_id)
    setattr(db_booking, 'quantity', booking.quantity)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    db.delete(db_booking)
    db.commit()
    return {"detail": "Booking deleted."}

@app.patch("/bookings/{booking_id}/status", response_model=BookingOut)
def update_booking_status(booking_id: int, status: BookingStatus, db: Session = Depends(get_db)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    setattr(db_booking, 'status', status)
    db.commit()
    db.refresh(db_booking)
    return db_booking

# AVAILABLE TICKETS FOR EVENT
@app.get("/events/{event_id}/available-tickets")
def get_available_tickets(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    venue = db.query(Venue).filter(Venue.id == event.venue_id).first()
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found.")
    total_booked = db.query(func.sum(Booking.quantity)).filter(Booking.event_id == event_id, Booking.status == BookingStatus.confirmed).scalar()
    total_booked = int(total_booked or 0)
    available = venue.capacity - total_booked
    return {"event_id": event_id, "available_tickets": available, "venue_capacity": venue.capacity}

@app.get("/bookings/search", response_model=List[BookingOut])
def search_bookings(
    event: Optional[str] = Query(None),
    venue: Optional[str] = Query(None),
    ticket_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Booking)
    if event:
        query = query.join(Event).filter(Event.name.ilike(f"%{event}%"))
    if venue:
        query = query.join(Venue, Booking.venue_id == Venue.id).filter(Venue.name.ilike(f"%{venue}%"))
    if ticket_type:
        query = query.join(TicketType).filter(TicketType.name.ilike(f"%{ticket_type}%"))
    return query.all()

@app.get("/booking-system/stats")
def booking_system_stats(db: Session = Depends(get_db)):
    total_bookings = db.query(Booking).count()
    total_events = db.query(Event).count()
    total_venues = db.query(Venue).count()
    total_available_tickets = 0
    for event in db.query(Event).all():
        venue = db.query(Venue).filter(Venue.id == event.venue_id).first()
        if isinstance(venue, Venue) and hasattr(venue, 'capacity') and isinstance(venue.capacity, int):
            total_booked = db.query(func.sum(Booking.quantity)).filter(Booking.event_id == event.id, Booking.status == BookingStatus.confirmed).scalar()
            total_booked = int(total_booked or 0)
            venue_capacity = venue.capacity
            total_available_tickets += max(venue_capacity - total_booked, 0)
        else:
            continue
    return {
        "total_bookings": total_bookings,
        "total_events": total_events,
        "total_venues": total_venues,
        "total_available_tickets": total_available_tickets
    }

@app.get("/events/{event_id}/revenue")
def event_revenue(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    revenue = db.query(func.sum(Booking.quantity * TicketType.price)).join(TicketType, Booking.ticket_type_id == TicketType.id).filter(Booking.event_id == event_id, Booking.status == BookingStatus.confirmed).scalar() or 0.0
    return {"event_id": event_id, "revenue": revenue}

@app.get("/venues/{venue_id}/occupancy")
def venue_occupancy(venue_id: int, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found.")
    events = db.query(Event).filter(Event.venue_id == venue_id).all()
    occupancy = []
    for event in events:
        total_booked = db.query(func.sum(Booking.quantity)).filter(Booking.event_id == event.id, Booking.status == BookingStatus.confirmed).scalar()
        total_booked = int(total_booked or 0)
        if hasattr(venue, 'capacity') and isinstance(venue.capacity, int):
            venue_capacity = venue.capacity
        else:
            venue_capacity = 0
        occupancy_rate = (total_booked / venue_capacity) if venue_capacity > 0 else 0
        occupancy.append({
            "event_id": event.id,
            "event_name": event.name,
            "booked": total_booked,
            "capacity": venue_capacity,
            "occupancy_rate": occupancy_rate
        })
    return {"venue_id": venue_id, "venue_name": venue.name, "occupancy": occupancy}

@app.get("/", response_class=HTMLResponse)
def root(request):
    return templates.TemplateResponse("base.html", {"request": request}) 