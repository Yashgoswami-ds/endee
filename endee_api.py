"""Endee API integration for vector search."""

import os
import json
from typing import List, Dict, Optional
import warnings
import urllib3

import requests
import dotenv

# Suppress SSL warnings (for testing with verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Create custom session with SSL verification disabled
session = requests.Session()
session.verify = False
session.headers.update({"User-Agent": "Python-Requests"})

# Load environment variables
dotenv.load_dotenv()

ENDEE_BASE_URL = os.getenv("ENDEE_BASE_URL", "https://api.endee.ai/v1")
ENDEE_API_KEY = os.getenv("ENDEE_API_KEY", "")

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ENDEE_API_KEY}" if ENDEE_API_KEY else ""
}


def is_configured():
    """Check if Endee API is properly configured."""
    return ENDEE_API_KEY and ENDEE_BASE_URL


def store_to_endee(text_chunks: List[str]) -> tuple:
    """
    Store text chunks to Endee vector database.
    
    Args:
        text_chunks: List of text strings to store
    
    Returns:
        (success, message)
    """
    if not is_configured():
        return False, "Endee API key not configured. Set ENDEE_API_KEY in .env"

    try:
        stored_count = 0
        
        for chunk in text_chunks:
            if not chunk.strip():
                continue

            payload = {
                "text": chunk.strip()
            }

            response = session.post(
                f"{ENDEE_BASE_URL}/vectors",
                json=payload,
                headers=HEADERS,
                timeout=15
            )

            if response.status_code == 201:  # Created
                stored_count += 1
            else:
                print(f"Warning: Failed to store chunk (status {response.status_code})")

        return True, f"Stored {stored_count} chunks to Endee"

    except Exception as e:
        return False, f"Error storing to Endee: {str(e)}"


def search_endee(query: str, top_k: int = 3) -> tuple:
    """
    Search Endee vector database for top results.
    
    Args:
        query: Search query string
        top_k: Number of top results to return (default: 3)
    
    Returns:
        (results_list, error_message)
        
    Results format:
        [
            {"text": "...", "score": 0.91},
            {"text": "...", "score": 0.84},
            ...
        ]
    """
    if not is_configured():
        return None, "Endee API key not configured"

    try:
        payload = {
            "query": query,
            "top_k": top_k
        }

        response = session.post(
            f"{ENDEE_BASE_URL}/search",
            json=payload,
            headers=HEADERS,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Ensure results have score and text fields
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result.get("text", ""),
                    "score": result.get("score", 0.0)
                })
            
            return formatted_results, None
        else:
            return None, f"Endee API error: {response.status_code}"

    except requests.RequestException as e:
        return None, f"Cannot connect to Endee: {str(e)}"
    except Exception as e:
        return None, f"Error searching Endee: {str(e)}"


def delete_all_vectors() -> tuple:
    """Delete all vectors from Endee (for reset/testing)."""
    if not is_configured():
        return False, "Endee API key not configured"

    try:
        response = session.delete(
            f"{ENDEE_BASE_URL}/vectors",
            headers=HEADERS,
            timeout=15
        )

        if response.status_code == 200:
            return True, "All vectors deleted from Endee"
        else:
            return False, f"Failed to delete vectors (status {response.status_code})"

    except Exception as e:
        return False, f"Error deleting vectors: {str(e)}"


# Fallback: Mock search if API not available
def mock_search(query: str, knowledge_text: str, top_k: int = 3) -> List[Dict]:
    """
    Fallback search when Endee API is not available.
    Uses simple keyword matching.
    """
    paragraphs = knowledge_text.split("\n\n")
    results = []

    # Simple scoring: count matching words
    query_words = query.lower().split()

    for para in paragraphs:
        if not para.strip():
            continue

        score = 0
        para_lower = para.lower()

        for word in query_words:
            score += para_lower.count(word)

        if score > 0:
            results.append({
                "text": para.strip(),
                "score": min(score / max(len(query_words), 1) / 10, 1.0)  # Normalize
            })

    # Sort by score and return top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
