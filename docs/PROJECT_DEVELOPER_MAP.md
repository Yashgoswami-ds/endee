# AI Knowledge Assistant - Developer Map

This document explains:
- What each file does
- How files are connected
- What to update when adding a new feature/file
- A safe checklist so the project stays easy to maintain

## 1) High-level architecture

User (Browser / API Client)
-> Flask routes in app.py
-> Feature modules (src/search.py, src/pdf_handler.py, src/link_extractor.py, src/translator.py)
-> Endee integration (src/endee_api.py)
-> Data files under data/
-> Templates under templates/

## 2) Core entry point and route map

### app.py (main orchestrator)

Responsibilities:
- Starts Flask app
- Defines web routes and API routes
- Reads form/json input
- Calls feature modules
- Writes feedback and search history
- Passes data to templates

Main web routes:
- / : search + URL extraction UI
- /upload-pdf : PDF upload page and processing
- /about : project info page
- /history : recent user activity
- /documents : uploaded PDF list

Main API routes:
- /api/search (POST)
- /api/history (GET)
- /api/documents (GET)

Writes runtime files:
- data/feedback.jsonl
- data/search_history.jsonl

## 3) Feature modules and connections

### src/search.py

Used by:
- app.py (search requests)

Uses:
- src.endee_api.search_endee for local/pdf retrieval
- src.translator.translate_result for multilingual output
- Wikipedia API for online mode

Returns:
- normalized results
- top result and explanation

### src/pdf_handler.py

Used by:
- app.py (/upload-pdf route)

Uses:
- PyPDF2 to extract text
- src.endee_api.store_to_endee to index chunks

Reads/Writes:
- reads uploaded PDF from data/uploads/
- appends extracted text to data/knowledge.txt

### src/link_extractor.py

Used by:
- app.py (action=extract_link)

Uses:
- requests + BeautifulSoup

Output:
- page title
- cleaned readable content
- truncated flag

### src/translator.py

Used by:
- search.py

Backends:
- googletrans (preferred)
- deep-translator (fallback)

### src/endee_api.py

Used by:
- search.py (search)
- pdf_handler.py (store)

Requires env config:
- ENDEE_BASE_URL
- ENDEE_API_KEY
- ENDEE_TIMEOUT_SECONDS (optional)
- ENDEE_VERIFY_SSL (optional)

## 4) Data and support scripts

### data/

- knowledge.txt : knowledge base text (local + appended PDF text)
- feedback.jsonl : user feedback log
- search_history.jsonl : recent activity log
- uploads/ : uploaded PDF files

### scripts/fetch_data.py

- Utility script to fetch Wikipedia summaries and append to knowledge.txt

### scripts/embed_store.py

- Utility script to generate embeddings and upsert to Endee SDK index

## 5) Frontend template map

### templates/index.html

- Main UI
- Search form
- URL extraction form
- Results rendering
- Feedback form
- Nav links

### templates/upload_pdf.html

- Upload PDF UI and status messages

### templates/history.html

- Renders entries from search_history.jsonl (via app.py)

### templates/documents.html

- Renders uploaded PDF names (via app.py -> src.pdf_handler.list_uploaded_pdfs)

### templates/about.html

- Project overview page

## 6) Testing map

### tests/test_routes.py

- Route health checks
- Endee status badge check
- History/Documents routes
- API endpoints response checks

### tests/test_search.py

- Search logic and ranking checks

### tests/test_ingestion_and_extract.py

- Ingestion/extraction related checks

Run tests:
- pytest -q

## 7) Dependency map

Main runtime deps in requirements.txt:
- flask
- requests
- PyPDF2
- beautifulsoup4
- python-dotenv
- googletrans / deep-translator
- pytest (dev test dependency)

## 8) How to add a NEW FEATURE (recommended workflow)

Example: add "Query bookmarks" feature.

1. Create feature module
- Add a new file in src/, for example src/bookmarks.py
- Keep pure business logic in this file

2. Wire route/API in app.py
- Add route for web page or API endpoint
- Validate inputs
- Call functions from bookmarks.py
- Return template or JSON

3. Add/update template
- Add a new template file if needed
- Add nav link in all pages where navigation exists:
  - templates/index.html
  - templates/upload_pdf.html
  - templates/about.html
  - templates/history.html
  - templates/documents.html

4. Add persistence if needed
- If feature writes logs/data, store under data/
- If generated at runtime, add to .gitignore

5. Add tests
- Route/API tests in tests/test_routes.py
- Logic tests in a new or existing test module

6. Update docs
- Update README.md (feature list + structure)
- Optionally update this file if architecture changed

7. Validate
- Run pytest -q
- Run app locally and test UI + endpoint manually

8. Commit cleanly
- Stage only source/template/test/docs files
- Avoid committing runtime data noise

## 9) How to add a NEW FILE safely

When adding any new file type, use this quick decision table:

- Python logic file (new_module.py)
- Python logic file (src/new_module.py)
  - Add import + call site in app.py or other src module
  - Add tests
  - Update README if user-visible

- Template file (templates/new_page.html)
  - Add Flask route in app.py
  - Add nav links where needed
  - Add route test

- Data file (data/*.jsonl, data/*.txt)
  - Decide: source-controlled or runtime-generated
  - If runtime-generated, add to .gitignore

- Config file
  - Document env keys in README
  - Load via dotenv/os.getenv in app.py or target module

## 10) Safe change checklist (copy/paste)

- I added/updated route in app.py
- I connected route to logic module
- I updated template/navigation links
- I updated tests
- I updated README/docs
- I checked .gitignore for runtime files
- I ran pytest -q
- I committed only intended files

---

If you keep this map updated after every major feature, the project remains easy to understand for reviewers, interviewers, and future contributors.
