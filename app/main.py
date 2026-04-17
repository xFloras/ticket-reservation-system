from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, database
from pydantic import BaseModel
from .redis_client import set_seat_lock, release_seat_lock, get_seat_status

class BookingRequest(BaseModel):
    event_id: int
    seat_id: int
    user_id: int

app = FastAPI(title="Event Reservation System")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Event Reservation System API!"}


@app.get("/events/")
async def read_events(db: AsyncSession = Depends(database.get_db)):
    events = await db.execute(select(models.Event))
    return events.scalars().all()


@app.get("/events/{event_id}/seats/")
async def get_seats(event_id: int, db: AsyncSession = Depends(database.get_db)):
    seats = await db.execute(select(models.Seat).filter(models.Seat.event_id == event_id))
    seats_list = seats.scalars().all()
    if not seats_list:
        raise HTTPException(status_code=404, detail="Event not found or no seats available")
    return seats_list


@app.post("/book/")
async def book_seat(booking_request: BookingRequest, db: AsyncSession = Depends(database.get_db)):
    # check if seat exists for this event
    seat = await db.execute(select(models.Seat).where(
        models.Seat.event_id == booking_request.event_id,
        models.Seat.id == booking_request.seat_id
    ))
    seat = seat.scalar_one_or_none()
    
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found for the given event")

    # check if user exists
    user = await db.execute(select(models.User).where(models.User.id == booking_request.user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # check if seat is already permanently reserved in DB
    existing_reservation = await db.execute(select(models.Reservation).where(
        models.Reservation.seat_id == booking_request.seat_id
    ))
    existing_reservation = existing_reservation.scalar_one_or_none()
    if existing_reservation:
        raise HTTPException(status_code=400, detail="Seat is already reserved")

    
    # attempt to set Redis lock
    locked = await set_seat_lock(booking_request.event_id, booking_request.seat_id, booking_request.user_id)
    if not locked:
        raise HTTPException(status_code=400, detail="Seat is currently locked by another user. Please try again later.")

    return {"message": f"Seat {booking_request.seat_id} locked for 10 minutes. Proceed to payment."}


@app.post("/book/pay/{event_id}/{seat_id}")
async def pay_for_booking(event_id: int, seat_id: int, db: AsyncSession = Depends(database.get_db)):
    # get user_id from Redis
    raw = await get_seat_status(event_id, seat_id)
    if not raw:
        raise HTTPException(status_code=400, detail="Booking expired or not found — please book the seat again")

    user_id = int(raw)  # Redis returns bytes e.g. b"3", must cast to int

    # double-check the seat isn't already in reservations (edge case)
    existing = await db.execute(select(models.Reservation).where(
        models.Reservation.seat_id == seat_id
    ))
    existing = existing.scalar_one_or_none()
    if existing:
        await release_seat_lock(event_id, seat_id, user_id)  # release lock if reservation already exists
        raise HTTPException(status_code=400, detail="Seat was already reserved")

    try:
        new_reservation = models.Reservation(
            seat_id=seat_id,
            user_id=user_id,
            reservation_time=datetime.utcnow()
        )
        db.add(new_reservation)
        await db.commit()

        await release_seat_lock(event_id, seat_id, user_id)
        return {"message": f"Payment successful. Seat {seat_id} reserved for user {user_id}."}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")