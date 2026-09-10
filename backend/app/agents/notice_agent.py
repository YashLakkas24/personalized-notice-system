import os
import json
from strands import Agent
from strands_tools import tool
from app.agents.prompts import NOTICE_SYSTEM_PROMPT

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@tool
def calculate_match_score(student_profile: dict, notice_metadata: dict) -> dict:
    """
    Deterministically filters eligibility and evaluates the semantic matching
    coefficient between a student's interests and the notice metadata.
    """

    eligibility = False

    notice_eligibility = notice_metadata.get("eligibility", {})
    eligible_years = notice_eligibility.get("years", [])
    eligible_branches = notice_eligibility.get("brances", [])

    student_year = student_profile.get("year")
    student_branch = student_profile.get("branch")

    year_match = (student_year in eligible_years) or (not eligible_years)
    branch_match = (student_branch in eligible_branches) or ("ALL" in eligible_branches)

    if year_match and branch_match:
        eligible = True

    if notice_metadata.get("is_mandatory", False):
        return {"eligible": eligible, "relevance_score": 1.0, "routing": "MUST_NOTIFY"}

    if not eligible:
        return {"eligible": False, "relevance_score": 0.0, "routing": "SUPPRESSED"}

    student_interests = [i.lower() for i in student_profile.get("interests", [])]
    notice_category = notice_metadata.get("category", "").lower()
    notice_title = notice_metadata.get("title", "").lower()

    match_count = 0
    if notice_category in student_interests:
        match_count += 2

    for interest in student_interests:
        if interest in notice_title:
            match_count += 1

    relevance_score = min(1.0, 0.2 + (match_count * 0.25))

    routing = "HIGHLY_RELEVANT" if relevance_score >= 0.6 else "MAYBE_RELEVANT"

    return {
        "eligible": True,
        "relevance_score": round(relevance_score, 2),
        "routing": routing,
    }


notice_agent = Agent(
    model="openai/gpt-5-nano",
    tools=[calculate_match_score],
    system_prompt=NOTICE_SYSTEM_PROMPT,
    temperature=0.1,
)


def process_new_notice(raw_text: str) -> dict:
    """Invokes the Strands Agent workflow loop to convert text to structured data."""
    try:
        response = notice_agent.run(
            f"Parse this unstructured notice text completely:\n\n{raw_text}"
        )
        # Clean up code blocks if the LLM accidentally includes them
        cleaned_response = (
            response.content.replace("```json", "").replace("```", "").strip()
        )
        return json.loads(cleaned_response)
    except Exception as e:
        return {
            "error": "Failed to parse notice via AI agent.",
            "details": str(e),
            "title": "Fallback: Unparsed Notice",
            "category": "Academics",
            "is_mandatory": True,
            "eligibility": {"branches": ["ALL"], "years": [1, 2, 3, 4]},
            "summary": raw_text[:150],
            "deadline": "None Specified",
        }
