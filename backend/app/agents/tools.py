from strands import tool


@tool
def route_processed_notice(notice_id: str) -> str:
    """
    Route an already-processed notice to the students
    who are eligible and relevant.

    The actual eligibility, relevance, urgency and priority
    decisions are handled by the application's deterministic
    decision engine.
    """

    return (
        f"Notice {notice_id} is ready for student routing. "
        "Use the application's notification workflow to "
        "evaluate students and create notifications."
    )


@tool
def find_relevant_students(
    category: str,
    eligibility: str,
) -> str:
    """
    Find student groups that may be relevant to a notice.

    This tool provides the agent with a summary of the
    student population matching the notice criteria.
    """

    return f"""
    Find students relevant to this notice:

    Category:
    {category}

    Eligibility:
    {eligibility}

    Consider:
    - year
    - branch
    - interests
    - eligibility requirements
    """


@tool
def get_student_population_summary() -> str:
    """
    Get a summary of the student population.

    This is a read-only tool. It provides the agent
    with high-level information about students without
    exposing database credentials or allowing direct SQL.
    """

    from app.database import SessionLocal
    from app.models.student import Student

    db = SessionLocal()

    try:
        students = db.query(Student).all()

        if not students:
            return "No student profiles are currently registered."

        total = len(students)

        year_counts = {}
        branch_counts = {}

        for student in students:

            year_counts[student.year] = year_counts.get(student.year, 0) + 1

            branch_counts[student.branch] = branch_counts.get(student.branch, 0) + 1

        return (
            f"Total students: {total}\n"
            f"Students by year: {year_counts}\n"
            f"Students by branch: {branch_counts}"
        )

    finally:
        db.close()
