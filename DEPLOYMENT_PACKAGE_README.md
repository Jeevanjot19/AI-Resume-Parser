# Deployment Package Documentation

This directory contains all files necessary to deploy the AI Resume Parser API.

## 📦 Package Contents

### Core Deployment Files

1. **`docker-compose.yml`** - Full production deployment with all services
   - FastAPI application
   - PostgreSQL database
   - Redis cache
   - Elasticsearch search engine
   - Celery worker for async tasks
   - Apache Airflow for orchestration
   - Prometheus + Grafana monitoring

2. **`docker-compose.simple.yml`** - Minimal deployment (SQLite, no external services)
   - Ideal for development, demos, or small-scale deployments
   - Uses SQLite instead of PostgreSQL
   - No Redis, Elasticsearch, or monitoring stack
   - Quick start: `docker-compose -f docker-compose.simple.yml up`

3. **`docker/Dockerfile`** - Multi-stage Docker image definition
   - Python 3.11 slim base
   - Includes Tesseract OCR, Apache Tika, Poppler
   - Optimized for size and build time
   - Health check included

4. **`.dockerignore`** - Excludes unnecessary files from Docker build
   - Reduces image size
   - Speeds up build time
   - Excludes dev files, logs, virtual environments

5. **`.env.example`** - Environment variables template
   - Copy to `.env` and customize
   - Contains all configuration options
   - Includes database, Redis, API, and monitoring settings

### Supporting Files

6. **`setup.sh`** - Automated setup script (Unix/Linux/Mac)
   - Creates directories
   - Sets up Python environment
   - Downloads ML models
   - Initializes database

7. **`setup.ps1`** - Automated setup script (Windows PowerShell)
   - Same functionality as setup.sh for Windows users

8. **`requirements.txt`** - Python dependencies
   - All required packages with versions
   - Includes FastAPI, SQLAlchemy, spaCy, Transformers, etc.

---

## 🚀 Quick Start Guide

### Option 1: Simple Deployment (Recommended for Testing)

**Using SQLite, no external services required**

```bash
# 1. Clone repository
git clone <your-repo-url>
cd resume_parser_ai

# 2. Copy environment file
cp .env.example .env

# 3. Start with Docker Compose (simple)
docker-compose -f docker-compose.simple.yml up --build

# 4. API available at http://localhost:8000
# Swagger UI: http://localhost:8000/api/v1/docs
```

### Option 2: Full Production Deployment

**With PostgreSQL, Redis, Elasticsearch, monitoring**

```bash
# 1. Clone repository
git clone <your-repo-url>
cd resume_parser_ai

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings (database passwords, etc.)

# 3. Start all services
docker-compose up --build -d

# 4. Wait for services to be ready (30-60 seconds)
docker-compose ps

# 5. Access services
# API: http://localhost:8000
# Swagger UI: http://localhost:8000/api/v1/docs
# Airflow: http://localhost:8080
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
# Elasticsearch: http://localhost:9200
```

### Option 3: Local Development (Without Docker)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd resume_parser_ai

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# Or on Windows:
# .\setup.ps1

# 3. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 4. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. API available at http://localhost:8000
```

---

## 🔧 Configuration

### Environment Variables (.env file)

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/resume_parser
# Or for SQLite: DATABASE_URL=sqlite:///./data/resume_parser.db

# API
API_V1_STR=/api/v1
PROJECT_NAME=AI Resume Parser

# CORS (adjust for your frontend)
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

**Optional Variables:**
```bash
# Redis (for caching)
REDIS_URL=redis://redis:6379/0

# Elasticsearch (for search)
ELASTICSEARCH_URL=http://elasticsearch:9200

# JWT (for authentication)
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Docker Compose Profiles

The full `docker-compose.yml` can be used selectively:

```bash
# API only (with dependencies)
docker-compose up api postgres redis

# API + Search
docker-compose up api postgres redis elasticsearch

# API + Monitoring
docker-compose up api postgres redis prometheus grafana

# All services
docker-compose up
```

---

## 📊 Service Architecture

### Simple Deployment (docker-compose.simple.yml)
```
┌──────────────────┐
│   FastAPI App    │ :8000
│   (SQLite DB)    │
└──────────────────┘
```

### Full Deployment (docker-compose.yml)
```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│  FastAPI    │───▶│ PostgreSQL   │    │    Redis      │
│    API      │    │   Database   │◀───│    Cache      │
│   :8000     │    │    :5432     │    │    :6379      │
└─────────────┘    └──────────────┘    └───────────────┘
       │
       ├──────────▶┌──────────────┐    ┌───────────────┐
       │           │ Elasticsearch│    │    Celery     │
       │           │    Search    │    │    Worker     │
       │           │    :9200     │    │               │
       │           └──────────────┘    └───────────────┘
       │
       └──────────▶┌──────────────┐    ┌───────────────┐
                   │  Prometheus  │    │   Grafana     │
                   │  Monitoring  │───▶│  Dashboard    │
                   │    :9090     │    │    :3000      │
                   └──────────────┘    └───────────────┘
```

---

## 🧪 Testing the Deployment

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T12:00:00.000000",
  "version": "1.0.0"
}
```

### Upload Test Resume
```bash
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_resume.pdf"
```

### Access Swagger UI
Open browser: http://localhost:8000/api/v1/docs

---

## 🔍 Troubleshooting

### Issue: Containers won't start
```bash
# Check logs
docker-compose logs api

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Issue: Port already in use
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Issue: Database connection errors
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database URL in .env
echo $DATABASE_URL

# Reset database
docker-compose down -v postgres
docker-compose up postgres -d
```

### Issue: Models not loading
```bash
# Models are downloaded on first run
# Check logs for download progress
docker-compose logs -f api

# Or pre-download models
docker-compose exec api python -m spacy download en_core_web_lg
```

---

## 📝 Deployment Checklist

Before deploying to production:

- [ ] Update `.env` with production values
- [ ] Change default passwords (PostgreSQL, Grafana, etc.)
- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Configure `BACKEND_CORS_ORIGINS` for your domain
- [ ] Set up SSL/TLS (use nginx reverse proxy)
- [ ] Configure backup strategy for PostgreSQL
- [ ] Set up monitoring alerts in Grafana
- [ ] Configure log rotation
- [ ] Test health checks and readiness
- [ ] Set resource limits in docker-compose.yml
- [ ] Document any custom configuration

---

## 🔐 Security Considerations

### Production Deployment

1. **Use HTTPS**: Deploy behind nginx with SSL certificates
2. **Secure Passwords**: Change all default passwords
3. **Firewall Rules**: Restrict access to database ports
4. **Environment Variables**: Never commit `.env` to git
5. **API Keys**: Use secrets management (AWS Secrets Manager, HashiCorp Vault)
6. **Rate Limiting**: Enable rate limiting in nginx or API
7. **Database Backups**: Automated daily backups with retention policy

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 Monitoring

### Prometheus Metrics
- Available at: http://localhost:9090
- Metrics endpoint: http://localhost:8000/metrics

### Grafana Dashboards
- Available at: http://localhost:3000
- Default login: admin/admin
- Pre-configured dashboards for:
  - API request rates
  - Response times
  - Error rates
  - Database connections
  - System resources

---

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### Database Migrations
```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"
```

### Backup Database
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U postgres resume_parser > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres resume_parser < backup.sql
```

---

## 📞 Support

For issues or questions:
- Check the logs: `docker-compose logs -f`
- Review documentation in `docs/`
- Open an issue on GitHub
- Contact: your-email@example.com

---

## 📄 License

[Your License Here]

---

**Last Updated**: November 5, 2025
**Version**: 1.0.0
