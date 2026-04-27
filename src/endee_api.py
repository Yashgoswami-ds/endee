"""Endee SDK integration for vector search."""

import hashlib
import logging
import os
import re
from collections import Counter
from functools import lru_cache
from typing import Dict, List, Optional

import dotenv
import numpy as np

try:
    from endee import Endee, Precision
    ENDEE_AVAILABLE = True
except ImportError:
    ENDEE_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Load environment variables.
dotenv.load_dotenv()

ENDEE_BASE_URL = os.getenv("ENDEE_BASE_URL", "http://localhost:8080/api/v1")
ENDEE_API_KEY = os.getenv("ENDEE_API_KEY", "")
INDEX_NAME = os.getenv("ENDEE_INDEX_NAME", "knowledge_base")
MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))
ALLOW_MODEL_DOWNLOAD = os.getenv("ALLOW_MODEL_DOWNLOAD", "1").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def is_configured():
    """Check if the Endee client can be used with the current environment."""
    return bool(ENDEE_AVAILABLE and ENDEE_BASE_URL)


@lru_cache(maxsize=1)
def _get_client():
    """Create a configured Endee SDK client."""
    if not ENDEE_AVAILABLE:
        return None

    client = Endee(ENDEE_API_KEY) if ENDEE_API_KEY else Endee()
    client.set_base_url(ENDEE_BASE_URL)
    return client


@lru_cache(maxsize=1)
def _get_embedding_model():
    """Load the sentence-transformer model once and reuse it."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None

    try:
        return SentenceTransformer(MODEL_NAME, local_files_only=not ALLOW_MODEL_DOWNLOAD)
    except Exception as error:
        logger.warning("embedding_model_load_failed model=%s error=%s", MODEL_NAME, error)
        return None


def _tokenize(text: str) -> List[str]:
    """Split text into lowercase tokens for the fallback embedding path."""
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def _build_embeddings(texts: List[str]) -> np.ndarray:
    """Create dense embeddings or a deterministic fallback vector representation."""
    model = _get_embedding_model()
    if model is not None:
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return np.array(embeddings)

    vocabulary = sorted({word for text in texts for word in _tokenize(text)})
    vectors = []

    for text in texts:
        word_counts = Counter(_tokenize(text))
        vector = [word_counts[word] for word in vocabulary]
        padded_vector = vector + [0] * max(0, EMBEDDING_DIM - len(vector))
        vectors.append(padded_vector[:EMBEDDING_DIM])

    return np.array(vectors, dtype=float)


def _ensure_index():
    """Return an existing index or create the default one if needed."""
    client = _get_client()
    if client is None:
        return None, "Endee SDK not installed. Run: pip install endee"

    try:
        index = client.get_index(name=INDEX_NAME)
        return index, None
    except Exception:
        try:
            client.create_index(
                name=INDEX_NAME,
                dimension=EMBEDDING_DIM,
                space_type="cosine",
                precision=Precision.INT8,
            )
        except Exception as error:
            # Another process/request may have created the index between get and create.
            # Treat conflict/already-exists as non-fatal and retry get_index below.
            error_text = str(error).lower()
            if "already exists" not in error_text and "conflict" not in error_text:
                logger.exception("endee_index_create_failed index=%s", INDEX_NAME)
                return None, f"Error creating Endee index: {error}"

        try:
            index = client.get_index(name=INDEX_NAME)
            return index, None
        except Exception as error:
            logger.exception("endee_index_load_failed_after_create index=%s", INDEX_NAME)
            return None, f"Error loading Endee index: {error}"


def store_to_endee(text_chunks: List[str]) -> tuple:
    """Store text chunks to Endee as indexed vectors."""
    if not is_configured():
        return False, "Endee is not configured"

    chunks = [chunk.strip() for chunk in text_chunks if chunk and chunk.strip()]
    if not chunks:
        return False, "No text chunks to store"

    index, error = _ensure_index()
    if index is None:
        return False, error or "Unable to initialize Endee index"

    try:
        embeddings = _build_embeddings(chunks)
        vectors_to_upsert = []

        for position, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = hashlib.sha1(f"{position}:{chunk}".encode("utf-8")).hexdigest()[:24]
            vectors_to_upsert.append({
                "id": vector_id,
                "vector": embedding.tolist(),
                "meta": {"text": chunk},
            })

        batch_size = 1000
        for start_index in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[start_index : start_index + batch_size]
            index.upsert(batch)

        return True, f"Stored {len(vectors_to_upsert)} chunks to Endee"
    except Exception as error:
        logger.exception("endee_store_failed")
        return False, f"Error storing to Endee: {error}"


def search_endee(query: str, top_k: int = 3) -> tuple:
    """Search Endee vector database for top matching chunks."""
    if not is_configured():
        return None, "Endee is not configured"

    index, error = _ensure_index()
    if index is None:
        return None, error or "Unable to initialize Endee index"

    try:
        query_vector = _build_embeddings([query])[0].tolist()
        results = index.query(
            vector=query_vector,
            top_k=top_k,
            ef=128,
            include_vectors=False,
        )

        formatted_results = []
        for item in results or []:
            meta = item.get("meta", {}) if isinstance(item, dict) else {}
            formatted_results.append({
                "text": meta.get("text", ""),
                "score": item.get("similarity", 0.0) if isinstance(item, dict) else 0.0,
            })

        return formatted_results, None
    except Exception as error:
        logger.exception("endee_search_failed query=%s", query)
        return None, f"Error searching Endee: {error}"


def delete_all_vectors() -> tuple:
    """Delete the current Endee index contents if supported by the SDK."""
    if not is_configured():
        return False, "Endee is not configured"

    index, error = _ensure_index()
    if index is None:
        return False, error or "Unable to initialize Endee index"

    try:
        # If the SDK exposes a full-index delete later, this is the place to wire it.
        # For now we keep the method as a safe no-op-compatible hook.
        return False, "Bulk delete is not implemented in this client"
    except Exception as error:
        return False, f"Error deleting vectors: {error}"


# Fallback: Mock search if the SDK is unavailable.
def mock_search(query: str, knowledge_text: str, top_k: int = 3) -> List[Dict]:
    """Fallback search when Endee SDK is unavailable."""
    paragraphs = knowledge_text.split("\n\n")
    results = []
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
                "score": min(score / max(len(query_words), 1) / 10, 1.0),
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
