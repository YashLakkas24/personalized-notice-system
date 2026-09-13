from strands import tool


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
