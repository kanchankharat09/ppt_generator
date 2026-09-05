from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from core.api_client import call_content_api, call_outline_api, call_regenerate_slide_api
from core.gemini_client import describe_image
from core.groq_client import choose_image_slide
from core.image_utils import read_image_bytes
from core.pdf_utils import extract_text_from_pdfs
from core.ppt_builder import build_pptx
from core.schemas import ImageAttachment

st.set_page_config(page_title="AI PPT Generator", page_icon="📊")
st.title("AI PPT Generator — Phase 8")
st.caption("Streamlit → FastAPI → LangGraph → Groq → Charts/Images → python-pptx → Download")

for key, default in [
    ("outline", None),
    ("input_text", ""),
    ("plan", None),
    ("image_store", {}),
    ("image_attachments", []),
    ("images_placed", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Step 1: input + outline generation ---

if st.session_state.outline is None and st.session_state.plan is None:
    uploaded_pdfs = st.file_uploader(
        "Upload PDF(s) (optional)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    user_text = st.text_area(
        "Additional instructions or text (optional if you uploaded PDFs)",
        placeholder="e.g. Focus on the results section. Make it 10 slides for a client.",
        height=150,
    )

    slide_count_choice = st.selectbox(
        "Number of slides",
        options=["Auto (AI decides)", "3", "5", "7", "10", "12", "15"],
    )
    slide_count = None if slide_count_choice == "Auto (AI decides)" else int(slide_count_choice)

    st.subheader("Upload Images (optional)")
    st.caption(
        "Describe each image or leave it blank to let AI figure it out (requires a "
        "Gemini API key set as GEMINI_API_KEY - Groq's models can't see images)."
    )

    uploaded_images = st.file_uploader(
        "Upload image(s) (optional)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    image_attachments = []
    if uploaded_images:
        for img_file in uploaded_images:
            with st.container(border=True):
                st.image(img_file, width=200)

                description = st.text_input(
                    "Describe this image or tell AI how you want to use it",
                    key=f"img_desc_{img_file.name}",
                    placeholder="e.g. This is our system architecture. Put it on the Architecture slide.",
                )

                placement_choice = st.selectbox(
                    "Placement",
                    options=["Let AI decide", "Title slide", "Specific slide"],
                    key=f"img_placement_{img_file.name}",
                )

                slide_number = None
                if placement_choice == "Specific slide":
                    slide_number = st.number_input(
                        "Slide number", min_value=1, step=1, key=f"img_slide_num_{img_file.name}"
                    )

                if placement_choice == "Title slide":
                    placement = "title"
                elif placement_choice == "Specific slide":
                    placement = str(int(slide_number))
                else:
                    placement = "auto"

                st.session_state.image_store[img_file.name] = read_image_bytes(img_file)
                image_attachments.append(
                    ImageAttachment(
                        filename=img_file.name, description=description, placement=placement
                    )
                )

    if st.button("Generate Outline", type="primary"):
        pdf_text = ""
        if uploaded_pdfs:
            with st.spinner("Extracting text from PDF(s)..."):
                try:
                    pdf_text = extract_text_from_pdfs(uploaded_pdfs)
                except Exception as e:
                    st.error(f"Failed to read PDF(s): {e}")
                    st.stop()

        combined_text = "\n\n".join(part for part in [pdf_text, user_text.strip()] if part)

        if not combined_text.strip():
            st.warning("Please enter some text or upload at least one PDF.")
        else:
            with st.spinner("Planning outline..."):
                try:
                    st.session_state.input_text = combined_text
                    st.session_state.image_attachments = image_attachments
                    st.session_state.outline = call_outline_api(combined_text, slide_count)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to plan outline: {e}")

# --- Step 2: outline review (add/remove/rename/reorder) ---

elif st.session_state.outline is not None and st.session_state.plan is None:
    outline = st.session_state.outline

    st.subheader(f"Proposed outline: {outline.presentation_title}")
    st.caption("Review before we write full slide content. Edit, reorder, add, or remove items.")

    outline.presentation_title = st.text_input(
        "Presentation title", value=outline.presentation_title
    )

    items_to_remove = []

    for i, item in enumerate(outline.items):
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([4, 4, 1, 1])

            with col1:
                item.title = st.text_input("Title", value=item.title, key=f"outline_title_{i}")
            with col2:
                item.focus = st.text_input("Focus", value=item.focus, key=f"outline_focus_{i}")
            with col3:
                if st.button("↑", key=f"up_{i}") and i > 0:
                    outline.items[i - 1], outline.items[i] = outline.items[i], outline.items[i - 1]
                    st.rerun()
            with col4:
                if st.button("✕", key=f"remove_{i}"):
                    items_to_remove.append(i)

    if items_to_remove:
        for index in sorted(items_to_remove, reverse=True):
            outline.items.pop(index)
        st.rerun()

    if st.button("+ Add slide"):
        from core.schemas import OutlineItem

        outline.items.append(OutlineItem(title="New slide", focus="Describe what this covers"))
        st.rerun()

    chart_choice = st.selectbox(
        "Charts",
        options=["Auto (AI decides)", "Bar", "Line", "Pie", "No charts"],
        help="Controls whether/which chart type is used for slides with numeric data.",
    )
    chart_preference = {
        "Auto (AI decides)": "auto",
        "Bar": "bar",
        "Line": "line",
        "Pie": "pie",
        "No charts": "none",
    }[chart_choice]

    col_approve, col_restart = st.columns(2)

    with col_approve:
        if st.button("Approve outline and generate slides", type="primary"):
            if not outline.items:
                st.warning("Add at least one slide before generating.")
            else:
                with st.spinner("Writing slide content and running a quality check..."):
                    try:
                        st.session_state.plan = call_content_api(
                            outline, st.session_state.input_text, chart_preference
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate slide content: {e}")

    with col_restart:
        if st.button("Start over"):
            st.session_state.outline = None
            st.session_state.input_text = ""
            st.session_state.plan = None
            st.session_state.image_store = {}
            st.session_state.image_attachments = []
            st.session_state.images_placed = False
            st.rerun()

# --- Step 3: final slide review, delete/regenerate, download ---

else:
    plan = st.session_state.plan

    if not st.session_state.images_placed and st.session_state.image_attachments:
        with st.spinner("Placing images on slides..."):
            for attachment in st.session_state.image_attachments:
                description = attachment.description.strip()

                if not description:
                    image_bytes = st.session_state.image_store.get(attachment.filename)
                    if image_bytes:
                        try:
                            description = describe_image(image_bytes)
                        except Exception:
                            description = ""

                if attachment.placement == "title":
                    plan.title_slide_image_filenames.append(attachment.filename)
                elif attachment.placement not in ("auto", "title"):
                    try:
                        slide_index = int(attachment.placement) - 1
                    except ValueError:
                        slide_index = 0
                    slide_index = max(0, min(slide_index, len(plan.slides) - 1))
                    plan.slides[slide_index].image_filenames.append(attachment.filename)
                else:
                    if description:
                        try:
                            slide_index = choose_image_slide(description, plan)
                            plan.slides[slide_index].image_filenames.append(attachment.filename)
                        except Exception:
                            plan.title_slide_image_filenames.append(attachment.filename)
                    else:
                        # No description available (no Gemini key and user left it blank) -
                        # fall back to the title slide rather than guessing.
                        plan.title_slide_image_filenames.append(attachment.filename)

        st.session_state.images_placed = True

    st.success(f"Generated plan: {plan.presentation_title} ({len(plan.slides)} slides)")
    st.subheader("Review your slides")
    st.caption("Delete slides you don't want, or regenerate a slide before downloading.")

    slides_to_remove = []

    for i, slide in enumerate(plan.slides):
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(f"**Slide {i + 1}: {slide.title}**")
                if slide.chart is not None:
                    st.caption(f"📊 {slide.chart.chart_type.title()} chart included")
                if slide.image_filenames:
                    st.caption(f"🖼️ Image(s): {', '.join(slide.image_filenames)}")
                for bullet in slide.bullets:
                    st.markdown(f"- {bullet}")
                regen_instructions = st.text_input(
                    "Regeneration instructions (optional)",
                    key=f"regen_instructions_{i}",
                    placeholder="e.g. make it shorter, add more about cost",
                )

            with col2:
                if st.button("Regenerate", key=f"regen_{i}"):
                    with st.spinner("Regenerating slide..."):
                        try:
                            new_slide = call_regenerate_slide_api(
                                plan.presentation_title, slide, regen_instructions
                            )
                            # Regeneration only rewrites text; keep the existing chart/images.
                            new_slide.chart = slide.chart
                            new_slide.image_filenames = slide.image_filenames
                            plan.slides[i] = new_slide
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to regenerate slide: {e}")

                if st.button("Delete", key=f"delete_{i}"):
                    slides_to_remove.append(i)

    if slides_to_remove:
        for index in sorted(slides_to_remove, reverse=True):
            plan.slides.pop(index)
        st.rerun()

    if not plan.slides:
        st.warning("All slides deleted. Nothing to download.")
    else:
        with st.spinner("Building PowerPoint file..."):
            pptx_buffer = build_pptx(plan, image_store=st.session_state.image_store)

        st.download_button(
            label="Download .pptx",
            data=pptx_buffer,
            file_name="presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

    if st.button("Start a new presentation"):
        st.session_state.outline = None
        st.session_state.input_text = ""
        st.session_state.plan = None
        st.session_state.image_store = {}
        st.session_state.image_attachments = []
        st.session_state.images_placed = False
        st.rerun()
