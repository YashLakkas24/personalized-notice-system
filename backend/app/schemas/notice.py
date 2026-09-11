from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class NoticeEligibility(BaseModel):
    branches: List[str] = Field(
        default_factory=lambda: ["ALL"],
        description="Eligible academic branches.Use ALL when there is no branch restriction.",
    )

    years: List[int] = Field(
        default_factory=list,
        description="Eligible student years. Empty list means all years.",
    )

    other_criteria: Optional[str] = Field(
        default=None,
        description="Other eligibility requirements such as CGPA, gender, skills, team size, etc.",
    )


class NoticeMetadata(BaseModel):
    title: str = Field(description="Clear and concise title of the notice.")

    category: str = Field(
        description=(
            "One of: Sports, Hackathons, Technical, Cultural, Clubs, "
            "Scholarships, Internships, Academics, Workshops, Other."
        )
    )

    is_mandatory: bool = Field(
        description=(
            "True only when students are required to act, such as "
            "mandatory registration, examination instructions, or official notices."
        )
    )

    eligibility: NoticeEligibility

    deadline: Optional[date] = Field(
        default=None,
        description="Final application or registration deadline, if explicitly stated.",
    )

    summary: str = Field(
        description="Concise two-sentence summary for a student's personalized feed."
    )

    registration_link: Optional[str] = Field(
        default=None, description="Registration URL if one is present in the notice."
    )

    required_action: Optional[str] = Field(
        default=None,
        description="What the student needs to do, for example Apply, Register, Attend, Submit, or None.",
    )

    importance: str = Field(
        default="NORMAL", description="One of: CRITICAL, HIGH, NORMAL, LOW."
    )
