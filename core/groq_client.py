import json
import os

from groq import Groq

from core.schemas import Outline, Slide, SlidePlan

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
- Unless the user specifies an exact number of slides, produce between 5 and 10 slides
  based on how much content there is.
- If the user specifies a number of slides, produce exactly that many.
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


def generate_slide_plan(user_text: str, slide_count: int | None = None) -> SlidePlan:
    client = get_client()

    if slide_count:
        user_text = f"{user_text}\n\nPlease create exactly {slide_count} slides."

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


OUTLINE_SYSTEM_PROMPT = """You are a presentation planning assistant.
Given content/instructions from the user, decide the best slide structure for a
PowerPoint presentation. Do NOT write full bullet content yet — just an outline.

Respond with ONLY valid JSON, no extra text, matching exactly this shape:
{
  "presentation_title": "string",
  "items": [
    {"title": "string", "focus": "one sentence describing what this slide should cover"}
  ]
}

Rules:
- Unless the user specifies an exact number of slides, produce between 5 and 10 items
  based on how much content there is.
- If the user specifies a number of slides, produce exactly that many items.
- Only include sections that make sense for this content (e.g. a technical project might need
  Problem, Architecture, Implementation, Results; a business presentation might need
  Problem, Solution, Benefits, Impact). Do not force a fixed template.
- Do not include markdown formatting, backticks, or commentary outside the JSON.
"""


def plan_outline(user_text: str, slide_count: int | None = None) -> Outline:
    client = get_client()

    if slide_count:
        user_text = f"{user_text}\n\nPlease create exactly {slide_count} slides."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": OUTLINE_SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    return Outline(**data)


CONTENT_SYSTEM_PROMPT = """You are a presentation content writer.
You are given an approved slide outline (titles + focus for each slide).
Write the full bullet content for every slide, staying on each slide's stated focus.

If a slide's content is fundamentally a numeric comparison (e.g. values across categories,
years, groups, or options) and a chart would communicate it better than bullets, include a
"chart" field for that slide with the extracted data. Only add a chart when there is genuine
numeric data to plot - do not invent numbers, and do not force a chart onto slides that are
not naturally comparative/numeric.

Respond with ONLY valid JSON, no extra text, matching exactly this shape:
{
  "presentation_title": "string",
  "slides": [
    {
      "title": "string",
      "bullets": ["string", "string"],
      "chart": {
        "chart_type": "bar | line | pie",
        "categories": ["string", "string"],
        "values": [0, 0],
        "series_name": "string"
      }
    }
  ]
}

Rules:
- Produce exactly one slide per outline item, in the same order, using the same titles.
- The "chart" field is optional - omit it entirely (or set it to null) for slides without
  genuine numeric/comparative data.
- When a chart is included, still include 2-4 short bullets summarizing the key takeaway.
- Use "bar" for comparisons across categories, "line" for trends over time, "pie" for
  proportions/percentages that sum to a whole.
- Each slide should have 2-5 short, concise bullet points (max ~12 words each).
- Do not include markdown formatting, backticks, or commentary outside the JSON.
"""


def generate_content_from_outline(
    outline: Outline, original_text: str = "", chart_preference: str = "auto"
) -> SlidePlan:
    client = get_client()

    outline_json = outline.model_dump_json()
    user_message = f"Approved outline:\n{outline_json}\n"

    if original_text.strip():
        user_message += f"\nOriginal source content for reference:\n{original_text.strip()}\n"

    if chart_preference == "none":
        user_message += "\nDo not include any charts on any slide.\n"
    elif chart_preference != "auto":
        user_message += (
            f"\nWhen a slide has chart-worthy data, use chart_type '{chart_preference}'.\n"
        )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": CONTENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    return SlidePlan(**data)


QUALITY_CHECK_SYSTEM_PROMPT = """You are a presentation quality reviewer.
You are given a full slide plan (title + bullets per slide). Check it for:
- Bullets that are too long or read like full sentences/paragraphs instead of concise points.
- Repetition of the same point across multiple slides.
- Vague or generic bullets that don't say anything specific.
- Poor logical flow from one slide to the next.

If you find real issues, rewrite ONLY the slides that need fixing to address them, keeping
good slides unchanged. If the plan is already fine, return it exactly as given.

Respond with ONLY valid JSON, no extra text, matching exactly this shape:
{
  "presentation_title": "string",
  "slides": [
    {"title": "string", "bullets": ["string", "string"]}
  ]
}

Rules:
- Keep the same number of slides and the same order.
- Each slide should have 3-5 short, concise bullet points (max ~12 words each).
- Do not include markdown formatting, backticks, or commentary outside the JSON.
"""


def review_and_revise(plan: SlidePlan) -> SlidePlan:
    client = get_client()

    plan_json = plan.model_dump_json()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": QUALITY_CHECK_SYSTEM_PROMPT},
            {"role": "user", "content": f"Slide plan to review:\n{plan_json}"},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    revised_plan = SlidePlan(**data)

    # The quality-check prompt doesn't handle chart data, so re-attach the original
    # chart for each slide (order/count is guaranteed unchanged by the prompt's rules).
    if len(revised_plan.slides) == len(plan.slides):
        for revised_slide, original_slide in zip(revised_plan.slides, plan.slides):
            revised_slide.chart = original_slide.chart

    return revised_plan


REGENERATE_SLIDE_SYSTEM_PROMPT = """You are a presentation planning assistant.
The user wants a single slide regenerated, still on the same topic.
If the user gives specific instructions for the change, follow them exactly.
Otherwise, just rephrase or approach the same content differently.

Respond with ONLY valid JSON, no extra text, matching exactly this shape:
{"title": "string", "bullets": ["string", "string"]}

Rules:
- 3-5 short bullet points, max ~12 words each.
- Keep it on the same topic/section as the original slide unless the instructions say otherwise.
- No markdown, backticks, or commentary outside the JSON.
"""


def regenerate_slide(
    presentation_title: str, original_slide: Slide, instructions: str = ""
) -> Slide:
    client = get_client()

    user_message = (
        f"Presentation title: {presentation_title}\n"
        f"Current slide title: {original_slide.title}\n"
        f"Current bullets: {original_slide.bullets}\n"
    )

    if instructions.strip():
        user_message += f"Instructions for this regeneration: {instructions.strip()}\n"

    user_message += "Regenerate this slide."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": REGENERATE_SLIDE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    return Slide(**data)


IMAGE_PLACEMENT_SYSTEM_PROMPT = """You are a presentation assistant.
You are given a description of an image and a list of slides (index, title, bullets).
Pick the single best slide index for this image, based on how well its content
matches the image's description.

Respond with ONLY valid JSON, no extra text, matching exactly this shape:
{"slide_index": 0}

Rules:
- slide_index must be one of the given indices.
- If nothing matches well, pick the slide whose topic is closest.
"""


def choose_image_slide(description: str, plan: SlidePlan) -> int:
    """Returns the best-matching slide index (0-based) for an image, using Groq."""
    client = get_client()

    slides_summary = [
        {"index": i, "title": s.title, "bullets": s.bullets} for i, s in enumerate(plan.slides)
    ]

    user_message = f"Image description: {description}\n\nSlides:\n{json.dumps(slides_summary)}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": IMAGE_PLACEMENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    index = data.get("slide_index", 0)
    return max(0, min(index, len(plan.slides) - 1))
