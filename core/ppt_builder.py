from io import BytesIO

from pptx import Presentation
from pptx.util import Inches

from core.schemas import SlidePlan


def build_pptx(plan: SlidePlan) -> BytesIO:
    prs = Presentation()

    title_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_layout)
    slide.shapes.title.text = plan.presentation_title
    slide.placeholders[1].text = "Generated with AI PPT Generator"

    bullet_layout = prs.slide_layouts[1]
    for slide_data in plan.slides:
        slide = prs.slides.add_slide(bullet_layout)
        slide.shapes.title.text = slide_data.title

        body = slide.placeholders[1]
        text_frame = body.text_frame
        text_frame.clear()

        for i, bullet in enumerate(slide_data.bullets):
            if i == 0:
                text_frame.text = bullet
            else:
                paragraph = text_frame.add_paragraph()
                paragraph.text = bullet

    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer
