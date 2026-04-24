"""Handle PDF upload and text extraction."""

import os
from pathlib import Path

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


UPLOAD_FOLDER = os.path.join("data", "uploads")
KNOWLEDGE_FILE = os.path.join("data", "knowledge.txt")


def ensure_upload_folder():
    """Create upload folder if it doesn't exist."""
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)


def extract_pdf_text(pdf_path):
    """Extract text from PDF file."""
    if not PDF_AVAILABLE:
        return None, "PyPDF2 not installed. Run: pip install PyPDF2"

    try:
        text_chunks = []
        with open(pdf_path, "rb") as file:
            pdf_reader = PdfReader(file)
            num_pages = len(pdf_reader.pages)

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_chunks.append(text)

        return text_chunks, None
    except Exception as e:
        return None, f"Error extracting PDF: {str(e)}"


def save_pdf_text_to_knowledge(pdf_name, text_chunks):
    """Save extracted PDF text to knowledge.txt."""
    if not text_chunks:
        return False

    try:
        # Append to knowledge.txt
        with open(KNOWLEDGE_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- From PDF: {pdf_name} ---\n\n")
            for chunk in text_chunks:
                f.write(chunk.strip() + "\n\n")

        return True
    except Exception as e:
        print(f"Error saving PDF text: {e}")
        return False


def handle_pdf_upload(pdf_file):
    """
    Handle PDF file upload.
    
    Steps:
    1. Save uploaded file
    2. Extract text
    3. Save to knowledge base
    4. Return status
    """
    if not PDF_AVAILABLE:
        return False, "PDF support not installed"

    try:
        ensure_upload_folder()

        # Save uploaded file
        filename = pdf_file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        pdf_file.save(filepath)

        # Extract text
        text_chunks, error = extract_pdf_text(filepath)
        if error:
            return False, error

        # Save to knowledge base
        success = save_pdf_text_to_knowledge(filename, text_chunks)
        if success:
            return True, f"PDF '{filename}' successfully processed and added to knowledge base"
        else:
            return False, "Error saving PDF content to knowledge base"

    except Exception as e:
        return False, f"Error handling PDF: {str(e)}"


def list_uploaded_pdfs():
    """List all uploaded PDF files."""
    ensure_upload_folder()
    try:
        pdfs = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
        return pdfs
    except Exception:
        return []
