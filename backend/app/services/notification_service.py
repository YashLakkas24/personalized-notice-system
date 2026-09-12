import uuid

from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.notice import Notice
from app.models.notification import Notification

from app.services.decision_engine import evaluate_student_for_notice


def route_notice_to_students(
    db: Session,
    notice: Notice,
):

    students = db.query(Student).all()

    created = []

    for student_record in students:

        # Convert SQLAlchemy model -> dictionary
        student = {
            "id": student_record.id,
            "name": student_record.name,
            "year": student_record.year,
            "branch": student_record.branch,
            "interests": student_record.interests or [],
            "interest_embedding": student_record.interest_embedding,
        }

        notice_data = {
            "id": notice.id,
            "title": notice.title,
            "category": notice.category,
            "is_mandatory": notice.is_mandatory,
            "eligibility": notice.eligibility or {},
            "deadline": notice.deadline,
            "registration_link": notice.registration_link,
            "required_action": notice.required_action,
            "importance": notice.importance,
            "summary": notice.summary,
            "notice_embedding": notice.notice_embedding,
        }

        evaluation = evaluate_student_for_notice(
            student,
            notice_data,
        )

        if evaluation["routing"] not in [
            "NOTIFY",
            "MUST_NOTIFY",
        ]:
            continue

        # Prevent duplicate notifications
        existing = (
            db.query(Notification)
            .filter(
                Notification.student_id == student["id"],
                Notification.notice_id == notice.id,
            )
            .first()
        )

        if existing:
            continue

        notification = Notification(
            id=str(uuid.uuid4()),
            student_id=student["id"],
            notice_id=notice.id,
            relevance_score=evaluation["relevance_score"],
            priority=evaluation["priority"],
            urgency=evaluation["urgency"],
            days_left=evaluation["days_left"],
            reason=evaluation["reason"],
            status="UNREAD",
        )

        db.add(notification)

        created.append(notification)

    db.commit()

    return created
