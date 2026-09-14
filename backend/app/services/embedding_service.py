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
            max_tokens=250,
            messages=[
                {
                    "role": "system",
                    "content": """
                        You are a student preference expansion engine.

                        The student may describe their interests vaguely or in very few words.

                        Expand the student's statement into a rich but accurate list of
                        topics, activities, opportunities, events and related terms that
                        should be considered relevant.

                        Examples:

                        "football"
                        → football, soccer, football competitions, football tournaments,
                        football matches, football team, football trials, football training,
                        inter-college football, sports competitions

                        "AI"
                        → artificial intelligence, machine learning, deep learning,
                        generative AI, LLM, NLP, computer vision, AI hackathons,
                        AI workshops, AI projects, AI competitions

                        "coding"
                        → programming, software development, coding competitions,
                        hackathons, competitive programming, programming workshops,
                        developer events, software engineering

                        Rules:
                        - Preserve the student's actual intent.
                        - Expand broad interests aggressively enough to avoid missing
                        relevant opportunities.
                        - Do NOT add unrelated career interests.
                        - Do NOT invent specific organizations or events.
                        - Return ONLY a comma-separated list of concepts and related terms.
                        """,
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

    except Exception as e:
        print(f"Preference normalization failed: {e}")
        normalized = preferences

    embedding_text = f"""
        Original student requirements:
        {preferences}

        Expanded matching concepts:
        {normalized}
    """

    return create_embedding(embedding_text)


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)
