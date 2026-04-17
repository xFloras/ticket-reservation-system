from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    reservations = relationship("Reservation", back_populates="user")

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    date_time = Column(DateTime, nullable=False)
    
    seats = relationship("Seat", back_populates="event")

class Seat(Base):
    __tablename__ = 'seats'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    seat_number = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    event = relationship("Event", back_populates="seats")
    reservations = relationship("Reservation", back_populates="seat")   

class Reservation(Base):
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    seat_id = Column(Integer, ForeignKey('seats.id'), nullable=False)
    reservation_time = Column(DateTime, default=datetime.datetime.utcnow())
    
    user = relationship("User", back_populates="reservations")
    seat = relationship("Seat", back_populates="reservations")  