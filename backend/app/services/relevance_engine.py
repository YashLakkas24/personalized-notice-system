from typing import Dict, Any


def calculate_relevance(
    student: Dict[str, Any], notice: Dict[str, Any]
) -> Dict[str, Any]:
    interests = [str(i).lower() for i in student.get("interests", [])]

    category = str(notice.get("category", "")).lower()

    title = str(notice.get("title", "")).lower()

    summary = str(notice.get("summary", "")).lower()

    score = 0.0
    matched_interests = []

    if category in interests:
        score += 0.5
        matched_interests.append(category)

    notice_text = f"{title}{summary}"

    for interest in interests:
        if interest in notice_text:
            score += 0.2

            if interest not in matched_interests:
                matched_interests.append(interest)

    score = min(score, 1.0)

    if score >= 0.7:
        level = "HIGH"

    elif score >= 0.4:
        level = "MEDIUM"

    elif score > 0:
        level = "LOW"

    else:
        level = "NONE"

    return {
        "score": round(score, 2),
        "level": level,
        "matched_interests": matched_interests,
    }
