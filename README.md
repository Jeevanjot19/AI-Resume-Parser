# AI-Powered Resume Parser

An intelligent resume parsing system built using FastAPI, AI/ML technologies, and modern architecture practices.

## Features

- Multi-format resume parsing (PDF, DOCX, TXT, Images)
- AI-powered data extraction with context understanding
- Resume-Job matching with detailed scoring
- RESTful API with OpenAPI 3.1 specification
- Scalable architecture with Docker support

## Tech Stack

- **Backend:** FastAPI, Python 3.11+
- **AI/ML:** Hugging Face Transformers, spaCy, Tesseract OCR
- **Database:** PostgreSQL
- **Infrastructure:** Docker, Docker Compose
- **Documentation:** OpenAPI/Swagger

## Quick Start

1. Clone the repository
```bash
git clone https://github.com/yourusername/resume-parser-ai.git
cd resume-parser-ai
```

2. Run setup script
```bash
./setup.sh
```

3. Start with Docker Compose
```bash
docker-compose up -d
```

4. Access API documentation at http://localhost:8000/docs

## Architecture

The system uses a microservices-based architecture with the following components:

- API Service: FastAPI-based REST API
- Parser Service: Resume parsing and data extraction
- AI Service: ML models for enhanced parsing and matching
- Database Service: PostgreSQL for data persistence
- Cache Service: Redis for performance optimization

## Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## License

MIT