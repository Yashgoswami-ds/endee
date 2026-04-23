# Screenshots Guide

## Required Screenshots

To showcase the app, please take the following screenshots and save them in this folder:

### 1. `home_page.png`
**What to capture:**
- Flask app at http://localhost:5000
- Show the search form with:
  - Input field placeholder: "Ask a question..."
  - Search button
  - Clean UI with Poppins font
  - Gradient background

**How to take:**
1. Run `python app.py`
2. Open http://localhost:5000
3. Screenshot the page (Ctrl+Print Screen or browser DevTools)

---

### 2. `search_result_wikipedia.png`
**What to capture:**
- A search result from Wikipedia
- Title: "[Wikipedia Topic]"
- Content: Full Wikipedia summary
- Source badge: "Wikipedia"
- Confidence: "100%"
- Sample query: "What is Python?"

**How to take:**
1. Enter "What is Python?" in search box
2. Click Search or press Enter
3. Screenshot the result card

---

### 3. `search_result_endee.png`
**What to capture:**
- A search result from Endee vector DB
- Title: "Local Knowledge Base"
- Content: Relevant paragraph from knowledge.txt
- Source badge: "Endee Vector DB"
- Confidence: "[XX%]" (varies based on similarity)
- Sample query: "machine learning" or "Java programming"

**How to take:**
1. Enter "machine learning" in search box
2. Click Search
3. Screenshot the result card

---

### 4. `architecture_diagram.png` (Optional)
**Description:**
Flow diagram showing:
```
Browser (localhost:5000)
    ↓
Flask App
    ├─ Wikipedia API ──→ 100% confidence
    └─ Endee Vector DB ──→ Semantic % confidence
         └─ Docker (8080)
```

---

## Instructions for User

Once you take the screenshots:

1. **Save them in this folder** (`screenshots/`)
2. **Name them exactly as above** (lowercase with underscores)
3. **Format:** PNG or JPG
4. **Size:** Recommended 1280x720 or larger

---

## Implementation Steps

1. **Terminal 1: Start Endee**
   ```bash
   docker run -p 8080:8080 -v ./endee-data:/data --name endee-server endeeio/endee-server:latest
   ```

2. **Terminal 2: Create embeddings**
   ```bash
   python embed_store.py
   ```

3. **Terminal 3: Run Flask app**
   ```bash
   python app.py
   ```

4. **Browser: Take screenshots**
   - Go to http://localhost:5000
   - Test different queries
   - Capture results

5. **Git: Add and push**
   ```bash
   git add screenshots/*.png
   git commit -m "Add app screenshots: home, Wikipedia result, Endee result"
   git push
   ```

---

## Current Screenshots

Existing files in this folder:
- `image.png` - Previous screenshot (can be replaced)

---

## Tips

- **Clear browser cache** before taking screenshots
- **Use full page screenshots** (not just viewport)
- **Make sure Endee is running** before searching
- **Test multiple queries** to get good examples
- **Use good lighting** for clear screenshots

---

**Once you take and save the screenshots, I'll add them to git and push to GitHub!** 🚀
