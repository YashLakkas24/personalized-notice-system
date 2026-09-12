from app.database import SessionLocal

from app.models.student import Student

db = SessionLocal()

try:

    student = Student(
        id="student_1",
        name="Alex Kumar",
        year=3,
        branch="CS",
        interests=["Hackathons", "AI/ML", "Coding"],
    )

    db.add(student)
    db.commit()

    print("Student inserted successfully.")

finally:

    db.close()
