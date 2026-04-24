from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime, timezone

from dotenv import load_dotenv

from search import search
from pdf_handler import handle_pdf_upload
from translator import SUPPORTED_LANGUAGES, is_available as translator_available
from link_extractor import extract_from_url
from endee_api import is_configured as endee_configured


load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

# Configuration
UPLOAD_FOLDER = os.path.join("data", "uploads")
FEEDBACK_FILE = os.path.join("data", "feedback.jsonl")
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_feedback(feedback_data):
    """Persist user feedback in JSONL format for later review."""
    os.makedirs("data", exist_ok=True)
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(feedback_data, ensure_ascii=False) + "\n")


@app.route("/", methods=["GET", "POST"])
def index():
    """Main search page."""
    query = ""
    search_result = None
    error_message = ""
    link_url = ""
    extracted_link = None
    link_error_message = ""
    endee_status = "Configured" if endee_configured() else "Not Configured"
    language = request.args.get("language", "en")
    source_mode = request.args.get("source", "all")
    
    if request.method == "POST":
        action = request.form.get("action", "search")

        if action == "extract_link":
            link_url = request.form.get("link_url", "").strip()

            try:
                success, result = extract_from_url(link_url)
                if success:
                    extracted_link = result
                else:
                    link_error_message = result
                    logger.warning("url_extract_failed url=%s reason=%s", link_url, result)
            except Exception as error:
                logger.exception("url_extract_exception url=%s", link_url)
                link_error_message = f"Unexpected extraction error: {str(error)}"
        else:
            # Search flow
            query = request.form.get("question", "").strip()
            language = request.form.get("language", language)
            source_mode = request.form.get("source_mode", source_mode)

            if query:
                try:
                    search_result = search(query, target_language=language, source_mode=source_mode)
                except Exception as error:
                    logger.exception(
                        "search_exception source_mode=%s language=%s", source_mode, language
                    )
                    search_result = {"success": False, "error": f"Unexpected search error: {str(error)}"}

                if language != "en" and not translator_available():
                    flash("Selected language translation is unavailable. Install: pip install deep-translator", "error")

                if search_result and not search_result.get("success"):
                    error_message = search_result.get("error", "Search failed")
    
    return render_template(
        "index.html",
        query=query,
        search_result=search_result,
        error_message=error_message,
        languages=SUPPORTED_LANGUAGES,
        current_language=language,
        current_source=source_mode,
        link_url=link_url,
        extracted_link=extracted_link,
        link_error_message=link_error_message,
        endee_status=endee_status,
    )


@app.route("/feedback", methods=["POST"])
def feedback():
    """Store user feedback for answer quality tracking."""
    rating = request.form.get("rating", "").strip().lower()
    query = request.form.get("query", "").strip()
    source_mode = request.form.get("source", "all").strip().lower()
    language = request.form.get("language", "en").strip().lower()
    result_text = request.form.get("result_text", "").strip()
    comment = request.form.get("comment", "").strip()

    if rating not in {"like", "dislike"}:
        flash("Invalid feedback type.", "error")
        return redirect(url_for("index", language=language, source=source_mode))

    feedback_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rating": rating,
        "query": query,
        "source_mode": source_mode,
        "language": language,
        "result_text": result_text,
        "comment": comment,
    }

    try:
        save_feedback(feedback_data)
        flash("Thanks! Feedback saved.", "success")
    except Exception:
        logger.exception("feedback_save_failed")
        flash("Could not save feedback. Try again.", "error")

    return redirect(url_for("index", language=language, source=source_mode))


@app.route("/upload-pdf", methods=["GET", "POST"])
def upload_pdf():
    """Handle PDF upload and text extraction."""
    if request.method == "POST":
        # Check if file is present
        if "pdf_file" not in request.files:
            flash("No file selected", "error")
            return redirect(url_for("upload_pdf"))
        
        file = request.files["pdf_file"]
        
        if file.filename == "":
            flash("No file selected", "error")
            return redirect(url_for("upload_pdf"))
        
        if not allowed_file(file.filename):
            flash("Only PDF files allowed", "error")
            return redirect(url_for("upload_pdf"))
        
        # Handle PDF upload
        success, message = handle_pdf_upload(file)
        logger.info("pdf_upload_processed success=%s filename=%s", success, file.filename)
        
        if success:
            flash(f"✓ {message}", "success")
        else:
            flash(f"✗ {message}", "error")
        
        return redirect(url_for("upload_pdf"))
    
    return render_template("upload_pdf.html")


@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
