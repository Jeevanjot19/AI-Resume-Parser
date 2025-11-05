"""
Local development startup script.
This script initializes the application for local development without Docker.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_directories():
    """Create necessary directories for local development."""
    directories = [
        "data",
        "data/uploads",
        "models",
        "logs",
    ]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Created necessary directories")

def setup_environment():
    """Load environment variables from .env.local if it exists."""
    env_file = project_root / ".env.local"
    if env_file.exists():
        print(f"✅ Loading environment from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        print("⚠️  .env.local not found, using default settings")

def check_database():
    """Check if database is initialized."""
    db_path = Path("data/resume_parser.db")
    if not db_path.exists():
        print("ℹ️  Database not found. You may need to run migrations:")
        print("   alembic upgrade head")
    else:
        print(f"✅ Database found at {db_path}")

def check_spacy_model():
    """Check if spaCy model is downloaded."""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_trf")
            print("✅ spaCy model 'en_core_web_trf' is installed")
        except OSError:
            print("⚠️  spaCy model not found. Download with:")
            print("   python -m spacy download en_core_web_trf")
    except ImportError:
        print("⚠️  spaCy not installed yet")

def main():
    """Main startup routine."""
    print("=" * 60)
    print("🚀 Resume Parser AI - Local Development Setup")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Load environment
    setup_environment()
    
    # Check database
    check_database()
    
    # Check AI models
    check_spacy_model()
    
    print("=" * 60)
    print("✅ Local environment ready!")
    print("\nTo start the API server, run:")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAPI docs will be available at:")
    print("   http://localhost:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    main()
