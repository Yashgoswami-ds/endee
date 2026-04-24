"""Create and store embeddings in Endee vector database."""

import os
import re
from collections import Counter

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    from endee import Endee, Precision
    ENDEE_AVAILABLE = True
except ImportError:
    ENDEE_AVAILABLE = False


DATA_FILE = os.path.join("data", "knowledge.txt")
MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_NAME = os.getenv("ENDEE_INDEX_NAME", "knowledge_base")
EMBEDDING_DIM = 384  # Dimension of all-MiniLM-L6-v2
ENDEE_URL = os.getenv("ENDEE_URL", "http://localhost:8080/api/v1")
ALLOW_MODEL_DOWNLOAD = os.getenv("ALLOW_MODEL_DOWNLOAD", "1").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def tokenize(text):
    """Split text into simple lowercase words."""
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def load_paragraphs():
    """Read the knowledge file and split it into paragraphs."""
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        content = file.read().strip()

    paragraphs = [paragraph.strip() for paragraph in content.split("\n\n") if paragraph.strip()]

    unique_paragraphs = []
    seen = set()
    for paragraph in paragraphs:
        normalized = re.sub(r"\s+", " ", paragraph.lower())
        if normalized not in seen:
            unique_paragraphs.append(paragraph)
            seen.add(normalized)

    return unique_paragraphs


def create_embeddings(texts):
    """Generate embeddings for a list of paragraphs."""
    try:
        model = SentenceTransformer(MODEL_NAME, local_files_only=not ALLOW_MODEL_DOWNLOAD)
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return {
            "embedding_type": "sentence-transformer",
            "embeddings": np.array(embeddings),
            "vocabulary": [],
        }
    except Exception:
        vocabulary = sorted({word for text in texts for word in tokenize(text)})
        vectors = []

        for text in texts:
            word_counts = Counter(tokenize(text))
            vector = [word_counts[word] for word in vocabulary]
            vectors.append(vector)

        # Pad BOW vectors to match EMBEDDING_DIM
        padded_vectors = []
        for vec in vectors:
            padded = vec + [0] * (EMBEDDING_DIM - len(vec))
            padded_vectors.append(padded[:EMBEDDING_DIM])

        return {
            "embedding_type": "simple-bow",
            "embeddings": np.array(padded_vectors, dtype=float),
            "vocabulary": vocabulary,
        }


def upsert_to_endee(paragraphs, embeddings):
    """Upsert paragraphs and embeddings to Endee vector database."""
    if not ENDEE_AVAILABLE:
        print("Endee SDK not installed. Install with: pip install endee")
        return False

    try:
        client = Endee()
        client.set_base_url(ENDEE_URL)

        # Create index if it doesn't exist
        try:
            index = client.get_index(name=INDEX_NAME)
            print(f"Using existing index: {INDEX_NAME}")
        except Exception:
            print(f"Creating new index: {INDEX_NAME}")
            client.create_index(
                name=INDEX_NAME,
                dimension=EMBEDDING_DIM,
                space_type="cosine",
                precision=Precision.INT8,
            )
            index = client.get_index(name=INDEX_NAME)

        # Prepare vectors for upsert
        vectors_to_upsert = []
        for i, (paragraph, embedding) in enumerate(zip(paragraphs, embeddings)):
            vectors_to_upsert.append({
                "id": f"para_{i}",
                "vector": embedding.tolist(),
                "meta": {"text": paragraph},
            })

        # Upsert in batches (max 1000 per call)
        batch_size = 1000
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i : i + batch_size]
            index.upsert(batch)
            print(f"Upserted batch {i // batch_size + 1}")

        print(f"Successfully stored {len(paragraphs)} embeddings in Endee")
        return True

    except Exception as e:
        print(f"Error connecting to Endee: {e}")
        print(f"Make sure Endee server is running at {ENDEE_URL}")
        return False


def main():
    paragraphs = load_paragraphs()

    if not paragraphs:
        print("No knowledge found in data/knowledge.txt")
        return

    embedding_data = create_embeddings(paragraphs)
    embeddings = embedding_data["embeddings"]

    success = upsert_to_endee(paragraphs, embeddings)
    if success:
        print(f"✓ All {len(paragraphs)} paragraphs stored in Endee")
    else:
        print("✗ Failed to store embeddings in Endee")


if __name__ == "__main__":
    main()
