# 🚀 Deployment Guide for Company

## Project Summary

**AI Knowledge Base Assistant** - A Flask web application that provides semantic search using **Endee vector database**.

### Key Features
- ✅ Real-time semantic search with confidence scoring
- ✅ Wikipedia API integration for live data
- ✅ Open-source Endee vector database (no expensive cloud services)
- ✅ Docker containerized - easy deployment
- ✅ Modern responsive UI
- ✅ Production-ready code

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows, Linux, or macOS |
| Docker | Docker Desktop 4.0+ |
| Python | 3.8 or higher |
| RAM | Minimum 2GB |
| Storage | 1GB for Endee database |
| Network | Internet required (Wikipedia API) |

---

## Deployment Steps (5 minutes)

### Step 1: Install Docker
Download from: https://docs.docker.com/get-docker/

Verify:
```bash
docker --version
```

### Step 2: Clone Repository
```bash
git clone https://github.com/Yashgoswami-ds/AI-Knowledge-Assistant.git
cd AI-Knowledge-Assistant
```

### Step 3: Start Endee Vector Database
```bash
# Windows PowerShell
docker run `
  --ulimit nofile=100000:100000 `
  -p 8080:8080 `
  -v ./endee-data:/data `
  --name endee-server `
  --restart unless-stopped `
  endeeio/endee-server:latest
```

**Verify Endee is running:**
- Open http://localhost:8080 in browser
- Should see Endee dashboard

### Step 4: Setup Python Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

Expected packages:
- flask
- requests
- sentence-transformers
- numpy
- endee

### Step 6: Create Embeddings
```bash
python embed_store.py
```

Expected output:
```
Creating new index: knowledge_base
Upserted batch 1
Successfully stored 6 embeddings in Endee
✓ All 6 paragraphs stored in Endee
```

### Step 7: Start Flask Application
```bash
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
WARNING: This is a development server. Do not use it in production directly.
```

### Step 8: Access the Application
Open http://localhost:5000 in web browser

---

## Usage

### Searching
1. Enter a question in the search box
2. Press Enter or click "Search"
3. View result with:
   - **Title** - Question topic or Wikipedia article
   - **Content** - Full answer
   - **Source** - Wikipedia or Endee Vector DB
   - **Confidence** - Accuracy percentage

### Sample Queries
- "What is Python?"
- "Explain machine learning"
- "Tell me about Java"
- "How does artificial intelligence work?"

---

## Architecture

```
┌─────────────────────┐
│   Web Browser       │
│  localhost:5000     │
└──────────┬──────────┘
           │ HTTP Request
           ↓
┌──────────────────────────────┐
│   Flask Web Application       │
│  app.py                       │
└──────────┬───────────────────┘
           │
    ┌──────┴──────┐
    ↓             ↓
┌─────────────┐  ┌──────────────────────┐
│ Wikipedia   │  │ Endee Vector DB      │
│ REST API    │  │ (Semantic Search)    │
│ 100% conf   │  │ (Similarity %)       │
└─────────────┘  └──────────┬───────────┘
                            │
                   ┌────────↓────────┐
                   │ Docker Container│
                   │ localhost:8080  │
                   └─────────────────┘
```

---

## File Structure

```
AI-Knowledge-Assistant/
├── app.py                    # Flask web server entry point
├── fetch_data.py             # Wikipedia data fetcher
├── embed_store.py            # Embedding generator & Endee upserter
├── search.py                 # Search engine (Wikipedia + Endee)
├── requirements.txt          # Python dependencies
├── README.md                 # Project overview
├── SETUP_ENDEE.md            # Detailed Endee setup
├── TEST_GUIDE.md             # Quick start guide
├── DEPLOYMENT.md             # This file
├── templates/
│   └── index.html            # Web UI
├── data/
│   └── knowledge.txt         # Local knowledge base
├── endee-data/               # Endee database (Docker volume)
└── screenshots/
    ├── README.md             # Screenshots guide
    ├── home_page.png         # App home page
    ├── search_result_wikipedia.png
    └── search_result_endee.png
```

---

## Configuration

### Change Port
**Flask (default 5000):**
```bash
python app.py --port 8000
```
Or edit `app.py`:
```python
if __name__ == "__main__":
    app.run(debug=False, port=8000)
```

**Endee (default 8080):**
```bash
docker run -p 9000:8080 ... endeeio/endee-server:latest
```
Then update `search.py` and `embed_store.py`:
```python
ENDEE_URL = "http://localhost:9000/api/v1"
```

### Add Authentication
**Endee with token:**
```bash
docker run -e NDD_AUTH_TOKEN=secret_token ... endeeio/endee-server:latest
```

**In code:**
```python
from endee import Endee
client = Endee("secret_token")
```

---

## Production Deployment

### For AWS / Azure / GCP

**Option 1: EC2 / VM Instance**
1. Launch Linux instance
2. Install Docker and Python
3. Clone repository
4. Follow deployment steps above
5. Expose port 5000 via security group

**Option 2: Docker Container Registry**
1. Build Dockerfile:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "app.py"]
   ```
2. Push to ECR/Azure Container Registry
3. Deploy with docker-compose

**Option 3: Kubernetes**
1. Create deployment manifests
2. Deploy Endee and Flask as separate pods
3. Use persistent volumes for Endee data

---

## Monitoring & Logs

### Check Endee Status
```bash
curl http://localhost:8080/api/v1/health
```

### Check Flask Logs
```bash
# View real-time logs
python app.py

# Or use logging in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Docker Containers
```bash
# List running containers
docker ps

# View Endee logs
docker logs endee-server

# Stop Endee
docker stop endee-server

# Start Endee
docker start endee-server
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to Endee" | 1. Check `docker ps`<br>2. Check http://localhost:8080<br>3. Restart: `docker restart endee-server` |
| "Port 8080 already in use" | Use different port: `docker run -p 9000:8080 ...` |
| "ImportError: endee" | Install: `pip install endee` |
| "No embeddings found" | Run: `python embed_store.py` |
| "Flask not starting" | Check port 5000 is free: `netstat -tuln \| grep 5000` |
| "Wikipedia timeout" | Network issue - check internet connection |

---

## Scaling

### Add More Knowledge
1. Edit `fetch_data.py` to add more Wikipedia topics
2. Run `python fetch_data.py`
3. Run `python embed_store.py`
4. Restart Flask app

### Performance Tuning

**Endee Configuration:**
```bash
docker run \
  -e NDD_NUM_THREADS=4 \
  -p 8080:8080 \
  -v ./endee-data:/data \
  endeeio/endee-server:latest
```

**Flask Configuration:**
```python
app.run(debug=False, threaded=True, workers=4)
```

---

## Security

### Best Practices
1. ✅ Use Endee authentication token
2. ✅ Run Flask behind reverse proxy (Nginx)
3. ✅ Use HTTPS/TLS in production
4. ✅ Validate user input
5. ✅ Keep dependencies updated
6. ✅ Use environment variables for secrets

### Sample Nginx Config
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Support & Resources

- **Project GitHub**: https://github.com/Yashgoswami-ds/AI-Knowledge-Assistant
- **Endee Documentation**: https://docs.endee.io/
- **Endee GitHub**: https://github.com/endee-io/endee
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Docker Documentation**: https://docs.docker.com/

---

## License

This project is open source. See LICENSE file for details.

---

**Version:** 1.0.0  
**Last Updated:** April 2026  
**Status:** Production Ready ✅
