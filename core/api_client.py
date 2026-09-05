import os

import requests

from core.schemas import Outline, Slide, SlidePlan

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def call_outline_api(text: str, slide_count: int | None) -> Outline:
    response = requests.post(
        f"{API_BASE_URL}/outline",
        json={"text": text, "slide_count": slide_count},
        timeout=120,
    )
    response.raise_for_status()
    return Outline(**response.json()["outline"])


def call_content_api(
    outline: Outline,
    original_text: str,
    chart_preference: str = "auto",
    include_speaker_notes: bool = False,
) -> SlidePlan:
    response = requests.post(
        f"{API_BASE_URL}/content",
        json={
            "outline": outline.model_dump(),
            "original_text": original_text,
            "chart_preference": chart_preference,
            "include_speaker_notes": include_speaker_notes,
        },
        timeout=180,
    )
    response.raise_for_status()
    return SlidePlan(**response.json()["plan"])


def call_regenerate_slide_api(presentation_title: str, slide: Slide, instructions: str) -> Slide:
    response = requests.post(
        f"{API_BASE_URL}/regenerate-slide",
        json={
            "presentation_title": presentation_title,
            "slide": slide.model_dump(),
            "instructions": instructions,
        },
        timeout=60,
    )
    response.raise_for_status()
    return Slide(**response.json()["slide"])
