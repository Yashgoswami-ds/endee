# Endee Vector Database Setup

This project now uses **Endee** - an open-source vector database for AI search and retrieval.

## Prerequisites

1. **Docker Desktop** - Download from [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
   - Verify installation: `docker --version`

## Step 1: Start Endee Server

### Option A: Using PowerShell (Windows)
```powershell
docker run `
  --ulimit nofile=100000:100000 `
  -p 8080:8080 `
  -v ./endee-data:/data `
  --name endee-server `
  endeeio/endee-server:latest
```

### Option B: Using Bash/Shell (Linux/macOS)
```bash
docker run \
  --ulimit nofile=100000:100000 \
  -p 8080:8080 \
  -v ./endee-data:/data \
  --name endee-server \
  endeeio/endee-server:latest
```

### Option C: Using Pre-made Script (Windows)
Run the included `start_endee.bat` file in the project directory.

**Verify it's running:**
- Open http://localhost:8080 in your browser
- You should see the Endee dashboard

## Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `endee` - Python SDK for Endee
- `flask` - Web framework
- `requests` - HTTP library
- `sentence-transformers` - Embedding models
- `numpy` - Numerical computing

## Step 3: Create Embeddings in Endee

With the Endee server running, create embeddings from your knowledge base:

```bash
python embed_store.py
```

This:
1. Reads paragraphs from `data/knowledge.txt`
2. Generates 384-dimensional embeddings using sentence-transformers
3. Upserts them into Endee's `knowledge_base` index

**Expected output:**
```
Creating new index: knowledge_base
Upserted batch 1
Successfully stored 6 embeddings in Endee
✓ All 6 paragraphs stored in Endee
```

## Step 4: Run the Flask App

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

## Stopping Endee

```bash
docker stop endee-server
```

Your data is persisted in the `./endee-data` folder.

## Troubleshooting

### "Cannot connect to Endee"
- Make sure Docker is running
- Check if the server is running: `docker ps | grep endee-server`
- Verify port 8080 is not blocked

### "Import error for 'endee'"
- Install: `pip install endee`

### Docker not found
- Install Docker Desktop from [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

## Architecture

```
User Browser (localhost:5000)
         ↓
    Flask App (app.py)
         ↓
    Search (search.py)
         ├─→ Wikipedia API (direct search)
         └─→ Endee Vector DB (semantic search)
              └─→ Docker Container (localhost:8080)
                  └─→ Vector Index (knowledge_base)
```

## Configuration

### Endee URL
Default: `http://localhost:8080/api/v1`

To change, edit `embed_store.py` and `search.py`:
```python
ENDEE_URL = "http://your-server:8080/api/v1"
```

### Authentication (Optional)
If you need authentication, start Endee with:
```bash
docker run -e NDD_AUTH_TOKEN=your_token ... endeeio/endee-server:latest
```

Then in your code:
```python
from endee import Endee
client = Endee("your_token")
```

## Learn More

- **Endee Documentation**: https://docs.endee.io/quick-start
- **GitHub**: https://github.com/endee-io/endee
- **Website**: https://endee.io/
