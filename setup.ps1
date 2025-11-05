# Setup script for Resume Parser AI - Local Development (Windows)
# This script sets up the complete project after git clone on local machine

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Resume Parser AI - Local Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.11 or higher." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null
Write-Host "✅ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing Python packages..." -ForegroundColor Yellow
Write-Host "(This may take 15-30 minutes)" -ForegroundColor Gray
pip install -r requirements.txt
Write-Host "✅ All packages installed" -ForegroundColor Green
Write-Host ""

# Create necessary directories
Write-Host "Creating project directories..." -ForegroundColor Yellow
$directories = @("data\uploads", "models", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Directories created" -ForegroundColor Green
Write-Host ""

# Setup environment file
Write-Host "Setting up environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    $envContent = @"
# Local Development Environment Configuration
APP_NAME=Resume Parser AI
DEBUG=True
DATABASE_URL=sqlite:///./data/resume_parser.db
SECRET_KEY=local-dev-secret-key-change-in-production
REDIS_ENABLED=False
ELASTICSEARCH_ENABLED=False
CELERY_ENABLED=False
USE_GPU=False
MODEL_CACHE_DIR=./models
UPLOAD_DIR=./data/uploads
LOG_LEVEL=INFO
"@
    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "✅ Created .env file for local development" -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}
Write-Host ""

# Download spaCy model
Write-Host "Downloading spaCy NLP model..." -ForegroundColor Yellow
Write-Host "(This may take several minutes)" -ForegroundColor Gray
try {
    python -m spacy download en_core_web_trf
    Write-Host "✅ spaCy model downloaded" -ForegroundColor Green
} catch {
    Write-Host "⚠️  spaCy model download failed. You can download it later with:" -ForegroundColor Yellow
    Write-Host "   python -m spacy download en_core_web_trf" -ForegroundColor Gray
}
Write-Host ""

# Download NLTK data
Write-Host "Downloading NLTK data..." -ForegroundColor Yellow
try {
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
    Write-Host "✅ NLTK data downloaded" -ForegroundColor Green
} catch {
    Write-Host "⚠️  NLTK data download failed. You can download it later." -ForegroundColor Yellow
}
Write-Host ""

# Initialize database
Write-Host "Setting up database..." -ForegroundColor Yellow
if (-not (Test-Path "data\resume_parser.db")) {
    Write-Host "Running database migrations..." -ForegroundColor Gray
    try {
        alembic upgrade head
        Write-Host "✅ Database initialized" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Database migration failed. You may need to run 'alembic upgrade head' manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Database already exists" -ForegroundColor Green
}
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor White
Write-Host "  1. Activate virtual environment:" -ForegroundColor Yellow
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start the API server:" -ForegroundColor Yellow
Write-Host "     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Access the API documentation:" -ForegroundColor Yellow
Write-Host "     http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Import the Kaggle dataset:" -ForegroundColor Yellow
Write-Host "     python scripts/import_kaggle_dataset.py" -ForegroundColor Gray
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
