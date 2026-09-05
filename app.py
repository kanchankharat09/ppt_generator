from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from core.groq_client import generate_slide_plan, regenerate_slide
from core.ppt_builder import build_pptx

st.set_page_config(page_title="AI PPT Generator", page_icon="📊")
st.title("AI PPT Generator — Phase 1")
st.caption("Text → Groq → Slide Plan → python-pptx → Download")

if "plan" not in st.session_state:
    st.session_state.plan = None

user_text = st.text_area(
    "What should the presentation be about?",
    placeholder="e.g. The history and future of renewable energy",
    height=150,
)

if st.button("Generate Presentation", type="primary"):
    if not user_text.strip():
        st.warning("Please enter a topic or some text first.")
    else:
        with st.spinner("Asking Groq to plan your slides..."):
            try:
                st.session_state.plan = generate_slide_plan(user_text)
            except Exception as e:
                st.error(f"Failed to generate slide plan: {e}")
                st.session_state.plan = None

plan = st.session_state.plan

if plan is not None:
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

            with col2:
                if st.button("Regenerate", key=f"regen_{i}"):
                    with st.spinner("Regenerating slide..."):
                        try:
                            plan.slides[i] = regenerate_slide(plan.presentation_title, slide)
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
