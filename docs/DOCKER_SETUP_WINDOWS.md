# Docker Desktop Installation Guide for Windows

## Prerequisites Check

✅ Windows 10/11 (64-bit)
✅ Hardware virtualization enabled in BIOS
✅ WSL 2 (Windows Subsystem for Linux)

## Step 1: Enable WSL 2

Open PowerShell as Administrator and run:

```powershell
# Enable WSL
wsl --install

# Set WSL 2 as default
wsl --set-default-version 2

# Install Ubuntu (recommended)
wsl --install -d Ubuntu
```

**Note:** You may need to restart your computer after this step.

## Step 2: Download Docker Desktop

1. Go to: https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Run the installer: `Docker Desktop Installer.exe`

## Step 3: Install Docker Desktop

1. Double-click the installer
2. Keep "Use WSL 2 instead of Hyper-V" checked
3. Follow the installation wizard
4. Restart your computer when prompted

## Step 4: Configure Docker Desktop

1. Launch Docker Desktop
2. Accept the service agreement
3. Skip the survey (optional)
4. Go to Settings (gear icon):
   - **General**: Ensure "Use WSL 2 based engine" is checked
   - **Resources > WSL Integration**: Enable integration with Ubuntu
   - **Resources**: Allocate at least:
     - 4 GB RAM (recommended: 8 GB)
     - 2 CPUs (recommended: 4 CPUs)

## Step 5: Verify Installation

Open a new PowerShell window and run:

```powershell
docker --version
docker-compose --version
docker ps
```

You should see version information and no errors.

## Step 6: Start the Resume Parser Services

Once Docker is running:

```powershell
cd "d:\gemini hackathon\resume_parser_ai"

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

## Services Overview

After starting, you'll have:

- **PostgreSQL**: `localhost:5432` - Main database
- **Elasticsearch**: `localhost:9200` - Search engine
- **Redis**: `localhost:6379` - Cache & message broker
- **Kibana**: `localhost:5601` - Elasticsearch UI (optional)

## Troubleshooting

### WSL 2 Installation Issues

If WSL install fails:

```powershell
# Enable required Windows features
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer, then install WSL kernel update
# Download from: https://aka.ms/wsl2kernel
```

### Docker Desktop Won't Start

1. Check if virtualization is enabled in BIOS/UEFI
2. Ensure Hyper-V is enabled (for older systems):
   ```powershell
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```
3. Run Docker Desktop as Administrator

### Docker Compose Command Not Found

Docker Desktop includes docker-compose. If not working:

```powershell
# Install docker-compose separately
pip install docker-compose
```

## Quick Start After Docker Installation

```powershell
# 1. Start all services
cd "d:\gemini hackathon\resume_parser_ai"
docker-compose up -d

# 2. Wait for services to be healthy (30-60 seconds)
Start-Sleep -Seconds 60

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Run database migrations
alembic upgrade head

# 6. Import Kaggle dataset
python scripts/import_kaggle_dataset.py

# 7. Start the API
uvicorn app.main:app --reload
```

## Next Steps

Once Docker is installed and services are running:

1. ✅ Dataset is already loaded (2,484 resumes)
2. ✅ Import resumes into database
3. ✅ Test the API endpoints
4. ✅ Run example queries

## Support

- Docker Desktop Docs: https://docs.docker.com/desktop/windows/
- WSL 2 Guide: https://docs.microsoft.com/en-us/windows/wsl/install
- Project README: `README.md`

---

**Estimated Time**: 20-30 minutes (including restarts)
