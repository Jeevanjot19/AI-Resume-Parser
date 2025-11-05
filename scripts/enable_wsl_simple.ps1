# Simple WSL Installation Script
# This script will guide you through WSL installation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WSL Installation Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  You need Administrator privileges to install WSL" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Press Windows Key + X" -ForegroundColor Yellow
    Write-Host "2. Select 'Windows PowerShell (Admin)' or 'Terminal (Admin)'" -ForegroundColor Yellow
    Write-Host "3. In the Administrator window, run:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   wsl --install" -ForegroundColor Green
    Write-Host ""
    Write-Host "4. Restart your computer when prompted" -ForegroundColor Yellow
    Write-Host "5. After restart, download Docker Desktop from:" -ForegroundColor Yellow
    Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor White
    Write-Host ""
    pause
    exit
}

# Running as Administrator
Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

Write-Host "Installing WSL..." -ForegroundColor Cyan
Write-Host ""

try {
    # Try the simple method first (Windows 10 version 2004+ / Windows 11)
    Write-Host "Attempting: wsl --install" -ForegroundColor Yellow
    wsl --install
    
    Write-Host ""
    Write-Host "✅ WSL installation initiated!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: You MUST restart your computer!" -ForegroundColor Yellow
    Write-Host ""
    
    $restart = Read-Host "Restart now? (Y/N)"
    if ($restart -eq 'Y' -or $restart -eq 'y') {
        Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        Restart-Computer -Force
    } else {
        Write-Host ""
        Write-Host "Please restart manually, then install Docker Desktop" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host ""
    Write-Host "⚠️  Automatic installation failed. Trying manual method..." -ForegroundColor Yellow
    Write-Host ""
    
    # Manual DISM method
    Write-Host "Step 1: Enabling WSL feature..." -ForegroundColor Cyan
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    
    Write-Host "Step 2: Enabling Virtual Machine Platform..." -ForegroundColor Cyan
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    
    Write-Host ""
    Write-Host "✅ Features enabled!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  RESTART REQUIRED!" -ForegroundColor Yellow
    Write-Host ""
    
    $restart = Read-Host "Restart now? (Y/N)"
    if ($restart -eq 'Y' -or $restart -eq 'y') {
        Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        Restart-Computer -Force
    }
}
