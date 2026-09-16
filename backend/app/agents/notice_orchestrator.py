from strands import Agent
from strands.models import OpenAIModel
from app.agents.tools import (
    get_student_population_summary,
    find_relevant_students,
    route_processed_notice,
)
import os

model = OpenAIModel(
    client_args={
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
    model_id="gpt-4o-mini",
    params={
        "temperature": 0.1,
        "max_tokens": 1000,
    },
)


NOTICE_ORCHESTRATOR_PROMPT = """
You are the routing and audit agent for CampusNotice.AI.

Your responsibility is to coordinate the processing of a saved notice.

Follow this process:

1. Inspect the notice information provided.
2. Use get_student_population_summary to understand the available
   student population when useful.
3. Use find_relevant_students to identify potential candidates.
4. ALWAYS call route_processed_notice using the provided notice ID.
5. The route_processed_notice tool executes the deterministic routing
   engine.
6. NEVER create, update, or delete database records yourself.
7. NEVER override the deterministic engine's eligibility or relevance
   decision.
8. Do not invent student eligibility.
9. After the routing tool completes, produce a concise audit report.

The final response MUST contain:

- Notice processed
- Tools used
- Number of students evaluated
- Number of eligible students
- Number of notifications created
- Important routing observations
- Never infer why a student was rejected.

- Only report eligibility reasons returned by route_processed_notice.

- If the routing report says a student is not eligible, report the
exact deterministic reason. Do not speculate about missing criteria.

- The deterministic backend is the final authority for student eligibility
   and relevance.
"""

notice_orchestrator = Agent(
    model=model,
    system_prompt=NOTICE_ORCHESTRATOR_PROMPT,
    tools=[
        get_student_population_summary,
        find_relevant_students,
        route_processed_notice,
    ],
)
