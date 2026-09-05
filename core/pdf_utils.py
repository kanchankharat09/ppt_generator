from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages_text = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)

    return "\n".join(pages_text)


def extract_text_from_pdfs(uploaded_files) -> str:
    combined = []

    for uploaded_file in uploaded_files:
        text = extract_text_from_pdf(uploaded_file)
        combined.append(f"--- Content from {uploaded_file.name} ---\n{text}")

    return "\n\n".join(combined)
