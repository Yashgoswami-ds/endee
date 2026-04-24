"""Utilities to extract readable text content from a web URL."""

from urllib.parse import urlparse
import re

import requests
from bs4 import BeautifulSoup


def _is_valid_url(url: str) -> bool:
    """Validate that URL has http/https scheme and hostname."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _clean_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph-like line breaks."""
    text = text.replace("\r", "\n")
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_from_url(url: str, max_chars: int = 12000) -> tuple:
    """
    Extract readable content from a URL.

    Returns:
        (True, {"url": str, "title": str, "content": str, "truncated": bool}) on success
        (False, error_message) on failure
    """
    if not url or not url.strip():
        return False, "Please enter a URL."

    normalized_url = url.strip()
    if not _is_valid_url(normalized_url):
        return False, "Invalid URL. Use a full link starting with http:// or https://"

    try:
        response = requests.get(
            normalized_url,
            timeout=15,
            headers={"User-Agent": "AI-Knowledge-Assistant/1.0"},
        )
        response.raise_for_status()
    except requests.RequestException as error:
        return False, f"Unable to fetch URL: {str(error)}"

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        return False, "URL did not return an HTML page."

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "form", "aside"]):
        tag.decompose()

    main_content = soup.find("article") or soup.find("main") or soup.body or soup
    extracted_text = _clean_text(main_content.get_text(separator="\n"))

    if not extracted_text:
        return False, "Could not extract readable content from this page."

    page_title = ""
    if soup.title and soup.title.string:
        page_title = soup.title.string.strip()

    truncated = len(extracted_text) > max_chars
    final_text = extracted_text[:max_chars].strip() if truncated else extracted_text

    return True, {
        "url": normalized_url,
        "title": page_title,
        "content": final_text,
        "truncated": truncated,
    }
