# Architecture Documentation

## System Overview

The AI-Powered Resume Parser is a production-ready FastAPI application that parses resumes, extracts structured information, and provides intelligent job matching using AI/ML technologies.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Swagger UI   │  │   Web App    │  │  Mobile App  │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                       │
│         └──────────────────┴──────────────────┘                       │
│                            │                                          │
└────────────────────────────┼──────────────────────────────────────────┘
                             │
                             │ HTTPS/REST API
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     API Gateway Layer (FastAPI)                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  CORS Middleware │ Authentication │ Rate Limiting │ Logging  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Application Layer (FastAPI)                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    API Endpoints (v1)                          │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │ │
│  │  │  Resumes   │  │    Jobs    │  │   Health   │             │ │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │ │
│  │        │               │               │                      │ │
│  │        └───────────────┴───────────────┘                      │ │
│  │                        │                                       │ │
│  └────────────────────────┼───────────────────────────────────── │ │
│                           │                                        │ │
│  ┌────────────────────────┼────────────────────────────────────┐ │ │
│  │           Business Logic / Service Layer                     │ │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │ │ │
│  │  │ Resume Parser│  │ Job Matcher  │  │ AI Enhancer  │      │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │ │ │
│  │         │                  │                  │               │ │ │
│  │         └──────────────────┴──────────────────┘               │ │ │
│  │                            │                                   │ │ │
│  └────────────────────────────┼───────────────────────────────── │ │
│                               │                                    │ │
│  ┌────────────────────────────┼────────────────────────────────┐ │ │
│  │              Data Access Layer (DAL)                         │ │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │ │ │
│  │  │SQLAlchemy ORM│  │  Cache Layer │  │ File Storage │      │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │ │ │
│  │         │                  │                  │               │ │ │
│  └─────────┼──────────────────┼──────────────────┼──────────────┘ │ │
│            │                  │                  │                 │ │
└────────────┼──────────────────┼──────────────────┼─────────────────┘
             │                  │                  │
             ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Data Storage Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   SQLite     │  │    Redis     │  │ File System  │             │
│  │  (Database)  │  │   (Cache)    │  │   (Uploads)  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     External Services Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Apache Tika  │  │ HuggingFace  │  │    spaCy     │             │
│  │(File Parser) │  │  (Embeddings)│  │     (NLP)    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Gateway Layer
- **FastAPI Framework**: High-performance async web framework
- **CORS Middleware**: Cross-origin request handling
- **Rate Limiting**: Request throttling for API protection
- **Request/Response Logging**: Comprehensive audit trail

### 2. API Endpoints (RESTful)

#### Resume Management
- `POST /api/v1/resumes/upload` - Upload resume files (PDF, DOCX)
- `GET /api/v1/resumes/{id}` - Retrieve parsed resume data
- `GET /api/v1/resumes` - List all resumes (paginated)
- `GET /api/v1/resumes/search` - Semantic search
- `DELETE /api/v1/resumes/{id}` - Delete resume

#### Job Matching
- `POST /api/v1/resumes/{id}/match` - Match resume with job description
- `POST /api/v1/jobs/{id}/match` - Alternative job matching endpoint

#### Analytics & Monitoring
- `GET /api/v1/resumes/{id}/status` - Processing status
- `GET /api/v1/resumes/{id}/analysis` - AI quality analysis
- `GET /api/v1/health` - Health check

### 3. Business Logic Layer

#### Resume Parser Service
- **File Processing**: Apache Tika for text extraction
- **Text Cleaning**: Remove noise, normalize formatting
- **Entity Extraction**: spaCy NLP for named entities
- **Structure Detection**: Pattern matching for sections
- **Data Validation**: Pydantic models for type safety

#### Job Matcher Service
- **Skill Matching**: Token-based similarity (35% weight)
- **Experience Matching**: Years and level comparison (25% weight)
- **Education Matching**: Degree and field relevance (15% weight)
- **Role Alignment**: Title and responsibility overlap (15% weight)
- **Location Matching**: Geographic compatibility (10% weight)
- **Gap Analysis**: Identify skill gaps and improvement areas
- **Salary Alignment**: Compensation range analysis

#### AI Enhancement Service
- **Quality Scoring**: Resume completeness and quality metrics
- **Skill Gap Analysis**: Identify missing critical skills
- **Career Path Prediction**: Industry and role suggestions
- **Improvement Recommendations**: AI-generated suggestions

### 4. Data Access Layer

#### SQLAlchemy ORM
- **Models**: Resume, Job, Match (with relationships)
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Indexed fields for fast lookups
- **Migration Support**: Alembic for schema versioning

#### Cache Layer (Redis - Optional)
- **Session Cache**: User session data
- **Query Cache**: Frequent database queries
- **Rate Limit Counters**: API throttling state

#### File Storage
- **Local Storage**: `./data/uploads/` for resume files
- **Hash-based Deduplication**: Prevent duplicate uploads
- **Organized Structure**: Date-based directory hierarchy

### 5. Data Storage

#### SQLite Database
```sql
CREATE TABLE resumes (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    file_hash TEXT UNIQUE,
    file_size INTEGER,
    mime_type TEXT,
    structured_data JSON,
    ai_enhancements JSON,
    processing_status TEXT,
    uploaded_at TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE INDEX idx_resume_hash ON resumes(file_hash);
CREATE INDEX idx_resume_status ON resumes(processing_status);
CREATE INDEX idx_resume_uploaded ON resumes(uploaded_at);
```

### 6. External Services

#### Apache Tika
- Text extraction from PDF, DOCX, TXT
- Metadata extraction (author, dates, etc.)
- Format detection and conversion

#### HuggingFace Transformers
- Sentence embeddings for semantic search
- Zero-shot classification for skill categorization
- Named entity recognition

#### spaCy NLP
- Large English model (`en_core_web_lg`)
- Named entity recognition (PERSON, ORG, GPE)
- Part-of-speech tagging
- Dependency parsing

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.13
- **Database**: SQLite 3.x (PostgreSQL for production)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic V2
- **Migration**: Alembic

### AI/ML
- **NLP**: spaCy 3.7
- **Transformers**: HuggingFace 4.35
- **Embeddings**: sentence-transformers
- **Models**: 
  - `en_core_web_lg` (spaCy)
  - `sentence-transformers/all-MiniLM-L6-v2`

### File Processing
- **Parser**: Apache Tika 2.9.1
- **PDF**: PyPDF2
- **DOCX**: python-docx

### Infrastructure
- **Web Server**: Uvicorn (ASGI)
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx (optional)
- **Cache**: Redis (optional)

## Data Flow

### 1. Resume Upload Flow
```
User → Upload Resume (PDF/DOCX)
  ↓
API validates file (size, type, hash)
  ↓
Save to file system (./data/uploads/)
  ↓
Create DB record (status: PENDING)
  ↓
Background task: Extract text (Tika)
  ↓
Background task: Parse sections (spaCy)
  ↓
Background task: Extract entities
  ↓
Background task: Generate embeddings
  ↓
Update DB (status: COMPLETED, structured_data)
  ↓
Return resume ID to user
```

### 2. Job Matching Flow
```
User → POST /resumes/{id}/match + job_description
  ↓
Validate resume exists (status: COMPLETED)
  ↓
Extract job requirements (skills, experience, education)
  ↓
Calculate category scores:
  - Skills Match (35%)
  - Experience Match (25%)
  - Education Match (15%)
  - Role Alignment (15%)
  - Location Match (10%)
  ↓
Generate gap analysis (critical gaps, improvements)
  ↓
Calculate salary alignment
  ↓
Generate AI explanation (summary, factors, recommendations)
  ↓
Return JobMatchResponse (overall score + detailed breakdown)
```

### 3. Search Flow
```
User → GET /resumes/search?query=python
  ↓
Generate query embeddings
  ↓
Search DB for matching resumes
  ↓
Calculate semantic similarity scores
  ↓
Rank results by relevance
  ↓
Return paginated results
```

## Security Considerations

1. **Input Validation**: All inputs validated using Pydantic models
2. **File Upload Security**: 
   - Max file size: 10MB
   - Allowed types: PDF, DOCX, TXT
   - Virus scanning (optional integration)
3. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
4. **CORS**: Configured for allowed origins
5. **Rate Limiting**: API throttling to prevent abuse
6. **Authentication**: Ready for JWT/OAuth integration
7. **HTTPS**: TLS/SSL in production

## Scalability Considerations

1. **Horizontal Scaling**: Stateless API design
2. **Database**: 
   - SQLite for development
   - PostgreSQL for production
   - Read replicas for high traffic
3. **Caching**: Redis for frequently accessed data
4. **File Storage**: S3/MinIO for production
5. **Background Jobs**: Celery for async processing
6. **Load Balancing**: Nginx/HAProxy
7. **Monitoring**: Prometheus + Grafana

## Performance Optimization

1. **Database Indexing**: Key fields indexed
2. **Connection Pooling**: SQLAlchemy pool management
3. **Async Operations**: FastAPI async/await
4. **Lazy Loading**: Load data only when needed
5. **Response Compression**: Gzip compression
6. **Caching**: In-memory and Redis caching
7. **Model Loading**: Pre-load ML models at startup

## Deployment Architecture

### Development
```
Local Machine
  ├── SQLite database
  ├── File storage (local disk)
  └── Uvicorn server
```

### Production
```
                    ┌──────────────┐
                    │  Load Balancer│
                    └───────┬──────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼────┐         ┌───▼────┐         ┌───▼────┐
    │ API #1 │         │ API #2 │         │ API #3 │
    └───┬────┘         └───┬────┘         └───┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼─────┐       ┌────▼────┐        ┌────▼────┐
    │PostgreSQL│       │  Redis  │        │   S3    │
    │(Primary) │       │ (Cache) │        │ (Files) │
    └──────────┘       └─────────┘        └─────────┘
```

## Error Handling

1. **HTTP Status Codes**: Standard REST status codes
2. **Error Responses**: Structured JSON error messages
3. **Logging**: Comprehensive logging with levels
4. **Monitoring**: Health checks and metrics
5. **Retry Logic**: For transient failures
6. **Circuit Breakers**: Prevent cascade failures

## API Versioning

- **URL Versioning**: `/api/v1/` prefix
- **Backward Compatibility**: Maintain older versions
- **Deprecation Policy**: 6-month notice for breaking changes

## Future Enhancements

1. **GraphQL API**: Alternative to REST
2. **WebSocket Support**: Real-time updates
3. **Batch Processing**: Multiple resume upload
4. **Advanced Analytics**: ML-based insights
5. **Multi-language Support**: International resumes
6. **Integration APIs**: ATS/HRIS systems
7. **Mobile SDK**: Native mobile integration
