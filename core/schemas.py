from pydantic import BaseModel, Field


class Slide(BaseModel):
    title: str
    bullets: list[str] = Field(default_factory=list)


class SlidePlan(BaseModel):
    presentation_title: str
    slides: list[Slide]


class OutlineItem(BaseModel):
    title: str
    focus: str


class Outline(BaseModel):
    presentation_title: str
    items: list[OutlineItem]
