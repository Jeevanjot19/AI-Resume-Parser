# Docker Desktop Setup Script for Windows
# Run this in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Desktop Setup for Resume Parser AI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Right-click on PowerShell" -ForegroundColor Yellow
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "3. Navigate to this directory and run the script again" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Step 1: Check Windows version
Write-Host "[Step 1/5] Checking Windows version..." -ForegroundColor Cyan
$osVersion = [System.Environment]::OSVersion.Version
if ($osVersion.Major -lt 10) {
    Write-Host "❌ ERROR: Windows 10 or later is required!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Windows version: $($osVersion.Major).$($osVersion.Minor)" -ForegroundColor Green
Write-Host ""

# Step 2: Enable WSL
Write-Host "[Step 2/5] Enabling WSL (Windows Subsystem for Linux)..." -ForegroundColor Cyan
try {
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    Write-Host "✓ WSL features enabled" -ForegroundColor Green
} catch {
    Write-Host "⚠ WSL feature installation encountered an issue: $_" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Check if restart is needed
Write-Host "[Step 3/5] Checking if restart is required..." -ForegroundColor Cyan
Write-Host "⚠ A system restart is typically required after enabling WSL features." -ForegroundColor Yellow
Write-Host ""

$restart = Read-Host "Do you want to restart now? (Y/N)"
if ($restart -eq 'Y' -or $restart -eq 'y') {
    Write-Host ""
    Write-Host "After restart, please:" -ForegroundColor Cyan
    Write-Host "1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host "2. Install Docker Desktop" -ForegroundColor Yellow
    Write-Host "3. Run 'docker --version' to verify" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host ""
    Write-Host "📋 Next Steps (Manual):" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Restart your computer" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Download Docker Desktop:" -ForegroundColor Yellow
    Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Install Docker Desktop:" -ForegroundColor Yellow
    Write-Host "   - Run the downloaded installer" -ForegroundColor White
    Write-Host "   - Keep 'Use WSL 2 instead of Hyper-V' checked" -ForegroundColor White
    Write-Host "   - Follow the installation wizard" -ForegroundColor White
    Write-Host ""
    Write-Host "4. After Docker Desktop is installed:" -ForegroundColor Yellow
    Write-Host "   - Open a new PowerShell window" -ForegroundColor White
    Write-Host "   - Navigate to: d:\gemini hackathon\resume_parser_ai" -ForegroundColor White
    Write-Host "   - Run: docker-compose up -d" -ForegroundColor White
    Write-Host ""
    Write-Host "5. Install Python dependencies:" -ForegroundColor Yellow
    Write-Host "   pip install -r requirements.txt" -ForegroundColor White
    Write-Host "   python -m spacy download en_core_web_sm" -ForegroundColor White
    Write-Host ""
    Write-Host "6. Import the dataset:" -ForegroundColor Yellow
    Write-Host "   python scripts/import_kaggle_dataset.py" -ForegroundColor White
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📖 Full guide: docs/DOCKER_SETUP_WINDOWS.md" -ForegroundColor Green
    Write-Host ""
}
