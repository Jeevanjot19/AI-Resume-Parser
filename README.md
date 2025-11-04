# AI-Powered Resume Parser

Production-ready AI-powered resume parsing and job matching system with semantic search capabilities.

## Features

### Core Functionality
- **Multi-format Support**: Parse resumes in PDF, DOCX, TXT, and image formats
- **AI-Powered Extraction**: Advanced NER for extracting personal info, skills, experience, education
- **Semantic Search**: Vector embeddings for intelligent resume search
- **Job Matching**: Multi-dimensional scoring algorithm (85%+ accuracy target)
- **Quality Analysis**: AI-driven resume quality assessment and improvement suggestions
- **Career Path Analysis**: Industry classification and career level determination

### Technical Highlights
- **Async Processing**: Celery task queue for background resume processing
- **High Performance**: Redis caching, <5s response time target
- **Scalable Architecture**: Docker Compose orchestration, Kubernetes-ready
- **Comprehensive Monitoring**: Prometheus, Grafana, ELK stack, Sentry integration
- **Production-Ready**: Health checks, error handling, logging, CI/CD pipeline

## Tech Stack

### Backend Framework
- **FastAPI**: Modern async web framework
- **Python 3.11+**: Latest Python features

### Databases & Search
- **PostgreSQL 15**: Primary database with JSONB support
- **Elasticsearch 8**: Full-text search with vector embeddings
- **Redis**: Caching and Celery broker

### AI/ML Components
- **Hugging Face Transformers**: BERT-based NER, zero-shot classification
- **spaCy**: Fast NER processing
- **sentence-transformers**: Semantic embeddings (768-dim vectors)
- **LangChain + OpenAI**: LLM orchestration for analysis

### Document Processing
- **Apache Tika**: Primary document extraction
- **PyPDF2 & pdfplumber**: PDF parsing with fallback
- **python-docx**: DOCX parsing
- **Tesseract OCR**: Image text extraction

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **Celery**: Async task queue
- **GitHub Actions**: CI/CD pipeline

### Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **ELK Stack**: Centralized logging
- **Sentry**: Error tracking

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Jeevanjot19/AI-Resume-Parser.git
cd AI-Resume-Parser
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Run Migrations
```bash
docker-compose exec api alembic upgrade head
```

### 5. Import Kaggle Dataset (Optional)

**Option A - Manual Download (Recommended):**
1. Download from https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
2. Extract and copy `Resume.csv` to `data\kaggle_resume_dataset\Resume.csv`
3. Run: `python scripts/import_kaggle_dataset.py`

**Option B - Automated Download:**
```bash
python scripts/download_kaggle_dataset.py  # Requires Kaggle API key
python scripts/import_kaggle_dataset.py
```

📖 See [Kaggle Dataset Guide](docs/KAGGLE_DATASET_GUIDE.md) for detailed instructions.

### 6. Access API
- **API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Grafana**: http://localhost:3000 (admin/admin)

## API Endpoints

### Resume Operations

#### Upload Resume
```http
POST /api/v1/resumes/upload
Content-Type: multipart/form-data

file: <resume_file>
```

#### Get Resume
```http
GET /api/v1/resumes/{resume_id}
```

#### Get AI Analysis
```http
GET /api/v1/resumes/{resume_id}/analysis
```

#### Match with Job
```http
POST /api/v1/resumes/{resume_id}/match
```

#### Search Resumes
```http
POST /api/v1/resumes/search
```

### Health Checks
```http
GET /api/v1/health
GET /api/v1/health/ready
GET /api/v1/health/live
```

## License

MIT License
