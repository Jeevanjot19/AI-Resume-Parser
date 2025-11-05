# WSL Installation - Error Resolution Guide

## Error: DISM Commands Failing

If you're getting errors with the DISM commands, it's because they require **Administrator privileges**.

---

## ✅ EASIEST METHOD - Use wsl --install

### Step 1: Open PowerShell as Administrator

**Option A - Using Start Menu:**
1. Click Start Menu
2. Type `PowerShell`
3. Right-click on "Windows PowerShell"
4. Select **"Run as administrator"**

**Option B - Using Windows Key + X:**
1. Press `Windows Key + X`
2. Select **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**

### Step 2: Run WSL Install Command

In the Administrator PowerShell window, run:

```powershell
wsl --install
```

This single command will:
- ✅ Enable WSL
- ✅ Enable Virtual Machine Platform
- ✅ Download and install WSL kernel
- ✅ Install Ubuntu by default

### Step 3: Restart Your Computer

After the installation completes, **restart is required**.

---

## 🔧 ALTERNATIVE METHOD - If wsl --install doesn't work

If `wsl --install` fails (older Windows 10 versions), use these steps:

### Step 1: Enable Features Manually

**In Administrator PowerShell:**

```powershell
# Enable WSL
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart

# Enable Virtual Machine Platform
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart
```

### Step 2: Download WSL2 Kernel Update

1. Download from: https://aka.ms/wsl2kernel
2. Run the installer: `wsl_update_x64.msi`

### Step 3: Set WSL 2 as Default

```powershell
wsl --set-default-version 2
```

### Step 4: Restart Your Computer

---

## 📋 After Restart - Install Docker Desktop

### 1. Download Docker Desktop

Go to: https://www.docker.com/products/docker-desktop/

Click **"Download for Windows"**

### 2. Install Docker Desktop

1. Run `Docker Desktop Installer.exe`
2. **Important:** Keep "Use WSL 2 instead of Hyper-V" **CHECKED**
3. Follow installation wizard
4. Restart if prompted

### 3. Launch Docker Desktop

1. Open Docker Desktop from Start Menu
2. Accept the service agreement
3. Wait for Docker to start (whale icon in system tray turns steady)

### 4. Verify Installation

Open a **new** PowerShell window (doesn't need to be Admin):

```powershell
docker --version
docker-compose --version
docker ps
```

You should see version numbers and no errors.

---

## 🚀 After Docker is Installed

### Start the Resume Parser Services

```powershell
cd "d:\gemini hackathon\resume_parser_ai"

# Start all services
docker-compose up -d

# Check status (should show all services as "Up")
docker-compose ps

# View logs
docker-compose logs
```

### Install Python Dependencies

```powershell
# Make sure virtual environment is active
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Import the Kaggle Dataset

```powershell
python scripts/import_kaggle_dataset.py
```

This will import all 2,484 resumes into the database with full AI processing.

---

## ⚠️ Common Errors & Solutions

### "Access Denied" or "Insufficient Privileges"

**Solution:** You MUST run PowerShell as Administrator for WSL installation.

### "This application requires the Windows Subsystem for Linux"

**Solution:** Restart your computer after enabling WSL features.

### Docker Desktop won't start

**Solutions:**
1. Ensure WSL 2 is installed: `wsl --status`
2. Check if virtualization is enabled in BIOS
3. Try restarting Docker Desktop
4. Restart your computer

### "docker-compose: command not found"

**Solution:** Docker Desktop includes docker-compose. If missing:
- Close and reopen PowerShell
- Or install manually: `pip install docker-compose`

---

## 📞 Need Help?

If you encounter any specific error, please share:
1. The exact error message
2. Which step you're on
3. Your Windows version: `winver`

---

## Quick Reference Commands

```powershell
# Check WSL status
wsl --status

# Check Docker
docker --version
docker ps

# Start services
cd "d:\gemini hackathon\resume_parser_ai"
docker-compose up -d

# Stop services
docker-compose down

# View service logs
docker-compose logs -f
```
