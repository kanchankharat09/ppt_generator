from io import BytesIO

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches, Pt

from core.schemas import Slide, SlidePlan

CHART_TYPE_MAP = {
    "bar": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "line": XL_CHART_TYPE.LINE_MARKERS,
    "pie": XL_CHART_TYPE.PIE,
}


def _add_bullet_slide(prs: Presentation, bullet_layout, slide_data: Slide):
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


def _add_chart_slide(prs: Presentation, title_only_layout, slide_data: Slide):
    slide = prs.slides.add_slide(title_only_layout)
    slide.shapes.title.text = slide_data.title

    # Bullets go in a small text box above the chart, since this layout has no body placeholder.
    if slide_data.bullets:
        textbox = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(1))
        text_frame = textbox.text_frame
        text_frame.word_wrap = True
        for i, bullet in enumerate(slide_data.bullets):
            paragraph = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
            paragraph.text = f"• {bullet}"
            paragraph.font.size = Pt(14)

    chart = slide_data.chart
    chart_data = CategoryChartData()
    chart_data.categories = chart.categories
    chart_data.add_series(chart.series_name, chart.values)

    xl_chart_type = CHART_TYPE_MAP.get(chart.chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED)

    slide.shapes.add_chart(
        xl_chart_type, Inches(1), Inches(2.4), Inches(8), Inches(4.2), chart_data
    )


def build_pptx(plan: SlidePlan) -> BytesIO:
    prs = Presentation()

    title_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_layout)
    slide.shapes.title.text = plan.presentation_title
    slide.placeholders[1].text = "Generated with AI PPT Generator"

    bullet_layout = prs.slide_layouts[1]
    title_only_layout = prs.slide_layouts[5]

    for slide_data in plan.slides:
        if slide_data.chart is not None:
            _add_chart_slide(prs, title_only_layout, slide_data)
        else:
            _add_bullet_slide(prs, bullet_layout, slide_data)

    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer
