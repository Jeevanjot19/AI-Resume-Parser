#!/bin/bash
# Setup script for Resume Parser AI - Local Development
# This script sets up the complete project after git clone on local machine

set -e  # Exit on error

echo "======================================"
echo "Resume Parser AI - Local Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
if [ -d "venv/Scripts" ]; then
    source venv/Scripts/activate  # Windows Git Bash
elif [ -d "venv/bin" ]; then
    source venv/bin/activate      # Linux/Mac
fi
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "Installing Python packages..."
echo "(This may take 15-30 minutes)"
pip install -r requirements.txt
echo "✅ All packages installed"
echo ""

# Create necessary directories
echo "Creating project directories..."
mkdir -p data/uploads models logs
echo "✅ Directories created"
echo ""

# Setup environment file for local development
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOL'
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
EOL
    echo "✅ Created .env file for local development"
else
    echo "✅ .env file already exists"
fi
echo ""

# Download spaCy model
echo "Downloading spaCy NLP model..."
echo "(This may take several minutes)"
python -m spacy download en_core_web_trf || echo "⚠️  spaCy model download failed. You can download it later."
echo ""

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')" || echo "⚠️  NLTK data download failed. You can download it later."
echo ""

# Initialize database
echo "Setting up database..."
if [ ! -f "data/resume_parser.db" ]; then
    echo "Running database migrations..."
    alembic upgrade head || echo "⚠️  Database migration failed. You may need to run 'alembic upgrade head' manually."
else
    echo "✅ Database already exists"
fi
echo ""

echo "======================================"
echo "✅ Setup complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate  (Linux/Mac)"
echo "     venv\\Scripts\\activate     (Windows)"
echo ""
echo "  2. Start the API server:"
echo "     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  3. Access the API documentation:"
echo "     http://localhost:8000/docs"
echo ""
echo "  4. Import the Kaggle dataset:"
echo "     python scripts/import_kaggle_dataset.py"
echo ""
echo "======================================"