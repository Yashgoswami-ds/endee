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
