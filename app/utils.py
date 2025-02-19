#utils.py
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file_bytes):
    """
    Given a PDF file (as bytes), extract text from each page.
    Returns a list of page texts.
    """
    reader = PyPDF2.PdfReader(file_bytes)
    pages = [page.extract_text() for page in reader.pages if page.extract_text()]
    return pages

def split_text(pages, chunk_size=500, chunk_overlap=50):
    """
    Given a list of page texts, join them and split into smaller chunks.
    Returns a list of text chunks.
    """
    full_text = "\n".join(pages)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # The split_text method returns a list of strings.
    chunks = splitter.split_text(full_text)
    return chunks

