"""Fetch Wikipedia summaries and save them locally."""

import os
import re

import requests


DATA_FILE = os.path.join("data", "knowledge.txt")
TOPICS = [
    "Python_(programming_language)",
    "Java_(programming_language)",
    "Machine_learning",
]
HEADERS = {
    "User-Agent": "AI Knowledge Base Assistant/1.0 (student project)",
}


def normalize_text(text):
    """Make text easier to compare and store."""
    return re.sub(r"\s+", " ", text.strip()).lower()


def load_existing_entries():
    """Read the current file so we do not add the same entry twice."""
    if not os.path.exists(DATA_FILE):
        return set()

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        content = file.read().strip()

    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
    return {normalize_text(chunk) for chunk in chunks}


def fetch_wikipedia_summary(topic):
    """Get the summary text for one Wikipedia page."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    data = response.json()

    title = data.get("title", topic.replace("_", " "))
    extract = data.get("extract", "")

    if not extract:
        return ""

    return f"{title}\n{extract.strip()}"


def save_knowledge(texts):
    """Append fetched content to the knowledge file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    existing_entries = load_existing_entries()

    with open(DATA_FILE, "a", encoding="utf-8") as file:
        for text in texts:
            cleaned_text = text.strip()
            if cleaned_text and normalize_text(cleaned_text) not in existing_entries:
                file.write(cleaned_text)
                file.write("\n\n")
                existing_entries.add(normalize_text(cleaned_text))


def main():
    collected_texts = []

    for topic in TOPICS:
        try:
            text = fetch_wikipedia_summary(topic)
            if text:
                collected_texts.append(text)
                print(f"Fetched: {topic}")
        except requests.RequestException as error:
            print(f"Failed to fetch {topic}: {error}")

    if collected_texts:
        save_knowledge(collected_texts)
        print(f"Saved content to {DATA_FILE}")
    else:
        print("No Wikipedia summaries were fetched.")


if __name__ == "__main__":
    main()