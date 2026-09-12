from app.database import SessionLocal
from app.models.student import Student
from app.models.notice import Notice
from app.services.embedding_service import create_embedding

db = SessionLocal()

try:

    # Students
    students = db.query(Student).all()

    for student in students:

        if student.interest_embedding:
            continue

        interests = ", ".join(student.interests or [])

        text = f"""
            Student interests:
            {interests}
        """

        student.interest_embedding = create_embedding(text)

        print(f"Generated embedding for student: " f"{student.name}")

        # Notices
    notices = db.query(Notice).all()

    for notice in notices:

        if notice.notice_embedding:
            continue

        text = f"""
        Title: {notice.title}
        Category: {notice.category}
        Summary: {notice.summary}
        Required action: {notice.required_action}
        Eligibility: {notice.eligibility}
        """

        notice.notice_embedding = create_embedding(text)

        print(f"Generated embedding for notice: " f"{notice.title}")

    db.commit()

    print("\nAll embeddings generated successfully.")

except Exception as e:

    db.rollback()
    print(f"ERROR: {e}")

finally:

    db.close()
