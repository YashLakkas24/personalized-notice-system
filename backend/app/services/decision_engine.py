from typing import Dict, Any

from app.services.eligibility_engine import check_eligibility
from app.services.embedding_service import cosine_similarity

HIGH_RELEVANCE = 0.75
MEDIUM_RELEVANCE = 0.55


def evaluate_student_for_notice(
    student: Dict[str, Any], notice: Dict[str, Any]
) -> Dict[str, Any]:

    # ========================================================
    # STEP 1 — ELIGIBILITY
    # ========================================================

    eligibility = check_eligibility(student, notice)

    if not eligibility["eligible"]:

        return {
            "routing": "SUPPRESS",
            "eligible": False,
            "relevance_score": 0.0,
            "relevance_level": "NONE",
            "reason": "Student is not eligible.",
            "eligibility": eligibility,
        }

    # ========================================================
    # STEP 2 — MANDATORY
    # ========================================================

    if notice.get("is_mandatory", False):

        return {
            "routing": "MUST_NOTIFY",
            "eligible": True,
            "relevance_score": 1.0,
            "relevance_level": "MANDATORY",
            "reason": "Mandatory notice for this eligible student.",
            "eligibility": eligibility,
        }

    # ========================================================
    # STEP 3 — SEMANTIC MATCHING
    # ========================================================

    student_embedding = student.get("interest_embedding")

    notice_embedding = notice.get("notice_embedding")

    if not student_embedding or not notice_embedding:

        return {
            "routing": "SUPPRESS",
            "eligible": True,
            "relevance_score": 0.0,
            "relevance_level": "NONE",
            "reason": "Embeddings unavailable.",
            "eligibility": eligibility,
        }

    score = cosine_similarity(student_embedding, notice_embedding)

    score = max(0.0, min(1.0, score))

    # ========================================================
    # STEP 4 — RELEVANCE LEVEL
    # ========================================================

    if score >= HIGH_RELEVANCE:

        level = "HIGH"
        routing = "NOTIFY"

        reason = "Strong semantic match with the student's interests."

    elif score >= MEDIUM_RELEVANCE:

        level = "MEDIUM"
        routing = "NOTIFY"

        reason = "Moderate semantic match with the student's interests."

    else:

        level = "LOW"
        routing = "SUPPRESS"

        reason = "The notice has low semantic relevance to the student."

    return {
        "routing": routing,
        "eligible": True,
        "relevance_score": round(score, 4),
        "relevance_level": level,
        "reason": reason,
        "eligibility": eligibility,
    }
