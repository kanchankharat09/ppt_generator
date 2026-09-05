from pydantic import BaseModel, Field


class ChartData(BaseModel):
    chart_type: str  # "bar", "line", or "pie"
    categories: list[str]
    values: list[float]
    series_name: str = "Series 1"


class ImageAttachment(BaseModel):
    filename: str
    description: str = ""
    placement: str = "auto"  # "auto", "title", or a 1-based slide number as string


class Slide(BaseModel):
    title: str
    bullets: list[str] = Field(default_factory=list)
    chart: ChartData | None = None
    image_filenames: list[str] = Field(default_factory=list)
    notes: str = ""


class SlidePlan(BaseModel):
    presentation_title: str
    slides: list[Slide]
    title_slide_image_filenames: list[str] = Field(default_factory=list)


class OutlineItem(BaseModel):
    title: str
    focus: str


class Outline(BaseModel):
    presentation_title: str
    items: list[OutlineItem]
