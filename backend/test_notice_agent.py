
from app.agents.notice_agent import process_new_notice

notice = """
Applications are now open for the Inter-College AI Hackathon 2026.

Students from 2nd and 3rd year of all branches can participate.
Teams must contain 2 to 4 students.

The registration deadline is September 18, 2026.

Register at:
https://example.com/register

Participants will solve real-world AI problems.
"""


result = process_new_notice(notice)

print("\n--- STRUCTURED NOTICE ---")
print(result.model_dump_json(indent=2))
