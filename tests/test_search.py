from search import search, _search_local


def test_search_empty_query_returns_error():
    result = search("   ")
    assert result["success"] is False
    assert "Please enter a search query" in result["error"]


def test_search_local_requires_endee(monkeypatch):
    monkeypatch.setattr("search.endee_configured", lambda: False)
    results, error = _search_local("python", source_mode="local", top_k=3)
    assert results == []
    assert "Endee is required" in error


def test_invalid_source_mode_falls_back_to_all(monkeypatch):
    monkeypatch.setattr("search._search_local", lambda *args, **kwargs: ([], "no local"))
    monkeypatch.setattr("search._search_online_wikipedia", lambda *args, **kwargs: ([{"text": "online", "score": 0.8, "source": "online"}], None))
    result = search("test query", source_mode="invalid")
    assert result["success"] is True
    assert result["source_mode"] == "all"
