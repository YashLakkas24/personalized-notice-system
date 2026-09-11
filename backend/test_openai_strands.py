from strands import Agent
from strands.models.openai import OpenAIModel
from dotenv import load_dotenv

import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found")


model = OpenAIModel(
    client_args={
        "api_key": api_key,
    },
    model_id="gpt-4o",
)


agent = Agent(model=model)

response = agent("Reply with exactly: Strands OpenAI connection successful.")

print(response)
