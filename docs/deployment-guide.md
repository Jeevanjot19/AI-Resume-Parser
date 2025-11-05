# Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Docker Deployment](#docker-deployment)
4. [Local Development Setup](#local-development-setup)
5. [Production Deployment](#production-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows 10/11
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **Internet**: For downloading models and dependencies

### Required Software
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Git**: For cloning repository
- **Python**: 3.10+ (for local development)

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/resume-parser-ai.git
cd resume-parser-ai
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Start Application
```bash
docker-compose up -d
```

### 4. Access API
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/api/v1/health

---

## Docker Deployment

### Using Docker Compose (Recommended)

#### 1. Configuration
Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Application
ENVIRONMENT=production
DEBUG=False
API_VERSION=1.0.0

# Database
DATABASE_URL=sqlite:///./data/resume_parser.db
# For production, use PostgreSQL:
# DATABASE_URL=postgresql://user:password@db:5432/resume_parser

# File Storage
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# ML Models
HF_HOME=./models/huggingface
TRANSFORMERS_CACHE=./models/huggingface
SPACY_MODEL=en_core_web_lg

# API Configuration
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
RATE_LIMIT=100/minute

# Optional: Redis Cache
REDIS_URL=redis://redis:6379/0

# Optional: Monitoring
SENTRY_DSN=your-sentry-dsn
```

#### 2. Build and Start
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Check status
docker-compose ps
```

#### 3. Initialize Database
```bash
# Run migrations
docker-compose exec api alembic upgrade head

# (Optional) Load sample data
docker-compose exec api python scripts/import_kaggle_dataset.py
```

#### 4. Stop Services
```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Using Docker Only

#### Build Image
```bash
docker build -t resume-parser-ai:latest -f docker/Dockerfile .
```

#### Run Container
```bash
docker run -d \
  --name resume-parser \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -e ENVIRONMENT=production \
  resume-parser-ai:latest
```

---

## Local Development Setup

### 1. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg

# Download HuggingFace models (automatic on first run)
```

### 3. Setup Database
```bash
# Create database directory
mkdir -p data

# Run migrations
alembic upgrade head

# Initialize database
python init_db.py
```

### 4. Start Development Server
```bash
# Method 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Python script
python start_local.py

# Method 3: Using setup script
./setup.sh
```

### 5. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py -v
```

---

## Production Deployment

### 1. Server Setup (Ubuntu 22.04)

#### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Create application user
sudo useradd -m -s /bin/bash resumeapp
sudo usermod -aG docker resumeapp
```

#### Setup Application
```bash
# Switch to app user
sudo su - resumeapp

# Clone repository
git clone https://github.com/yourusername/resume-parser-ai.git
cd resume-parser-ai

# Setup environment
cp .env.example .env
nano .env  # Configure production settings
```

### 2. Database Setup (PostgreSQL)

#### Install PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE resume_parser;
CREATE USER resumeapp WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE resume_parser TO resumeapp;
\q
```

#### Update Database URL
```env
DATABASE_URL=postgresql://resumeapp:secure_password@localhost:5432/resume_parser
```

### 3. Nginx Reverse Proxy

#### Install Nginx
```bash
sudo apt install nginx
```

#### Configure Nginx
Create `/etc/nginx/sites-available/resume-parser`:
```nginx
upstream api_backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/resume-parser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal is configured automatically
```

### 5. Systemd Service

Create `/etc/systemd/system/resume-parser.service`:
```ini
[Unit]
Description=Resume Parser API
After=network.target postgresql.service

[Service]
Type=simple
User=resumeapp
WorkingDirectory=/home/resumeapp/resume-parser-ai
ExecStart=/home/resumeapp/resume-parser-ai/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service
```bash
sudo systemctl enable resume-parser
sudo systemctl start resume-parser
sudo systemctl status resume-parser
```

### 6. Monitoring Setup

#### Install Prometheus (Optional)
```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

#### Install Grafana (Optional)
```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

---

## Environment Configuration

### Development (.env.local)
```env
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./data/resume_parser.db
CORS_ORIGINS=*
```

### Staging (.env.staging)
```env
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql://user:pass@staging-db:5432/resume_parser
CORS_ORIGINS=https://staging.yourdomain.com
SENTRY_DSN=your-sentry-dsn
```

### Production (.env.production)
```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/resume_parser
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
REDIS_URL=redis://redis:6379/0
SENTRY_DSN=your-sentry-dsn
RATE_LIMIT=1000/hour
```

---

## Troubleshooting

### Docker Issues

#### Container won't start
```bash
# Check logs
docker-compose logs api

# Check if port is already in use
sudo lsof -i :8000

# Rebuild without cache
docker-compose build --no-cache
```

#### Permission errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

### Database Issues

#### Migration errors
```bash
# Reset migrations
alembic downgrade base
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "description"
```

#### Connection errors
```bash
# Test database connection
docker-compose exec api python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('Connected!')"
```

### Model Loading Issues

#### spaCy model not found
```bash
# Download model manually
docker-compose exec api python -m spacy download en_core_web_lg

# Or locally
python -m spacy download en_core_web_lg
```

#### HuggingFace timeout
```bash
# Set longer timeout
export TRANSFORMERS_TIMEOUT=600

# Use mirror (China)
export HF_ENDPOINT=https://hf-mirror.com
```

### Performance Issues

#### High memory usage
```bash
# Reduce number of workers
# In docker-compose.yml, set workers to 2
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

# Or set in .env
WORKERS=2
```

#### Slow API responses
```bash
# Enable Redis caching
REDIS_URL=redis://redis:6379/0

# Optimize database queries
# Add indexes (see docs/architecture.md)

# Use connection pooling
DATABASE_POOL_SIZE=10
```

---

## Health Checks

### Application Health
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "models_loaded": true
}
```

### Container Health
```bash
docker-compose ps
docker-compose exec api curl http://localhost:8000/api/v1/health
```

---

## Backup and Recovery

### Database Backup
```bash
# SQLite
cp data/resume_parser.db data/backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump -U resumeapp resume_parser > backup_$(date +%Y%m%d).sql
```

### File Backup
```bash
# Backup uploaded files
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz data/uploads/

# Backup models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/
```

### Restore
```bash
# Restore database
cp data/backup_20250105.db data/resume_parser.db

# Restore files
tar -xzf uploads_backup_20250105.tar.gz
```

---

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
    ports:
      - "8000-8002:8000"
```

### Load Balancer (Nginx)
```nginx
upstream api_cluster {
    least_conn;
    server api1:8000;
    server api2:8000;
    server api3:8000;
}
```

---

## Support

For issues and questions:
- **GitHub Issues**: https://github.com/yourusername/resume-parser-ai/issues
- **Documentation**: https://github.com/yourusername/resume-parser-ai/wiki
- **Email**: support@yourdomain.com
