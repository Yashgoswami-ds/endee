"""Create and store embeddings for the local knowledge base."""

import os
import pickle
import re
from collections import Counter

import numpy as np
from sentence_transformers import SentenceTransformer


DATA_FILE = os.path.join("data", "knowledge.txt")
DB_FILE = os.path.join("db", "vectors.pkl")
MODEL_NAME = "all-MiniLM-L6-v2"


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
        model = SentenceTransformer(MODEL_NAME, local_files_only=True)
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

        return {
            "embedding_type": "simple-bow",
            "embeddings": np.array(vectors, dtype=float),
            "vocabulary": vocabulary,
        }


def store_embeddings(paragraphs, embedding_data):
    """Save paragraphs and embeddings to a pickle file."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    data = {
        "paragraphs": paragraphs,
        "embeddings": embedding_data["embeddings"],
        "embedding_type": embedding_data["embedding_type"],
        "vocabulary": embedding_data["vocabulary"],
        "model_name": MODEL_NAME,
        "paragraph_count": len(paragraphs),
    }

    with open(DB_FILE, "wb") as file:
        pickle.dump(data, file)


def main():
    paragraphs = load_paragraphs()

    if not paragraphs:
        print("No knowledge found in data/knowledge.txt")
        return

    embedding_data = create_embeddings(paragraphs)
    store_embeddings(paragraphs, embedding_data)
    print(f"Stored {len(paragraphs)} embeddings in {DB_FILE}")


if __name__ == "__main__":
    main()
