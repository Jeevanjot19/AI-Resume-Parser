#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [ -d "venv/Scripts" ]; then
    source venv/Scripts/activate  # Windows
else
    source venv/bin/activate     # Linux/Mac
fi

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOL
PROJECT_NAME=AI-Powered Resume Parser
API_V1_STR=/api/v1
DATABASE_URL=postgresql://user:password@localhost:5432/resume_parser
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_FILE_SIZE=10485760
WORKERS_COUNT=4
EOL

# Create database and run migrations
alembic upgrade head

echo "Setup complete! Start the application with: uvicorn app.main:app --reload"