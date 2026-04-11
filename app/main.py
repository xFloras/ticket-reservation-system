from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database
from typing import List
from pydantic import BaseModel
from .redis_client import redis_client

class BookingRequest(BaseModel):
    event_id: int
    seat_id: int
    user_name: str

app = FastAPI(title="Event Reservation System")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Event Reservation System API!"}

@app.get("/events/")
def read_events(db: Session = Depends(database.get_db)):
    events = db.query(models.Event).all()
    return events

@app.get("/events/{event_id}/seats/")
def get_seats(event_id: int, db: Session = Depends(database.get_db)):
    seats = db.query(models.Seat).filter(models.Seat.event_id == event_id).all()
    if not seats:
        raise HTTPException(status_code=404, detail="Event not found or no seats available")
    return seats

@app.post("/book/")
def book_seat(booking_request: BookingRequest, db: Session = Depends(database.get_db)):
    # check if seat is present in the database
    seat = db.query(models.Seat).filter(models.Seat.event_id == booking_request.event_id, models.Seat.id == booking_request.seat_id).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found for the given event")

    # check if seat is already booked
    if redis_client.get(f"event_{booking_request.event_id}:seat_{booking_request.seat_id}"):
        raise HTTPException(status_code=400, detail="Seat is already booked")
    
    # lock the seat for the user

    