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

    # Routing metrics
    students_evaluated = 0
    eligible_count = 0
    not_eligible_count = 0
    highly_relevant_count = 0
    medium_relevant_count = 0
    suppressed_count = 0
    mandatory_count = 0

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

        # ------------------------------------------
        # Routing metrics
        # ------------------------------------------

        if evaluation["eligible"]:
            eligible_count += 1
        else:
            not_eligible_count += 1

        if evaluation["relevance_level"] == "HIGH":
            highly_relevant_count += 1

        elif evaluation["relevance_level"] == "MEDIUM":
            medium_relevant_count += 1

        if evaluation["routing"] == "SUPPRESS":
            suppressed_count += 1
            continue

        if evaluation["routing"] == "MUST_NOTIFY":
            mandatory_count += 1

        # ------------------------------------------
        # Prevent duplicate notifications
        # ------------------------------------------

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

    # ------------------------------------------
    # Routing report
    # ------------------------------------------

    routing_report = {
        "students_evaluated": students_evaluated,
        "eligible": eligible_count,
        "not_eligible": not_eligible_count,
        "highly_relevant": highly_relevant_count,
        "medium_relevant": medium_relevant_count,
        "suppressed": suppressed_count,
        "mandatory": mandatory_count,
        "notifications_created": len(created),
    }

    return created, routing_report
