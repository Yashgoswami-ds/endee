# AI Knowledge Assistant

AI Knowledge Assistant is a Flask-based app that lets you search across local notes, uploaded PDFs, and online knowledge in one place.

It is designed to be simple to run, easy to understand, and practical for day-to-day use.

## What You Can Do

- Ask natural-language questions and get top 3 matching answers
- Pick source mode: all, only PDF, or only online
- Upload PDFs and make their content searchable
- Paste any valid URL and extract readable page text
- Translate answers into multiple languages
- Save answer feedback (like/dislike + optional comment)

## Key Features

### 1. Smart Search with Ranking
- Main search flow is in search.py
- Returns top 3 matches with score
- Selects the highest-scoring result as best answer

### 2. Source Control in Search
- Source options available in UI:
  - all: combines local + online
  - pdf: only uploaded PDF data
  - online: Wikipedia-based online search

### 3. URL Content Extraction
- New module: link_extractor.py
- Accepts http:// or https:// URLs
- Removes noisy HTML elements (scripts/styles/nav/etc.)
- Extracts readable text and shows it directly in UI

### 4. PDF Knowledge Expansion
- PDF upload route: /upload-pdf
- Uses PyPDF2 for extraction
- Appends extracted content to local knowledge store

### 5. Translation Layer
- Translation helper in translator.py
- Supports multiple languages (EN, HI, DE, FR, ES, ZH-CN)
- Uses googletrans, falls back to deep-translator when needed

### 6. Feedback Tracking
- Feedback endpoint: /feedback
- Stores records in data/feedback.jsonl for review/analysis

## Project Flow

1. User enters question or URL in UI
2. Flask route in app.py handles request
3. Search request goes to search.py (local/online/PDF logic)
4. URL extract request goes to link_extractor.py
5. Result is rendered in templates/index.html

## Tech Stack

- Backend: Python, Flask
- Data/API: requests, Endee API (optional)
- Parsing: BeautifulSoup4, PyPDF2
- Translation: googletrans, deep-translator
- Frontend: HTML + CSS (Jinja templates)

## Setup Instructions

### 1) Create virtual environment

Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\activate
```

Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Optional environment config
Create .env in project root if you want Endee API enabled:

```env
ENDEE_BASE_URL=https://api.endee.ai/v1
ENDEE_API_KEY=your_api_key_here
```

### 4) Run the app
```bash
python app.py
```

Open in browser:
http://127.0.0.1:5000

## Quick Validation Checklist

1. Home page opens successfully
2. Search form is visible
3. Extract Content From URL section is visible
4. URL test: https://example.com shows extracted content
5. PDF upload page works
6. Search returns ranked results with score

## Important Files

- app.py: main Flask routes
- search.py: search logic and ranking
- link_extractor.py: URL text extraction
- pdf_handler.py: PDF upload and extraction
- translator.py: translation handling
- endee_api.py: Endee API wrapper
- templates/index.html: main UI template
- requirements.txt: all Python dependencies

## Project Structure

```text
AI-Knowledge-Assistant/
├── app.py
├── search.py
├── link_extractor.py
├── pdf_handler.py
├── translator.py
├── endee_api.py
├── fetch_data.py
├── embed_store.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── upload_pdf.html
│   └── about.html
└── data/
    ├── knowledge.txt
    ├── feedback.jsonl
    └── uploads/
```

## Notes

- Do not commit your .env file
- URL extraction works only for public HTML pages
- Some websites block scraping; in that case extraction may fail gracefully with an error message

## Developer

- Name: Yash
- Email: yg86253692outlook.com

