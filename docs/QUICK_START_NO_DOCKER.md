# Quick Start Without Docker

## Install Python Dependencies Locally

We'll skip Docker for now and run everything locally with SQLite instead of PostgreSQL.

### Step 1: Activate Virtual Environment

```powershell
cd "d:\gemini hackathon\resume_parser_ai"
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Core Dependencies Only

```powershell
# Install minimal requirements for basic functionality
pip install fastapi uvicorn python-multipart
pip install sqlalchemy alembic
pip install pypdf2 python-docx pillow
pip install spacy
pip install pydantic pydantic-settings
pip install httpx aiofiles
pip install transformers torch

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 3: Create SQLite Database Configuration

We'll use SQLite instead of PostgreSQL (no Docker needed).

### Step 4: Start the API

```powershell
uvicorn app.main:app --reload
```

### Step 5: Test with Your Dataset

```powershell
# Process a few sample resumes from your dataset
python scripts/test_local.py
```

---

## Why This Is Faster

- ✅ No Docker build (saves 10+ minutes)
- ✅ No Elasticsearch/Redis (use in-memory)
- ✅ SQLite instead of PostgreSQL
- ✅ Direct Python execution
- ✅ Faster iteration

## Trade-offs

- ❌ No full-text search (Elasticsearch)
- ❌ No caching (Redis)
- ❌ Single-threaded
- ✅ But everything else works!

---

Would you like to try this approach instead?
