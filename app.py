from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from core.groq_client import generate_slide_plan
from core.ppt_builder import build_pptx

st.set_page_config(page_title="AI PPT Generator", page_icon="📊")
st.title("AI PPT Generator — Phase 1")
st.caption("Text → Groq → Slide Plan → python-pptx → Download")

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
                plan = generate_slide_plan(user_text)
            except Exception as e:
                st.error(f"Failed to generate slide plan: {e}")
                st.stop()

        st.success(f"Generated plan: {plan.presentation_title} ({len(plan.slides)} slides)")

        with st.expander("Preview slide plan"):
            for i, slide in enumerate(plan.slides, start=1):
                st.markdown(f"**Slide {i}: {slide.title}**")
                for bullet in slide.bullets:
                    st.markdown(f"- {bullet}")

        with st.spinner("Building PowerPoint file..."):
            pptx_buffer = build_pptx(plan)

        st.download_button(
            label="Download .pptx",
            data=pptx_buffer,
            file_name="presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
