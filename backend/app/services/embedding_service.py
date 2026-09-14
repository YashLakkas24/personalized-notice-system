import os
import numpy as np

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


EMBEDDING_MODEL = "text-embedding-3-small"


def create_embedding(text: str) -> list[float]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)

    return response.data[0].embedding


PREFERENCE_NORMALIZATION_MODEL = "gpt-4o"


def create_preference_embedding(preferences: str) -> list[float]:
    preferences = preferences.strip()

    if not preferences:
        raise ValueError("Preferences cannot be empty.")

    try:
        response = client.chat.completions.create(
            model=PREFERENCE_NORMALIZATION_MODEL,
            temperature=0,
            max_tokens=180,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You normalize student preferences for semantic search. "
                        "Return ONLY a concise comma-separated list of concepts, "
                        "activities, opportunities, events, competitions, "
                        "programs, and related terms implied by the student's "
                        "preference. Do not invent unrelated interests."
                    ),
                },
                {
                    "role": "user",
                    "content": preferences,
                },
            ],
        )

        normalized = (response.choices[0].message.content or "").strip()

        if not normalized:
            normalized = preferences

    except Exception:
        normalized = preferences

    embedding_text = (
        f"Student requirements and interests: {preferences}. "
        f"Related concepts for matching: {normalized}"
    )

    return create_embedding(embedding_text)


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)
