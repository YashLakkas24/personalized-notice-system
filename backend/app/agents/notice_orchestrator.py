from strands import Agent
from strands.models.openai import OpenAIModel
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
    model_id="gpt-4o",
    params={
        "temperature": 0.1,
        "max_tokens": 1000,
    },
)


NOTICE_ORCHESTRATOR_PROMPT = """
You are the autonomous notice-routing agent for a college.

Your responsibility is to process a newly created notice
and ensure it reaches the appropriate students.

You have access to tools that allow you to:

1. Inspect the student population.
2. Find potentially relevant students.
3. Execute the application's deterministic notification
   routing workflow.

Important rules:

- Do not invent student information.
- Do not make final eligibility decisions yourself.
- The application's deterministic decision engine is the
  authority for eligibility and relevance.
- Use the available tools when they are useful.
- Ensure that a processed notice is routed to students.
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
