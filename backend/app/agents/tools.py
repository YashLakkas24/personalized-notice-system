from strands import tool


@tool
def get_student_population_summary() -> str:
    """Get a high-level summary of registered students."""
    from app.database import SessionLocal
    from app.models.student import Student

    db = SessionLocal()

    try:
        students = db.query(Student).all()

        if not students:
            return "No student profiles are currently registered."

        year_counts = {}
        branch_counts = {}

        for student in students:
            year_counts[student.year] = year_counts.get(student.year, 0) + 1
            branch_counts[student.branch] = branch_counts.get(student.branch, 0) + 1

        return (
            f"Total students: {len(students)}\n"
            f"Students by year: {year_counts}\n"
            f"Students by branch: {branch_counts}"
        )
    finally:
        db.close()


@tool
def find_relevant_students(category: str, eligibility: str) -> str:
    """
    Find candidate students using basic profile matching.
    Final eligibility/relevance decisions remain with the deterministic engine.
    """
    from app.database import SessionLocal
    from app.models.student import Student

    db = SessionLocal()

    try:
        students = db.query(Student).all()

        if not students:
            return "No students are registered."

        category_text = (category or "").lower()
        eligibility_text = (eligibility or "").lower()

        candidates = []

        for student in students:
            profile_text = " ".join(
                [
                    str(student.year),
                    str(student.branch),
                    " ".join(student.interests or []),
                ]
            ).lower()

            category_match = (
                not category_text
                or category_text in profile_text
                or any(
                    word in profile_text
                    for word in category_text.split()
                    if len(word) > 3
                )
            )

            eligibility_match = not eligibility_text or any(
                token in profile_text
                for token in eligibility_text.replace(",", " ").split()
                if len(token) > 2
            )

            if category_match or eligibility_match:
                candidates.append(
                    f"{student.id} | {student.name} | "
                    f"Year {student.year} | {student.branch} | "
                    f"interests={student.interests or []}"
                )

        if not candidates:
            return "No candidate students found."

        return (
            f"Candidate students: {len(candidates)}\n"
            + "\n".join(candidates[:50])
            + "\nFinal notification decisions must use the deterministic decision engine."
        )

    finally:
        db.close()


@tool
def route_processed_notice(notice_id: str) -> str:
    """
    Execute the existing deterministic routing workflow
    for a saved notice.
    """
    from app.database import SessionLocal
    from app.models.notice import Notice
    from app.services.notification_service import route_notice_to_students

    db = SessionLocal()

    try:
        notice = db.query(Notice).filter(Notice.id == notice_id).first()

        if not notice:
            return f"Notice {notice_id} was not found."

        notifications, routing_report = route_notice_to_students(
            db,
            notice,
        )

        import json

        return json.dumps(
            {
                "status": "success",
                "notice_id": notice.id,
                "title": notice.title,
                "notifications_created": len(notifications),
                "routing_report": routing_report,
            }
        )

    except Exception as e:
        db.rollback()
        return f"Routing failed: {str(e)}"

    finally:
        db.close()
