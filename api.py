from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException

from core.api_schemas import (
    ContentRequest,
    ContentResponse,
    OutlineRequest,
    OutlineResponse,
    RegenerateSlideRequest,
    SlideResponse,
)
from core.groq_client import regenerate_slide
from core.workflow import run_content_step, run_outline_step

app = FastAPI(title="AI PPT Generator API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/outline", response_model=OutlineResponse)
def generate_outline(request: OutlineRequest):
    try:
        outline = run_outline_step(request.text, slide_count=request.slide_count)
        return OutlineResponse(outline=outline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/content", response_model=ContentResponse)
def generate_content(request: ContentRequest):
    try:
        plan = run_content_step(
            request.outline,
            original_text=request.original_text,
            chart_preference=request.chart_preference,
        )
        return ContentResponse(plan=plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regenerate-slide", response_model=SlideResponse)
def regenerate_slide_endpoint(request: RegenerateSlideRequest):
    try:
        slide = regenerate_slide(
            request.presentation_title, request.slide, instructions=request.instructions
        )
        return SlideResponse(slide=slide)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
