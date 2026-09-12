from app.database import Base, engine

from app.models.student import Student
from app.models.notice import Notice

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")
