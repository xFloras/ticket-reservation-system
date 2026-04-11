from app.database import Base, engine
from app.models import User, Event, Seat, Reservation

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")