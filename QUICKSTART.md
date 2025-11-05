# Resume Parser AI - Local Development Quick Start Guide

## Overview
This guide will help you set up and run the Resume Parser AI application locally without Docker.

## Prerequisites
- Python 3.11 or higher
- 10-15 GB free disk space (for packages and AI models)
- Internet connection for downloading dependencies

## Setup Steps

### 1. Clone the Repository (if not already done)
```bash
git clone <your-repo-url>
cd resume_parser_ai
```

### 2. Create Virtual Environment
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Or for Git Bash on Windows
python -m venv venv
source venv/Scripts/activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Upgrade pip
```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

#### Option A: Install All at Once (Recommended)
```bash
pip install -r requirements.txt
```

This will install ~80 packages including:
- FastAPI & Uvicorn (API framework)
- SQLAlchemy & Alembic (Database)
- PyTorch (CPU version - AI/ML)
- Transformers (Hugging Face models)
- spaCy (NLP)
- Document processing libraries (PyPDF2, python-docx, etc.)

**Note:** This may take 15-30 minutes depending on your internet speed.

#### Option B: Install in Groups (If Option A fails)

**Core API packages:**
```bash
pip install fastapi uvicorn[standard] python-multipart pydantic pydantic-settings sqlalchemy alembic starlette httpx python-dotenv
```

**Security & Auth:**
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

**Database:**
```bash
pip install psycopg2-binary aiosqlite
```

**Document Processing:**
```bash
pip install PyPDF2 python-docx pdf2image pytesseract pdfplumber tika aiofiles python-magic chardet Pillow
```

**AI/ML (largest downloads):**
```bash
pip install --extra-index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio
pip install transformers spacy nltk scikit-learn sentence-transformers
```

**Search & Async:**
```bash
pip install elasticsearch elasticsearch-dsl redis celery flower
```

**Monitoring & Logging:**
```bash
pip install prometheus-client opentelemetry-api opentelemetry-sdk python-json-logger
```

**Testing:**
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### 5. Create Necessary Directories
```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path data\uploads, models, logs

# Linux/Mac/Git Bash
mkdir -p data/uploads models logs
```

### 6. Setup Environment Configuration
Copy `.env.local` to `.env`:
```powershell
# Windows PowerShell
Copy-Item .env.local .env

# Linux/Mac/Git Bash
cp .env.local .env
```

The `.env.local` file is already configured for local development with:
- SQLite database (no PostgreSQL needed)
- Elasticsearch disabled
- Redis disabled
- Celery disabled
- All AI features enabled

### 7. Download AI Models

#### spaCy English Model (Required - ~500MB)
```bash
python -m spacy download en_core_web_trf
```

#### NLTK Data (Required - ~50MB)
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
```

### 8. Initialize Database
```bash
alembic upgrade head
```

This creates the SQLite database at `data/resume_parser.db` with all required tables.

### 9. Verify Installation
Run the local setup checker:
```bash
python start_local.py
```

This will verify:
- ✅ All directories created
- ✅ Environment variables loaded
- ✅ Database exists
- ✅ spaCy model installed

## Running the Application

### Start the API Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Options:**
- `--reload`: Auto-reload on code changes (development mode)
- `--host 0.0.0.0`: Accept connections from any IP
- `--port 8000`: Run on port 8000

### Access the Application

1. **API Documentation (Swagger UI):**
   http://localhost:8000/docs

2. **Alternative API Documentation (ReDoc):**
   http://localhost:8000/redoc

3. **Health Check:**
   http://localhost:8000/health

### Import Kaggle Dataset
Once the server is running, import the 2,484 resumes:
```bash
python scripts/import_kaggle_dataset.py
```

This will:
- Process all 2,484 PDF resumes
- Extract text, entities, skills
- Calculate job matching scores
- Store in SQLite database

**Expected time:** 30-60 minutes (depending on CPU speed)

## Testing the API

### Using Swagger UI (Browser)
1. Go to http://localhost:8000/docs
2. Click on any endpoint (e.g., `POST /api/v1/resumes/upload`)
3. Click "Try it out"
4. Upload a resume file
5. Click "Execute"
6. View the response

### Using cURL (Command Line)
```bash
# Upload a resume
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/resume.pdf"

# Get parsed data
curl -X GET "http://localhost:8000/api/v1/resumes/{id}" \
  -H "accept: application/json"
```

### Using Python
```python
import requests

# Upload resume
with open("resume.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/resumes/upload",
        files={"file": f}
    )
    resume_id = response.json()["id"]

# Get parsed data
response = requests.get(f"http://localhost:8000/api/v1/resumes/{resume_id}")
print(response.json())
```

## Troubleshooting

### Issue: Package installation fails
**Solution:** Install packages in groups (see Option B above)

### Issue: spaCy model not found
**Solution:**
```bash
python -m spacy download en_core_web_trf
```

### Issue: Database not found
**Solution:**
```bash
alembic upgrade head
```

### Issue: ModuleNotFoundError
**Solution:** Ensure virtual environment is activated:
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### Issue: Port 8000 already in use
**Solution:** Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: Memory errors during dataset import
**Solution:** Process resumes in smaller batches by modifying `scripts/import_kaggle_dataset.py`

## Project Structure
```
resume_parser_ai/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── core/              # Configuration & database
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic
├── data/                  # Data storage
│   ├── kaggle_resume_dataset/  # 2,484 resumes
│   ├── uploads/           # User uploads
│   └── resume_parser.db   # SQLite database
├── models/                # AI model cache
├── logs/                  # Application logs
├── scripts/               # Utility scripts
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
└── start_local.py         # Local startup script
```

## Development Workflow

### 1. Make Code Changes
Edit files in `app/` directory

### 2. Auto-Reload
Server automatically reloads when code changes (if using `--reload`)

### 3. Run Tests
```bash
pytest
```

### 4. Check Code Quality
```bash
# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

## Performance Tips

### Local Development
- **Response Time:** 2-4 seconds per resume (CPU-only PyTorch)
- **Memory Usage:** 2-4 GB RAM
- **Disk Space:** ~10 GB (packages + models + data)

### Optimization
- Use caching for repeated extractions
- Process resumes asynchronously in production
- Consider using GPU if available (change `USE_GPU=True` in `.env`)

## Switching to Docker Later

All Docker files are already in place:
- `docker-compose.yml` - Full stack with 18 services
- `docker/Dockerfile` - Custom API/Celery images
- `.env` - Environment configuration

To switch to Docker:
```bash
docker-compose up -d
```

No code changes needed! The application works identically in both environments.

## Next Steps

1. ✅ Complete setup (follow steps 1-8 above)
2. ✅ Start API server
3. ✅ Test with sample resume
4. ✅ Import Kaggle dataset
5. ✅ Test resume-job matching
6. ✅ Build additional features
7. ✅ Prepare presentation slides

## Support

For issues or questions:
- Check API documentation: http://localhost:8000/docs
- Review logs in `logs/app.log`
- Check database: `sqlite3 data/resume_parser.db`

## License & Attribution

- Kaggle Dataset: https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
- Built with: FastAPI, PyTorch, spaCy, Transformers
