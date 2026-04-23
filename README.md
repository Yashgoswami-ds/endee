# AI Knowledge Base Assistant

AI Knowledge Base Assistant is a Flask web app that fetches text from Wikipedia, creates semantic embeddings using **Endee** vector database, and enables natural language search with confidence scoring.

## Features

- Fetches summaries from Wikipedia API
- Stores knowledge text locally with deduplication
- Creates sentence-transformer embeddings (384-dimensional)
- Uses **Endee** vector database for semantic search
- Falls back to bag-of-words embeddings if model unavailable
- Shows confidence scores and source attribution
- Primary: Wikipedia API (100% confidence), Secondary: Endee (semantic match with %)
- Modern responsive web UI with Poppins font

## Technologies Used

- **Backend**: Python, Flask
- **Vector Database**: Endee (open-source, Docker-based)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **APIs**: Wikipedia REST API
- **Frontend**: HTML5, CSS3 (Poppins font, CSS variables, responsive)
- **Libraries**: NumPy, requests, endee-sdk

## Quick Start

### Prerequisites
- Python 3.8+
- Docker Desktop (for Endee vector database)

### Step 1: Install Docker
Download and install [Docker Desktop](https://docs.docker.com/get-docker/) for your OS.

### Step 2: Start Endee Server
```bash
docker run \
  --ulimit nofile=100000:100000 \
  -p 8080:8080 \
  -v ./endee-data:/data \
  --name endee-server \
  endeeio/endee-server:latest
```
**Windows users**: Run `start_endee.bat` instead.

Verify: Open http://localhost:8080 in browser.

### Step 3: Create Virtual Environment

Windows PowerShell:
```powershell
python -m venv venv
.\\venv\\Scripts\\activate
```

Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Create Embeddings
```bash
python embed_store.py
```
This reads `data/knowledge.txt` and stores embeddings in Endee.

### Step 6: Run the App
```bash
python app.py
```
Open http://localhost:5000

## How It Works

```
1. User asks a question → 
2. Flask app (app.py) receives query →
3. Search tries Wikipedia API first →
4. If not found, queries Endee vector DB →
5. Returns result with confidence + source
```

### Component Details

- **fetch_data.py**: Downloads Wikipedia summaries, stores in `data/knowledge.txt`
- **embed_store.py**: Generates embeddings, upserts to Endee index `knowledge_base`
- **search.py**: Handles Wikipedia search + Endee semantic search
- **app.py**: Flask web server with GET/POST route
- **templates/index.html**: Modern UI with search form + result display

## Example Usage

Try these questions:

- "What is machine learning?"
- "Explain Python programming"
- "Tell me about Java"

**Expected Result:**
```json
{
  "title": "Machine Learning",
  "content": "[Wikipedia summary or local paragraph]",
  "source_label": "Wikipedia",
  "confidence": 100
}
```

## Project Structure

```
AI-Knowledge-Assistant/
├── app.py                    # Flask web server
├── fetch_data.py             # Wikipedia data fetching
├── embed_store.py            # Embedding generation & Endee upsert
├── search.py                 # Search logic (Wikipedia + Endee)
├── requirements.txt          # Python dependencies
├── SETUP_ENDEE.md            # Detailed Endee setup guide
├── start_endee.bat           # Windows batch script to start Endee
├── README.md                 # This file
├── data/
│   └── knowledge.txt         # Local knowledge base
├── templates/
│   └── index.html            # Web UI
└── endee-data/               # Endee database (Docker volume)
```

## Configuration

### Change Endee Server URL
Edit `embed_store.py` and `search.py`:
```python
ENDEE_URL = "http://your-server:8080/api/v1"
```

### Use Authentication with Endee
Start Endee with token:
```bash
docker run -e NDD_AUTH_TOKEN=your_token ... endeeio/endee-server:latest
```

Then in code:
```python
from endee import Endee
client = Endee("your_token")
client.set_base_url(ENDEE_URL)
```

## Stopping Services

### Stop Endee
```bash
docker stop endee-server
```

### Stop Flask App
Press `Ctrl+C` in terminal.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to Endee" | Ensure Docker is running: `docker ps` |
| "Import error: endee" | Install: `pip install endee` |
| Port 8080 already in use | Change port: `docker run -p 8081:8080 ...` |
| No embeddings found | Run `python embed_store.py` |

## Architecture

```
Browser (localhost:5000)
    ↓
Flask App (app.py)
    ↓
Search Logic (search.py)
    ├─→ Wikipedia API ────────→ 100% confidence result
    └─→ Endee Vector DB ──────→ Semantic match with %
         └─→ Docker (8080)
             └─→ knowledge_base index
                 └─→ Sentence embeddings
```

## Learning Resources

- [Endee Quick Start](https://docs.endee.io/quick-start)
- [Endee GitHub](https://github.com/endee-io/endee)
- [Sentence Transformers Docs](https://www.sbert.net/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

This project is open source. See LICENSE file for details.
