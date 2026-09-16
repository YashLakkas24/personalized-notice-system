from typing import Dict, Any


def check_eligibility(
    student: Dict[str, Any], notice: Dict[str, Any]
) -> Dict[str, Any]:

    eligibility = notice.get("eligibility", {})

    eligible_years = eligibility.get("years") or []
    eligible_branches = eligibility.get("branches") or ["ALL"]

    student_year = student.get("year")
    student_branch = (student.get("branch") or "").strip().upper()
    # -------------------------
    # Branch eligibility
    # -------------------------

    normalized_branches = [str(branch).strip().upper() for branch in eligible_branches]

    # Empty / ALL = no restriction
    year_match = not eligible_years or student_year in eligible_years

    branch_match = (
        not normalized_branches
        or "ALL" in normalized_branches
        or student_branch in normalized_branches
    )
    eligible = year_match and branch_match

    reasons = []

    if not year_match:
        reasons.append(f"Student year {student_year} is not eligible.")

    if not branch_match:
        reasons.append(f"Student branch {student_branch} is not eligible.")

    if eligible:
        reasons.append("Student satisfies the stated eligibility criteria.")

    return {
        "eligible": eligible,
        "year_match": year_match,
        "branch_match": branch_match,
        "reasons": reasons,
    }
