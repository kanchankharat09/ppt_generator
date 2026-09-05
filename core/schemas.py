from pydantic import BaseModel, Field


class ChartData(BaseModel):
    chart_type: str  # "bar", "line", or "pie"
    categories: list[str]
    values: list[float]
    series_name: str = "Series 1"


class Slide(BaseModel):
    title: str
    bullets: list[str] = Field(default_factory=list)
    chart: ChartData | None = None


class SlidePlan(BaseModel):
    presentation_title: str
    slides: list[Slide]


class OutlineItem(BaseModel):
    title: str
    focus: str


class Outline(BaseModel):
    presentation_title: str
    items: list[OutlineItem]
