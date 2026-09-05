import json
import os

from groq import Groq

from core.schemas import SlidePlan

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a presentation planning assistant.
Given a topic or text from the user, produce a slide plan for a PowerPoint presentation.

Respond with ONLY valid JSON, no extra text, matching exactly this shape:
{
  "presentation_title": "string",
  "slides": [
    {"title": "string", "bullets": ["string", "string"]}
  ]
}

Rules:
- Produce between 5 and 10 slides.
- Each slide should have 3-5 short bullet points.
- Keep bullets concise (max ~12 words each).
- Do not include markdown formatting, backticks, or commentary outside the JSON.
"""


def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to your .env file or environment variables."
        )
    return Groq(api_key=api_key)


def generate_slide_plan(user_text: str) -> SlidePlan:
    client = get_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    return SlidePlan(**data)
