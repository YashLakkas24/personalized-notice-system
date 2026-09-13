import os

from strands import Agent, tool
from dotenv import load_dotenv
from strands.models.openai import OpenAIModel

from app.agents.prompts import NOTICE_SYSTEM_PROMPT
from app.schemas.notice import NoticeMetadata
from app.agents.tools import get_student_population_summary

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not configured.",tools=[get_student_population_summary])


model = OpenAIModel(
    client_args={
        "api_key": OPENAI_API_KEY,
    },
    model_id="gpt-4o",
    params={
        "temperature": 0.1,
        "max_tokens": 1200,
    },
)

notice_agent = Agent(model=model, system_prompt=NOTICE_SYSTEM_PROMPT)


def process_new_notice(raw_text: str) -> NoticeMetadata:

    if not raw_text or not raw_text.strip():
        raise ValueError("Notice text cannot be empty.")

    result = notice_agent(
        f"""
        Analyze the following college notice.

        RAW NOTICE:
        ----------------
        {raw_text}
        ----------------

        Extract all available information according to the NoticeMetadata schema.
        Do not invent missing information.
""",
        structured_output_model=NoticeMetadata,
    )
    return result.structured_output
