#utils.py

import PyPDF2
import uuid

def read_pdf(file) -> str:
    """
    Extracts text from a PDF file.
    """
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def split_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """
    Splits text into overlapping chunks.
    Useful later for retrieval-based approaches.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def generate_session_id() -> str:
    """
    Generates a unique session ID.
    """
    return str(uuid.uuid4())
