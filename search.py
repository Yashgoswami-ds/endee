"""Search the knowledge base and improve results with Wikipedia API."""

import re
from urllib.parse import quote

import numpy as np
import requests
from sentence_transformers import SentenceTransformer

try:
    from endee import Endee
    ENDEE_AVAILABLE = True
except ImportError:
    ENDEE_AVAILABLE = False


HEADERS = {
    "User-Agent": "AI Knowledge Base Assistant/1.0 (student project)",
}
INDEX_NAME = "knowledge_base"
EMBEDDING_DIM = 384  # Dimension of all-MiniLM-L6-v2
ENDEE_URL = "http://localhost:8080/api/v1"


def tokenize(text):
    """Split text into simple lowercase words."""
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


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
    """Search Endee vector database for relevant paragraphs."""
    if not ENDEE_AVAILABLE:
        return {
            "title": "Endee SDK not available",
            "content": "Install it with: pip install endee",
            "source_url": "",
            "source_label": "",
            "confidence": 0,
        }

    try:
        client = Endee()
        client.set_base_url(ENDEE_URL)
        index = client.get_index(name=INDEX_NAME)

        # Generate query embedding
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            query_embedding = model.encode([query], convert_to_numpy=True, show_progress_bar=False)[0]
        except Exception:
            return {
                "title": "Embedding model unavailable",
                "content": "Could not generate query embedding.",
                "source_url": "",
                "source_label": "",
                "confidence": 0,
            }

        # Query Endee
        results = index.query(vector=query_embedding.tolist(), top_k=1)

        if not results:
            return {
                "title": "No match found",
                "content": "Try a different search term.",
                "source_url": "",
                "source_label": "",
                "confidence": 0,
            }

        # Get the best result
        best_result = results[0]
        paragraph_text = best_result.get("meta", {}).get("text", "")
        similarity = best_result.get("similarity", 0.0)

        # Convert similarity (0-1) to confidence percentage
        confidence = round(max(similarity, 0.0) * 100, 1)

        return {
            "title": "Local Knowledge Base",
            "content": paragraph_text,
            "source_url": "",
            "source_label": "Endee Vector DB",
            "confidence": confidence,
        }

    except Exception as e:
        return {
            "title": "Endee error",
            "content": f"Could not connect to Endee: {str(e)}",
            "source_url": "",
            "source_label": "",
            "confidence": 0,
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
    return search(query)
