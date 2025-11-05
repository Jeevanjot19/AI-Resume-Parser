# Move Docker Data to D: Drive

## Method 1: WSL Export/Import (Recommended)

Since your Docker is using WSL 2 backend, you need to move the WSL distributions:

### Steps:

1. **Stop Docker Desktop completely:**
   ```powershell
   Get-Process "*docker*" | Stop-Process -Force
   wsl --shutdown
   ```

2. **Check WSL distributions:**
   ```powershell
   wsl --list --verbose
   ```

3. **Export docker-desktop:**
   ```powershell
   wsl --export docker-desktop "D:\DockerData\docker-desktop.tar"
   ```

4. **Unregister the old distribution:**
   ```powershell
   wsl --unregister docker-desktop
   ```

5. **Import to new location:**
   ```powershell
   wsl --import docker-desktop "D:\DockerData\docker-desktop" "D:\DockerData\docker-desktop.tar" --version 2
   ```

6. **Clean up tar file:**
   ```powershell
   Remove-Item "D:\DockerData\docker-desktop.tar"
   ```

7. **Restart Docker Desktop**

---

## Method 2: Using Docker Desktop Settings

1. Open Docker Desktop
2. Go to **Settings** (gear icon)
3. Navigate to **Resources** → **Advanced** or **WSL Integration**
4. Look for disk image location settings
5. Change to `D:\DockerData`
6. Apply & Restart

---

## Method 3: Edit Docker Desktop Configuration

**For Windows with WSL 2:**

Docker Desktop stores WSL distributions in:
- `%LOCALAPPDATA%\Docker\wsl\data\ext4.vhdx` (main virtual disk)
- `C:\ProgramData\DockerDesktop\` (settings)

To move manually:

1. **Stop Docker:**
   ```powershell
   wsl --shutdown
   Get-Process "*docker*" | Stop-Process -Force
   ```

2. **Find the .wslconfig file** (or create it):
   ```powershell
   notepad "$env:USERPROFILE\.wslconfig"
   ```

3. **Add these settings:**
   ```ini
   [wsl2]
   # Move swap file to D:
   swap=8GB
   swapfile=D:\\DockerData\\swap.vhdx
   
   # Limit memory usage
   memory=4GB
   processors=2
   ```

4. **For Docker-specific data, you need to export/import WSL distros:**

---

## Verify New Location

After moving, verify with:

```powershell
# Check WSL distribution location
wsl --list --verbose

# Check Docker info
docker info | Select-String "Docker Root Dir"

# Check disk usage on D:
Get-ChildItem "D:\DockerData" -Recurse | Measure-Object -Property Length -Sum
```

---

## Free Up C: Drive Space After Move

After successful migration:

```powershell
# Clean up old Docker data
docker system prune -af --volumes

# Check C: drive space freed
Get-PSDrive C
```

---

## Troubleshooting

**If Docker won't start after move:**
1. Unregister all Docker WSL distros
2. Restart Docker Desktop (it will recreate them in default location)
3. Try Method 1 again more carefully

**If export is very large:**
- The export will be compressed but can still be several GB
- Make sure D: drive has enough space (check with `Get-PSDrive D`)
- Export time depends on amount of Docker data (images, containers, volumes)

---

## Current Docker Data Size

To check before moving:

```powershell
# Check Docker system space usage
docker system df -v

# Check WSL disk usage
wsl -d docker-desktop -e df -h
```
