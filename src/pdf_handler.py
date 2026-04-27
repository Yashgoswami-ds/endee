"""Handle PDF upload and text extraction."""

import os
import logging
from pathlib import Path
from werkzeug.utils import secure_filename
from src.endee_api import store_to_endee, is_configured as endee_configured

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


UPLOAD_FOLDER = os.path.join("data", "uploads")
KNOWLEDGE_FILE = os.path.join("data", "knowledge.txt")
logger = logging.getLogger(__name__)


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
        logger.exception("pdf_extract_exception path=%s", pdf_path)
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
        logger.exception("pdf_save_text_failed pdf_name=%s", pdf_name)
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

    if not endee_configured():
        return False, "Endee is required. Configure ENDEE_API_KEY in .env"

    try:
        ensure_upload_folder()

        # Save uploaded file
        filename = secure_filename(pdf_file.filename or "")
        if not filename:
            return False, "Invalid file name"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        pdf_file.save(filepath)

        # Extract text
        text_chunks, error = extract_pdf_text(filepath)
        if error:
            return False, error

        # Save to knowledge base
        success = save_pdf_text_to_knowledge(filename, text_chunks)
        if not success:
            return False, "Error saving PDF content to knowledge base"

        stored, store_message = store_to_endee(text_chunks)
        if not stored:
            logger.warning("pdf_endee_sync_failed filename=%s reason=%s", filename, store_message)
            return False, f"PDF text extracted, but Endee upsert failed: {store_message}"

        logger.info("pdf_upload_success filename=%s chunks=%s", filename, len(text_chunks))
        return True, f"PDF '{filename}' processed and synced to Endee"

    except Exception as e:
        logger.exception("pdf_upload_exception")
        return False, f"Error handling PDF: {str(e)}"


def list_uploaded_pdfs():
    """List all uploaded PDF files."""
    ensure_upload_folder()
    try:
        pdfs = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
        return pdfs
    except Exception:
        return []
