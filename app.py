from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from core.groq_client import regenerate_slide
from core.pdf_utils import extract_text_from_pdfs
from core.ppt_builder import build_pptx
from core.workflow import run_content_step, run_outline_step

st.set_page_config(page_title="AI PPT Generator", page_icon="📊")
st.title("AI PPT Generator — Phase 4")
st.caption("Text/PDFs → Outline (your review) → Slide Content → python-pptx → Download")

for key, default in [
    ("outline", None),
    ("input_text", ""),
    ("plan", None),
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
                    st.session_state.outline = run_outline_step(
                        combined_text, slide_count=slide_count
                    )
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

    col_approve, col_restart = st.columns(2)

    with col_approve:
        if st.button("Approve outline and generate slides", type="primary"):
            if not outline.items:
                st.warning("Add at least one slide before generating.")
            else:
                with st.spinner("Writing slide content..."):
                    try:
                        st.session_state.plan = run_content_step(
                            outline, original_text=st.session_state.input_text
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate slide content: {e}")

    with col_restart:
        if st.button("Start over"):
            st.session_state.outline = None
            st.session_state.input_text = ""
            st.session_state.plan = None
            st.rerun()

# --- Step 3: final slide review, delete/regenerate, download ---

else:
    plan = st.session_state.plan
    st.success(f"Generated plan: {plan.presentation_title} ({len(plan.slides)} slides)")
    st.subheader("Review your slides")
    st.caption("Delete slides you don't want, or regenerate a slide before downloading.")

    slides_to_remove = []

    for i, slide in enumerate(plan.slides):
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(f"**Slide {i + 1}: {slide.title}**")
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
                            plan.slides[i] = regenerate_slide(
                                plan.presentation_title, slide, instructions=regen_instructions
                            )
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
            pptx_buffer = build_pptx(plan)

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
        st.rerun()
