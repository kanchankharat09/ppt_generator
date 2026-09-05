import os

import google.generativeai as genai
from PIL import Image
from io import BytesIO


def describe_image(image_bytes: bytes) -> str:
    """Uses Gemini to describe an image when the user didn't provide a description.
    Returns an empty string if no Gemini API key is configured, rather than inventing text.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return ""

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    image = Image.open(BytesIO(image_bytes))
    prompt = (
        "Describe this image in one short sentence, focused on what it shows "
        "(e.g. 'a system architecture diagram', 'a product screenshot', 'a company logo')."
    )

    response = model.generate_content([prompt, image])
    return response.text.strip()
