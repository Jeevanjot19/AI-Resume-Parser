# Database Schema Documentation

## Overview
The Resume Parser AI uses SQLite for development and is PostgreSQL-ready for production deployment. The schema is designed for efficient resume storage, processing tracking, and job matching capabilities.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                          RESUMES                            │
├─────────────────────────────────────────────────────────────┤
│ PK │ id                UUID                                 │
│    │ filename          VARCHAR(255)                         │
│    │ file_hash         VARCHAR(64)      UNIQUE             │
│    │ file_size         INTEGER                             │
│    │ mime_type         VARCHAR(100)                        │
│    │ structured_data   JSON                                │
│    │ ai_enhancements   JSON                                │
│    │ processing_status ENUM                                │
│    │ uploaded_at       TIMESTAMP                           │
│    │ processed_at      TIMESTAMP        NULLABLE           │
│    │ created_at        TIMESTAMP                           │
│    │ updated_at        TIMESTAMP                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Tables

### 1. `resumes` Table

Primary table storing resume data and processing information.

#### Schema Definition (SQL)

```sql
CREATE TABLE resumes (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- File Metadata
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- Parsed Data (JSON)
    structured_data JSON,
    ai_enhancements JSON,
    
    -- Processing Status
    processing_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (processing_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    
    -- Timestamps
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_resume_hash ON resumes(file_hash);
CREATE INDEX idx_resume_status ON resumes(processing_status);
CREATE INDEX idx_resume_uploaded ON resumes(uploaded_at DESC);
CREATE INDEX idx_resume_processed ON resumes(processed_at DESC) WHERE processed_at IS NOT NULL;
```

#### Column Descriptions

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | UUID | Unique resume identifier | PRIMARY KEY |
| `filename` | VARCHAR(255) | Original filename | NOT NULL |
| `file_hash` | VARCHAR(64) | SHA-256 hash for deduplication | UNIQUE, NOT NULL |
| `file_size` | INTEGER | File size in bytes | NOT NULL |
| `mime_type` | VARCHAR(100) | MIME type (application/pdf, etc.) | NOT NULL |
| `structured_data` | JSON | Parsed resume content | - |
| `ai_enhancements` | JSON | AI-generated insights | - |
| `processing_status` | VARCHAR(20) | Current processing state | ENUM, NOT NULL |
| `uploaded_at` | TIMESTAMP | Upload timestamp | NOT NULL |
| `processed_at` | TIMESTAMP | Completion timestamp | NULLABLE |
| `created_at` | TIMESTAMP | Record creation time | NOT NULL |
| `updated_at` | TIMESTAMP | Last update time | NOT NULL |

#### Processing Status Values

```python
class ProcessingStatus(str, Enum):
    PENDING = "PENDING"         # Uploaded, waiting to process
    PROCESSING = "PROCESSING"   # Currently being processed
    COMPLETED = "COMPLETED"     # Successfully processed
    FAILED = "FAILED"           # Processing failed
```

---

## JSON Schema Structures

### `structured_data` JSON Field

Contains the parsed resume information in a structured format.

```json
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "zip_code": "94102",
      "country": "USA"
    },
    "linkedin": "https://linkedin.com/in/johndoe",
    "website": "https://johndoe.com"
  },
  
  "summary": {
    "text": "Experienced software engineer...",
    "years_of_experience": 5.5,
    "career_level": "Senior"
  },
  
  "work_experiences": [
    {
      "job_title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "start_date": "2020-01-15",
      "end_date": "present",
      "duration": "3 years 10 months",
      "description": "Led development of...",
      "responsibilities": [
        "Designed and implemented microservices",
        "Mentored junior developers"
      ],
      "technologies": ["Python", "FastAPI", "Docker"]
    }
  ],
  
  "education": [
    {
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "institution": "Stanford University",
      "location": "Stanford, CA",
      "graduation_date": "2018-06-15",
      "gpa": "3.8",
      "honors": ["Magna Cum Laude"]
    }
  ],
  
  "skills": {
    "technical_skills": [
      {"name": "Python", "level": "Expert", "years": 5},
      {"name": "JavaScript", "level": "Advanced", "years": 4}
    ],
    "soft_skills": [
      "Leadership",
      "Communication",
      "Problem Solving"
    ],
    "languages": [
      {"language": "English", "proficiency": "Native"},
      {"language": "Spanish", "proficiency": "Intermediate"}
    ]
  },
  
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuer": "Amazon Web Services",
      "date": "2022-03-15",
      "expiry": "2025-03-15",
      "credential_id": "ABC123"
    }
  ],
  
  "total_experience_years": 5.5,
  "career_level": {
    "label": "Senior",
    "confidence": 0.92
  }
}
```

### `ai_enhancements` JSON Field

Contains AI-generated insights and analysis.

```json
{
  "quality_score": 85,
  "completeness_score": 90,
  
  "industry_matches": [
    {
      "industry": "Technology",
      "confidence": 0.95,
      "evidence": ["Software Engineer roles", "Tech companies"]
    },
    {
      "industry": "Finance",
      "confidence": 0.45,
      "evidence": ["Fintech experience"]
    }
  ],
  
  "skill_gaps": [
    {
      "skill": "Kubernetes",
      "importance": "high",
      "suggestion": "Consider obtaining Kubernetes certification"
    }
  ],
  
  "improvement_suggestions": [
    "Add quantifiable achievements (e.g., 'Improved performance by 40%')",
    "Include more specific project outcomes",
    "Add links to portfolio/GitHub projects"
  ],
  
  "career_path_analysis": {
    "current_level": "Senior Engineer",
    "potential_next_roles": [
      "Staff Engineer",
      "Engineering Manager",
      "Tech Lead"
    ],
    "recommended_skills": [
      "System Design",
      "Team Leadership",
      "Strategic Planning"
    ]
  },
  
  "resume_strengths": [
    "Strong technical background",
    "Progressive career growth",
    "Diverse technology stack"
  ],
  
  "resume_weaknesses": [
    "Limited management experience",
    "Few quantifiable achievements",
    "Lacks certifications"
  ]
}
```

---

## Indexes

### Primary Index
```sql
PRIMARY KEY (id)
```

### Secondary Indexes

1. **File Hash Index** (for deduplication)
```sql
CREATE UNIQUE INDEX idx_resume_hash ON resumes(file_hash);
```

2. **Status Index** (for filtering by processing status)
```sql
CREATE INDEX idx_resume_status ON resumes(processing_status);
```

3. **Upload Time Index** (for sorting recent uploads)
```sql
CREATE INDEX idx_resume_uploaded ON resumes(uploaded_at DESC);
```

4. **Processed Time Index** (for completed resumes)
```sql
CREATE INDEX idx_resume_processed ON resumes(processed_at DESC) 
WHERE processed_at IS NOT NULL;
```

---

## Query Examples

### 1. Get Resume by ID
```sql
SELECT id, filename, structured_data, processing_status, uploaded_at
FROM resumes
WHERE id = '550e8400-e29b-41d4-a716-446655440000';
```

### 2. Check for Duplicate (by file hash)
```sql
SELECT id, filename
FROM resumes
WHERE file_hash = 'abc123...';
```

### 3. Get All Completed Resumes
```sql
SELECT id, filename, uploaded_at, processed_at
FROM resumes
WHERE processing_status = 'COMPLETED'
ORDER BY processed_at DESC
LIMIT 50;
```

### 4. Get Pending Resumes for Processing
```sql
SELECT id, filename, uploaded_at
FROM resumes
WHERE processing_status = 'PENDING'
ORDER BY uploaded_at ASC
LIMIT 10;
```

### 5. Search Resumes by Skills (JSON query)
```sql
-- PostgreSQL JSON query
SELECT id, filename, structured_data->'personal_info'->>'full_name' as name
FROM resumes
WHERE processing_status = 'COMPLETED'
  AND structured_data->'skills'->'technical_skills' @> '[{"name": "Python"}]';
```

### 6. Get Processing Statistics
```sql
SELECT 
    processing_status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (processed_at - uploaded_at))) as avg_processing_time_seconds
FROM resumes
WHERE processed_at IS NOT NULL
GROUP BY processing_status;
```

### 7. Get Recently Uploaded Resumes
```sql
SELECT id, filename, uploaded_at, processing_status
FROM resumes
WHERE uploaded_at >= NOW() - INTERVAL '24 hours'
ORDER BY uploaded_at DESC;
```

---

## Database Migrations

Using Alembic for schema versioning:

### Migration Files Structure
```
alembic/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_ai_enhancements.py
│   └── 003_add_indexes.py
└── env.py
```

### Creating a New Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

---

## Performance Considerations

### 1. Index Usage
- File hash index ensures O(1) duplicate detection
- Status index optimizes filtering by processing state
- Time-based indexes support efficient pagination

### 2. JSON Query Optimization (PostgreSQL)
```sql
-- Create GIN index for JSON queries
CREATE INDEX idx_resume_skills 
ON resumes USING GIN (structured_data->'skills');

-- Create index for specific JSON path
CREATE INDEX idx_resume_email 
ON resumes ((structured_data->'personal_info'->>'email'));
```

### 3. Partitioning (for large datasets)
```sql
-- Partition by month (PostgreSQL)
CREATE TABLE resumes_2025_01 PARTITION OF resumes
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

## Data Integrity

### 1. Constraints
- **Primary Key**: Ensures unique resume IDs
- **Unique Constraint**: Prevents duplicate file uploads
- **Check Constraint**: Validates processing status enum
- **Not Null**: Required fields cannot be empty

### 2. Triggers (PostgreSQL)
```sql
-- Auto-update updated_at timestamp
CREATE TRIGGER update_resumes_updated_at
BEFORE UPDATE ON resumes
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

### 3. Cascading Deletes
```sql
-- If adding related tables in future
ALTER TABLE resume_matches
ADD CONSTRAINT fk_resume
FOREIGN KEY (resume_id) REFERENCES resumes(id)
ON DELETE CASCADE;
```

---

## Backup Strategy

### SQLite (Development)
```bash
# Full backup
sqlite3 data/resume_parser.db ".backup 'backup.db'"

# Dump to SQL
sqlite3 data/resume_parser.db ".dump" > backup.sql
```

### PostgreSQL (Production)
```bash
# Logical backup
pg_dump -U user -d resume_parser > backup.sql

# Point-in-time recovery (continuous archiving)
# Configure in postgresql.conf:
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

---

## Monitoring Queries

### 1. Database Size
```sql
-- PostgreSQL
SELECT pg_size_pretty(pg_database_size('resume_parser'));

-- SQLite
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();
```

### 2. Table Statistics
```sql
SELECT 
    COUNT(*) as total_resumes,
    COUNT(CASE WHEN processing_status = 'COMPLETED' THEN 1 END) as completed,
    COUNT(CASE WHEN processing_status = 'PENDING' THEN 1 END) as pending,
    COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) as failed,
    AVG(file_size) as avg_file_size,
    SUM(file_size) as total_storage
FROM resumes;
```

### 3. Performance Metrics
```sql
-- PostgreSQL
SELECT 
    schemaname, tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables
WHERE tablename = 'resumes';
```

---

## Future Schema Enhancements

### Planned Tables

1. **job_postings** - Store job descriptions
2. **resume_job_matches** - Store matching results
3. **users** - User authentication and authorization
4. **audit_log** - Track all database changes
5. **analytics** - Pre-computed metrics and statistics

### Example: resume_job_matches table
```sql
CREATE TABLE resume_job_matches (
    id UUID PRIMARY KEY,
    resume_id UUID REFERENCES resumes(id) ON DELETE CASCADE,
    job_id UUID REFERENCES job_postings(id) ON DELETE CASCADE,
    overall_score INTEGER,
    category_scores JSON,
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resume_id, job_id)
);
```

---

## Schema Version

**Current Version**: 1.0.0
**Last Updated**: November 5, 2025
**Alembic Revision**: `001_initial_schema`
