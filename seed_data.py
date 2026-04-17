from app.database import SessionLocal, Base, engine
from app.models import Event, Seat, User
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt  # no 72-byte limit like bcrypt

def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── Users ──────────────────────────────────────────────────────────
        users = []
        for i in range(1, 6):
            users.append(User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=sha256_crypt.hash(f"password{i}"),
                is_active=True
            ))
        db.add_all(users)
        db.commit()
        print(f"✅ Seeded {len(users)} users.")

        # ── Event ──────────────────────────────────────────────────────────
        new_event = Event(
            name="Koncert Dawida ",
            description="Koncert Dawida w Warszawie",
            date_time=datetime.now() + timedelta(days=30)
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        print(f"✅ Seeded event: '{new_event.name}' (id={new_event.id})")

        # ── Seats ──────────────────────────────────────────────────────────
        seats = []
        for i in range(1, 51):
            seats.append(Seat(
                event_id=new_event.id,
                seat_number=str(i),
                price=199.99 if i <= 10 else 99.99
            ))
        db.add_all(seats)
        db.commit()
        print(f"✅ Seeded {len(seats)} seats.")

        print("\n🎉 All data seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()