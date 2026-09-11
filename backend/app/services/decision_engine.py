from typing import Dict, Any

from app.services.eligibility_engine import check_eligibility
from app.services.relevance_engine import calculate_relevance


def evaluate_student_for_notice(
    student: Dict[str, Any], notice: Dict[str, Any]
) -> Dict[str, Any]:

    # --------------------------------
    # STEP 1 — Eligibility
    # --------------------------------

    eligibility = check_eligibility(student, notice)

    if not eligibility["eligible"]:
        return {
            "routing": "SUPPRESS",
            "eligible": False,
            "relevance_level": "NONE",
            "reason": "Student is not eligible.",
            "eligibility": eligibility,
            "relevance": None,
        }

    # --------------------------------
    # STEP 2 — Mandatory notice
    # --------------------------------

    if notice.get("is_mandatory", False):
        return {
            "routing": "MUST_NOTIFY",
            "eligible": True,
            "relevance_score": 1.0,
            "relevance_level": "MANDATORY",
            "reason": "This is a mandatory notice for the student.",
            "eligibility": eligibility,
            "relevance": None,
        }

    # --------------------------------
    # STEP 3 — Interest relevance
    # --------------------------------

    relevance = calculate_relevance(student, notice)

    score = relevance["score"]

    # --------------------------------
    # STEP 4 — Final routing
    # --------------------------------

    if score >= 0.7:
        routing = "HIGHLY_RELEVANT"
        reason = "Strong match with student's interests."

    elif score >= 0.4:
        routing = "RELEVANT"
        reason = "Notice matches some of the student's interests."

    elif score > 0:
        routing = "LOW_PRIORITY"
        reason = "Weak interest match."

    else:
        routing = "SUPPRESS"
        reason = "No meaningful interest match."

    return {
        "routing": routing,
        "eligible": True,
        "relevance_score": score,
        "relevance_level": relevance["level"],
        "reason": reason,
        "eligibility": eligibility,
        "relevance": relevance,
    }
