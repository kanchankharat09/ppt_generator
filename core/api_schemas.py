from pydantic import BaseModel

from core.schemas import Outline, Slide, SlidePlan


class OutlineRequest(BaseModel):
    text: str
    slide_count: int | None = None


class ContentRequest(BaseModel):
    outline: Outline
    original_text: str = ""


class RegenerateSlideRequest(BaseModel):
    presentation_title: str
    slide: Slide
    instructions: str = ""


class OutlineResponse(BaseModel):
    outline: Outline


class ContentResponse(BaseModel):
    plan: SlidePlan


class SlideResponse(BaseModel):
    slide: Slide
