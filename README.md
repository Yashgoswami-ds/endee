# AI Knowledge Base Assistant

AI Knowledge Base Assistant is a simple Flask web app that fetches text from Wikipedia, stores it locally, creates embeddings, and lets the user search with natural language.

## Features

- Fetches summaries from Wikipedia
- Saves knowledge text in a local file
- Removes duplicate knowledge before building vectors
- Creates sentence-transformer embeddings
- Uses cosine similarity for semantic search
- Shows confidence and source in the result card
- Shows the answer in a simple web page

## Technologies Used

- Python
- Flask
- Requests
- Sentence Transformers
- NumPy
- HTML and basic CSS

## Setup

1. Create and activate virtual environment:

   - Windows PowerShell:

     ```powershell
     python -m venv venv
     .\\venv\\Scripts\\activate
     ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Run the app:

   ```powershell
   python app.py
   ```

4. Open: http://localhost:5000

## How It Works

1. Run `fetch_data.py` to download Wikipedia summaries.
2. Run `embed_store.py` to create and store embeddings.
3. Run `app.py` and ask a question in the browser.

## Example Usage

Try questions like:

- What is machine learning?
- Explain Python programming language
- What is Java used for?

## Project Structure

- app.py: Flask web app with search form and result page
- fetch_data.py: Gets Wikipedia summaries and saves them locally
- embed_store.py: Creates embeddings and stores them with pickle
- search.py: Loads embeddings and finds the closest paragraph
- data/knowledge.txt: Local knowledge text file
- db/vectors.pkl: Saved embeddings database
- templates/index.html: Basic UI template
