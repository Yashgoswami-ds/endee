"""Search the knowledge base and improve results with Wikipedia API."""

import os
import pickle
import re
from urllib.parse import quote

import numpy as np
import requests
from sentence_transformers import SentenceTransformer


DB_FILE = os.path.join("db", "vectors.pkl")
HEADERS = {
    "User-Agent": "AI Knowledge Base Assistant/1.0 (student project)",
}


def tokenize(text):
    """Split text into simple lowercase words."""
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def load_database():
    """Load the saved paragraphs and embeddings."""
    if not os.path.exists(DB_FILE):
        raise FileNotFoundError("Embedding database not found. Run embed_store.py first.")

    with open(DB_FILE, "rb") as file:
        data = pickle.load(file)

    return data


def fetch_wikipedia_result(query):
    """Try to get a direct Wikipedia answer for the query."""
    search_url = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&list=search&srsearch={quote(query)}&utf8=1&format=json&srlimit=1"
    )
    response = requests.get(search_url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    search_data = response.json()

    search_results = search_data.get("query", {}).get("search", [])
    if not search_results:
        return None

    title = search_results[0].get("title", "")
    if not title:
        return None

    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'))}"
    summary_response = requests.get(summary_url, headers=HEADERS, timeout=15)
    summary_response.raise_for_status()
    summary_data = summary_response.json()

    extract = summary_data.get("extract", "").strip()
    if not extract:
        return None

    return {
        "title": summary_data.get("title", title),
        "content": extract,
        "source_url": summary_data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        "source_label": "Wikipedia",
        "confidence": 100,
    }


def cosine_similarity(vector_a, vector_b):
    """Compute cosine similarity between two vectors."""
    vector_a = np.array(vector_a)
    vector_b = np.array(vector_b)

    denominator = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if denominator == 0:
        return 0.0

    return float(np.dot(vector_a, vector_b) / denominator)


def semantic_search(query):
    """Return the most relevant paragraph from the stored knowledge file."""
    data = load_database()
    paragraphs = data.get("paragraphs", [])
    embeddings = np.array(data.get("embeddings", []))
    embedding_type = data.get("embedding_type", "sentence-transformer")
    vocabulary = data.get("vocabulary", [])

    if len(paragraphs) == 0:
        return {
            "title": "No local data found",
            "content": "Please run fetch_data.py and embed_store.py.",
            "source_url": "",
            "source_label": "",
            "confidence": 0,
        }

    if embedding_type == "sentence-transformer":
        try:
            model = SentenceTransformer(data.get("model_name", "all-MiniLM-L6-v2"), local_files_only=True)
            query_embedding = model.encode([query], convert_to_numpy=True, show_progress_bar=False)[0]
        except Exception:
            embedding_type = "simple-bow"

    if embedding_type == "simple-bow":
        word_counts = {word: 0 for word in vocabulary}
        for word in tokenize(query):
            if word in word_counts:
                word_counts[word] += 1
        query_embedding = np.array([word_counts[word] for word in vocabulary], dtype=float)

    best_score = -1.0
    best_paragraph = ""

    for index, paragraph_embedding in enumerate(embeddings):
        score = cosine_similarity(query_embedding, paragraph_embedding)
        if score > best_score:
            best_score = score
            best_paragraph = paragraphs[index]

    return {
        "title": "Local Knowledge Base",
        "content": best_paragraph,
        "source_url": "",
        "source_label": "Local data",
        "confidence": round(max(best_score, 0.0) * 100, 1),
    }


def search(query):
    """Return the best result, starting with Wikipedia API."""
    query = query.strip()
    if not query:
        return {"title": "", "content": "", "source_url": "", "source_label": "", "confidence": 0}

    try:
        wikipedia_result = fetch_wikipedia_result(query)
        if wikipedia_result:
            return wikipedia_result
    except requests.RequestException:
        pass

    try:
        return semantic_search(query)
    except Exception:
        return {
            "title": "No result found",
            "content": "Please try a different question.",
            "source_url": "",
            "source_label": "",
            "confidence": 0,
        }


def search_knowledge_base(query):
    """Keep a simple wrapper for the Flask app."""
    if not query.strip():
        return {"title": "", "content": "", "source_url": "", "source_label": "", "confidence": 0}
    return search(query)
