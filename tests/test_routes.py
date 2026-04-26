from app import app as flask_app


def test_home_route_ok():
    client = flask_app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_about_and_upload_routes_ok():
    client = flask_app.test_client()
    assert client.get("/about").status_code == 200
    assert client.get("/upload-pdf").status_code == 200


def test_home_shows_endee_status_badge(monkeypatch):
    monkeypatch.setattr("app.endee_configured", lambda: True)
    client = flask_app.test_client()
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert "Endee Status:" in body
    assert "Configured" in body


def test_history_and_documents_routes_ok(monkeypatch):
    monkeypatch.setattr(
        "app.load_search_history",
        lambda limit=50: [
            {
                "type": "search",
                "timestamp": "2026-04-24T10:00:00+00:00",
                "query": "sample question",
                "source_mode": "all",
                "language": "en",
                "success": True,
                "result_count": 1,
                "best_score": 0.98,
            }
        ],
    )
    monkeypatch.setattr("app.list_uploaded_pdfs", lambda: ["sample.pdf"])

    client = flask_app.test_client()
    assert client.get("/history").status_code == 200
    documents_response = client.get("/documents")
    assert documents_response.status_code == 200
    assert "sample.pdf" in documents_response.get_data(as_text=True)


def test_api_endpoints_return_json(monkeypatch):
    def fake_search(query, target_language="en", source_mode="all"):
        return {
            "success": True,
            "query": query,
            "target_language": target_language,
            "source_mode": source_mode,
            "results": [],
            "best_result": None,
        }

    monkeypatch.setattr("app.search", fake_search)
    monkeypatch.setattr("app.load_search_history", lambda limit=50: [{"type": "search"}])
    monkeypatch.setattr("app.list_uploaded_pdfs", lambda: ["sample.pdf"])

    client = flask_app.test_client()

    search_response = client.post("/api/search", json={"query": "sample question"})
    assert search_response.status_code == 200
    assert search_response.get_json()["success"] is True

    history_response = client.get("/api/history")
    assert history_response.status_code == 200
    assert history_response.get_json() == {"entries": [{"type": "search"}]}

    documents_response = client.get("/api/documents")
    assert documents_response.status_code == 200
    assert documents_response.get_json() == {"documents": ["sample.pdf"]}
