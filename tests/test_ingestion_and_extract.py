from src.link_extractor import extract_from_url
from src.pdf_handler import handle_pdf_upload


class DummyUpload:
    filename = "dummy.pdf"

    def save(self, _path):
        return None


def test_extract_invalid_url_returns_error():
    ok, message = extract_from_url("not-a-url")
    assert ok is False
    assert "Invalid URL" in message


def test_pdf_upload_requires_endee(monkeypatch):
    monkeypatch.setattr("src.pdf_handler.PDF_AVAILABLE", True)
    monkeypatch.setattr("src.pdf_handler.endee_configured", lambda: False)
    success, message = handle_pdf_upload(DummyUpload())
    assert success is False
    assert "Endee is required" in message
