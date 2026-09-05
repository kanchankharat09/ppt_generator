from io import BytesIO

from PIL import Image


def read_image_bytes(uploaded_file) -> bytes:
    return uploaded_file.getvalue()


def get_image_size_inches(image_bytes: bytes, max_width_in: float, max_height_in: float):
    """Returns (width, height) in inches that fit within the max box, preserving aspect ratio."""
    with Image.open(BytesIO(image_bytes)) as img:
        width_px, height_px = img.size

    aspect_ratio = width_px / height_px

    width_in = max_width_in
    height_in = width_in / aspect_ratio

    if height_in > max_height_in:
        height_in = max_height_in
        width_in = height_in * aspect_ratio

    return width_in, height_in
