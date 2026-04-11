from app.database import SessionLocal
from app.models import Event, Seat
from datetime import datetime, timedelta

def seed_data():
    db = SessionLocal()
    
    try:
        new_event = Event(
            name="Koncert Dawida Podsiadło",
            description="Koncert Dawida Podsiadło w Warszawie",
            date_time=datetime.now() + timedelta(days=30)
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        seats = []
        for i in range(1, 51):
            seats.append(Seat(
                event_id=new_event.id,
                seat_number=i,
                price=199.99 if i <= 10 else 99.99
            ))
        db.add_all(seats)
        db.commit()
        print("Data seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()