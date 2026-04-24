"""Search logic with source control, relevance scoring, and translation."""

import os
import re
from urllib.parse import quote

import requests

from endee_api import search_endee, is_configured as endee_configured
from translator import translate_result


KNOWLEDGE_FILE = os.path.join("data", "knowledge.txt")

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "for", "with", "by", "as", "at", "from",
    "what", "which", "who", "whom", "why", "how", "when", "where",
    "and", "or", "but", "if", "then", "so", "than", "too", "very",
    "tell", "about", "me", "please", "can", "could", "would",
}


def get_best_result(results):
    """
    Select the best result from a list.
    
    Logic:
    - Find result with highest similarity score
    - Return that result
    """
    if not results:
        return None

    best = max(results, key=lambda x: x.get("score", 0))
    return best


def _tokenize(text):
    """Tokenize text and remove very short/low-signal words."""
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS]


def _parse_knowledge_entries(raw_text):
    """Parse knowledge file into entries tagged by source type."""
    entries = []
    chunks = [c.strip() for c in raw_text.split("\n\n") if c.strip()]

    current_source = "local"
    for chunk in chunks:
        if chunk.lower().startswith("--- from pdf:"):
            current_source = "pdf"
            continue

        entries.append({
            "text": chunk,
            "source": current_source,
        })

    return entries


def _load_local_entries(source_mode):
    """Load and filter local entries based on selected source mode."""
    if not os.path.exists(KNOWLEDGE_FILE):
        return []

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        raw_text = file.read()

    entries = _parse_knowledge_entries(raw_text)
    if source_mode == "pdf":
        return [e for e in entries if e["source"] == "pdf"]

    return entries


def _mock_search_entries(query, entries, top_k=3):
    """Score local entries with token overlap to reduce irrelevant answers."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    query_set = set(query_tokens)
    results = []

    for entry in entries:
        text = entry.get("text", "")
        text_tokens = _tokenize(text)
        if not text_tokens:
            continue

        text_set = set(text_tokens)
        overlap = len(query_set.intersection(text_set))
        if overlap == 0:
            continue

        token_frequency = sum(text_tokens.count(token) for token in query_tokens)
        coverage = overlap / max(len(query_set), 1)
        density = min(token_frequency / max(len(query_tokens) * 3, 1), 1.0)
        phrase_bonus = 0.2 if query.lower() in text.lower() else 0.0

        score = min((0.65 * coverage) + (0.25 * density) + phrase_bonus, 1.0)
        if score < 0.12:
            continue

        results.append({
            "text": text,
            "score": score,
            "source": entry.get("source", "local"),
        })

    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:top_k]


def _search_online_wikipedia(query, top_k=3):
    """Fetch top online results from Wikipedia APIs."""
    headers = {"User-Agent": "AI-Knowledge-Assistant/1.0"}
    results = []

    try:
        # First get likely topic titles for the query.
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "opensearch",
            "search": query,
            "limit": top_k,
            "namespace": 0,
            "format": "json",
        }
        search_response = requests.get(search_url, params=search_params, headers=headers, timeout=12)
        search_response.raise_for_status()
        search_data = search_response.json()
        titles = search_data[1] if len(search_data) > 1 else []

        if not titles:
            titles = [query]

        for idx, title in enumerate(titles[:top_k]):
            encoded_title = quote(title.replace(" ", "_"))
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
            summary_response = requests.get(summary_url, headers=headers, timeout=12)

            if summary_response.status_code != 200:
                continue

            summary = summary_response.json()
            extract = summary.get("extract", "").strip()
            final_title = summary.get("title", title)

            if not extract:
                continue

            results.append({
                "text": f"{final_title}\n{extract}",
                "score": max(0.55, 0.95 - (idx * 0.12)),
                "source": "online",
            })

        return results[:top_k], None

    except requests.RequestException as error:
        return [], f"Online search failed: {str(error)}"
    except Exception as error:
        return [], f"Online search error: {str(error)}"


def _search_local(query, source_mode="all", top_k=3):
    """Search local/PDF data strictly via Endee vector search."""
    if not endee_configured():
        return [], "Endee is required for local/PDF search. Configure ENDEE_API_KEY in .env"

    endee_results, endee_error = search_endee(query, top_k=top_k)
    if not endee_results:
        return [], endee_error or "No Endee results found"

    normalized = []
    for result in endee_results:
        normalized.append({
            "text": result.get("text", ""),
            "score": result.get("score", 0.0),
            "source": "local",
        })

    return normalized, None


def explain_result(best_result):
    """
    Generate explanation for why this result was selected.
    
    Args:
        best_result: The selected result dict
    
    Returns:
        Explanation string
    """
    if not best_result:
        return "No result to explain."

    score = best_result.get("score", 0)
    explanation = (
        f"This answer was selected because it has the highest similarity score "
        f"({score:.2f}) among the retrieved results."
    )
    return explanation


def search(query, target_language="en", source_mode="all"):
    """
    Main search function.
    
    source_mode:
    - all: combine local and online (top ranked 3)
    - pdf: only uploaded PDF content
    - online: only online API results
    """
    if not query.strip():
        return {
            "success": False,
            "error": "Please enter a search query",
            "results": [],
            "best_result": None,
            "explanation": ""
        }

    allowed_sources = {"all", "pdf", "online", "local"}
    if source_mode not in allowed_sources:
        source_mode = "all"

    results = []
    errors = []

    if source_mode == "online":
        online_results, online_error = _search_online_wikipedia(query, top_k=3)
        results = online_results
        if online_error:
            errors.append(online_error)
    elif source_mode == "pdf":
        local_results, local_error = _search_local(query, source_mode="pdf", top_k=3)
        results = local_results
        if local_error:
            errors.append(local_error)
    elif source_mode == "local":
        local_results, local_error = _search_local(query, source_mode="local", top_k=3)
        results = local_results
        if local_error:
            errors.append(local_error)
    else:
        # all mode: merge online and local and keep best 3
        local_results, local_error = _search_local(query, source_mode="all", top_k=3)
        online_results, online_error = _search_online_wikipedia(query, top_k=3)

        if local_error:
            errors.append(local_error)
        if online_error:
            errors.append(online_error)

        combined = local_results + online_results
        combined.sort(key=lambda x: x.get("score", 0), reverse=True)
        results = combined[:3]

    if not results:
        return {
            "success": False,
            "error": "No relevant results found. Try a more specific question.",
            "results": [],
            "best_result": None,
            "explanation": "",
            "source_mode": source_mode,
            "details": errors,
        }

    # Select best result
    best_result = get_best_result(results)

    # Generate explanation
    explanation = explain_result(best_result)

    # Translate if requested
    if target_language != "en":
        results = [translate_result(r, target_language) for r in results]
        best_result = translate_result(best_result, target_language)

    return {
        "success": True,
        "error": None,
        "results": results,  # Top 3 results
        "best_result": best_result,  # Best result
        "explanation": explanation,
        "language": target_language,
        "source_mode": source_mode,
        "details": errors,
    }


def search_knowledge_base(query, language="en"):
    """Wrapper function for backward compatibility."""
    return search(query, target_language=language, source_mode="all")
