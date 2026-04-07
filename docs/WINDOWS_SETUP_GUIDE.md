# 🚀 Supply Chain Control Tower - Windows Setup Guide

**Complete beginner-friendly setup for Windows 11 using VS Code and `uv`**

---

## 📋 Prerequisites

- **Windows 11** (or Windows 10 build 19041+)
- **VS Code** installed ([Download](https://code.visualstudio.com))
- **Python 3.9+** installed
- **Git** for Windows installed

### Verify Prerequisites

```powershell
# Open PowerShell and run:
python --version
git --version
```

---

## 🎯 PART 1: Install uv (Python Package Manager)

`uv` is a fast, modern Python environment manager. It replaces `pip` and `virtualenv`.

### Step 1: Install uv via PowerShell

```powershell
# Open PowerShell as Administrator
# Copy & paste this single command:
powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"

# If that fails, try:
pip install uv
```

### Step 2: Verify uv Installation

```powershell
uv --version

# Expected output: uv 0.x.x
```

### Step 3: Add uv to PATH (if needed)

If `uv` command not recognized:
1. Win + R → type `env` → Edit Environment Variables
2. Under "User variables", find `PATH`
3. Click Edit → New → Add: `C:\Program Files\uv`
4. Restart PowerShell

---

## 📂 PART 2: Clone/Create Project Structure

### Option A: Use the existing workspace

```powershell
# Navigate to your project directory
cd "c:\Users\YOUR_USERNAME\OneDrive\Documents\supply chain"

# Verify structure
ls  # Should show: backend, frontend, data, databricks, scripts, docs
```

### Option B: Create from scratch

```powershell
mkdir "C:\supply-chain-control-tower"
cd "C:\supply-chain-control-tower"

# Create folders
mkdir backend, frontend, data\raw, data\processed, scripts, databricks, docs
```

---

## ⚙️ PART 3: Backend Setup (FastAPI)

### Step 1: Open Project in VS Code

```powershell
# In PowerShell, from project root:
code .

# Or open VS Code and File → Open Folder
```

### Step 2: Create Virtual Environment with uv

```powershell
# In VS Code's integrated terminal (Ctrl + `):

# Navigate to backend
cd backend

# Create virtual environment with uv
uv venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate

# Expected: (venv) prompt appears
```

### Step 3: Configure VS Code Python Interpreter

1. Press `Ctrl + Shift + P`
2. Type: "Python: Select Interpreter"
3. Choose: `.\venv\Scripts\python.exe`

### Step 4: Install Backend Dependencies

```powershell
# Make sure you're in backend/ directory and venv is activated

# Copy requirements.txt content to backend folder
# Then install:
uv pip install -r requirements.txt

# This installs:
# - fastapi
# - uvicorn
# - pandas
# - scikit-learn
# - pydantic
# - etc.
```

### Step 5: Create .env File (Optional)

```powershell
# In backend/ folder, create .env:
New-Item .env -ItemType File

# Add content:
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
DATA_PATH=../data/raw
```

### Step 6: Test Backend

```powershell
# Make sure you're in backend/ with venv activated:
python -m uvicorn app.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# 
# Test in browser:
# http://localhost:8000/docs  # Interactive API docs
```

⚠️ If port 8000 is in use:
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID):
taskkill /PID <PID> /F
```

---

## 💻 PART 4: Frontend Setup (React)

### Step 1: Install Node.js

```powershell
# Download from https://nodejs.org/ (LTS recommended)
# Or use Chocolatey:
choco install nodejs

# Verify:
node --version
npm --version
```

### Step 2: Create React App

```powershell
# From project root (not in frontend directory yet)

# Option A: Use Create React App
npx create-react-app frontend

# Option B: Use the existing frontend folder
cd frontend
npm install
```

### Step 3: Install Frontend Dependencies

```powershell
# In frontend/ directory:
cd frontend

# Install packages from package.json:
npm install

# Installing:
# - react 18.2
# - axios
# - chart.js
# - etc.
```

### Step 4: Create .env File

```powershell
# Create frontend/.env file:

REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEBUG=false
```

### Step 5: Start React Development Server

```powershell
# In frontend/ directory:
npm start

# Expected:
# Compiled successfully!
# Local:  http://localhost:3000
# 
# Browser opens automatically
```

---

## 🔄 PART 5: Generate Sample Data

### Step 1: Create Data Generation Script

```powershell
# In project root, navigate to scripts:
cd scripts

# The script already exists: generate_daily_data.py
```

### Step 2: Run Data Generation

```powershell
# From project root with backend venv activated:
cd ..  # Go to project root

# Activate backend venv:
cd backend
.\venv\Scripts\activate
cd ..

# Run data generation:
python scripts/generate_daily_data.py

# Expected output:
# Generating data for 2026-04-06
# ✓ Data generation completed for 2026-04-06
# 
# Created files:
# - data/raw/production_2026_04_06.csv
# - data/raw/shipments_2026_04_06.csv
# - data/raw/inventory_2026_04_06.csv
# - data/raw/quality_2026_04_06.csv
# - data/raw/suppliers_2026_04_06.csv
```

### Step 3: Backfill Multiple Days (Optional)

```powershell
# Generate last 7 days:
python scripts/generate_daily_data.py --backfill 7

# Generate specific date:
python scripts/generate_daily_data.py --date 2026-04-05
```

---

## 🏃 PART 6: Running the Full System

### Terminal Setup (Each in Separate Terminal)

**Terminal 1: Backend**
```powershell
cd backend
.\venv\Scripts\activate
cd ..
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Frontend**
```powershell
cd frontend
npm start
```

**Terminal 3: Data Generation (Scheduled)**
```powershell
# Daily data generation
# Run once a day:
python scripts/generate_daily_data.py

# Or setup Windows Task Scheduler:
# See PART 8
```

### Expected URLs

| Component | URL | Purpose |
|---|---|---|
| **Frontend** | http://localhost:3000 | Dashboard, Chat, Anomalies |
| **Backend** | http://localhost:8000 | API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Redoc** | http://localhost:8000/redoc | Alternative API docs |

---

## 🔧 PART 7: Common Errors & Fixes

### Error 1: `pip install` fails without uv

**Problem:** Using old `pip` without `uv`

**Solution:**
```powershell
# Use uv explicitly:
uv pip install fastapi uvicorn

# Or upgrade uv:
uv tool install uv
```

### Error 2: Port 8000 already in use

**Problem:** Another process using FastAPI port

**Solution:**
```powershell
# Find process:
netstat -ano | findstr :8000

# Kill it (replace 1234 with PID):
taskkill /PID 1234 /F

# Or use different port:
python -m uvicorn app.main:app --port 8001
```

### Error 3: Module not found (e.g., "ModuleNotFoundError: No module named 'fastapi'")

**Problem:** Virtual environment not activated or dependencies not installed

**Solution:**
```powershell
# Verify venv activated:
# Check: (venv) prompt should appear

# If not:
cd backend
.\venv\Scripts\activate

# Reinstall:
uv pip install -r requirements.txt
```

### Error 4: CORS Error in Frontend

**Problem:** Frontend can't connect to backend

**Solution:**
1. Ensure backend is running on http://localhost:8000
2. Check CORS is enabled in `backend/app/main.py`
3. Verify frontend .env has: `REACT_APP_API_URL=http://localhost:8000`
4. Restart both frontend and backend

### Error 5: `npm install` fails

**Problem:** Node.js issues or corrupted cache

**Solution:**
```powershell
# Clear npm cache:
npm cache clean --force

# Delete node_modules and package-lock.json:
rm -r node_modules
rm package-lock.json

# Reinstall:
npm install
```

### Error 6: React app fails to compile

**Problem:** JavaScript syntax errors in frontend

**Solution:**
```powershell
# Check terminal for error details
# Common: Missing semicolons, wrong imports

# Fix and save file
# React will auto-reload

# If stuck, clear cache:
npm start -- --reset-cache
```

---

## 📊 PART 8: Automation (Optional)

### Option A: Windows Task Scheduler (Daily Data Generation)

1. **Create batch file** `C:\generate_data.bat`:
```batch
@echo off
cd C:\Users\YOUR_USERNAME\OneDrive\Documents\supply chain
backend\venv\Scripts\activate
python scripts/generate_daily_data.py
```

2. **Open Task Scheduler**:
   - Win + R → `taskschd.msc`
   - Create Task
   - Name: "Supply Chain Daily Data"
   - Trigger: Daily @ 6:00 AM
   - Action: Run `C:\generate_data.bat`

### Option B: PowerShell Scheduled Task

```powershell
# Create PowerShell script: generate_data.ps1
$env:PYTHONHOME = "C:\Python311"  # Adjust version
$env:Path = "$env:PYTHONHOME;$env:Path"

cd "C:\Users\YOUR_USERNAME\OneDrive\Documents\supply chain"
.\backend\venv\Scripts\activate
python scripts/generate_daily_data.py

# Schedule:
$trigger = New-JobTrigger -Daily -At 6:00AM
Register-ScheduledJob -Name "SupplyChainDaily" -Trigger $trigger -FilePath ".\generate_data.ps1"
```

---

## 🚀 PART 9: Quick Start Commands

Save this as `start.ps1` in project root:

```powershell
# start.ps1 - Launch everything

Write-Host "🚀 Starting Supply Chain Control Tower..."

# Start Backend
Write-Host "`nStarting Backend (Port 8000)..."
Start-Process powershell -ArgumentList {
    cd backend
    .\venv\Scripts\activate
    python -m uvicorn app.main:app --reload
}

# Wait 3 seconds
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend (Port 3000)..."
Start-Process powershell -ArgumentList {
    cd frontend
    npm start
}

Write-Host "`n✓ All services starting..."
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend:  http://localhost:8000"
Write-Host "API Docs: http://localhost:8000/docs"
```

**Run with:**
```powershell
.\start.ps1
```

---

## 📦 PART 10: Git Integration (Push to GitHub)

### Step 1: Initialize Git

```powershell
# In project root:
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

git init
git add .
git commit -m "Initial commit: Supply Chain Control Tower"
```

### Step 2: Push to GitHub

```powershell
# Create repo on GitHub.com first, then:

git remote add origin https://github.com/YOUR_USERNAME/supply-chain-data.git
git branch -M main
git push -u origin main

# For daily data pushes, create .github/workflows/push_data.yml
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Python 3.9+ installed
- [ ] uv installed and working
- [ ] Virtual environment created and activated
- [ ] Backend dependencies installed
- [ ] Backend runs on http://localhost:8000/docs
- [ ] Node.js and npm installed
- [ ] Frontend dependencies installed
- [ ] Frontend runs on http://localhost:3000
- [ ] Sample data generated in `data/raw/`
- [ ] Both services connected (no CORS errors)

---

## 📚 NEXT STEPS

1. **Explore the Dashboard**: http://localhost:3000
2. **Test API Endpoints**: http://localhost:8000/docs
3. **Check Anomalies**: Interact with anomaly detection
4. **Chat with AI**: Ask about supply chain metrics
5. **Generate More Data**: `python scripts/generate_daily_data.py --backfill 30`
6. **Setup Databricks** (optional): Use notebooks in `databricks/`

---

## 🆘 Need Help?

### Check Logs

```powershell
# Backend logs show in terminal
# Frontend errors show in browser console (F12)
# Check VS Code terminal for Python errors
```

### Debug Mode

```powershell
# Backend with verbose logging:
$env:LOG_LEVEL = "DEBUG"
python -m uvicorn app.main:app --reload

# Frontend with debug:
$env:REACT_APP_DEBUG = "true"
npm start
```

### Restart Everything

```powershell
# Kill all processes safely:
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Clear caches:
npm cache clean --force
pip cache purge

# Reinstall:
uv pip install -r backend/requirements.txt
cd frontend && npm install
```

---

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Pandas**: https://pandas.pydata.org/
- **Databricks**: https://www.databricks.com/
- **Ollama (Local LLM)**: https://ollama.ai/

---

## 📝 Notes

- All data is stored locally in `data/raw/` as CSV files
- APIs are fully documented at `/docs` endpoint
- No cloud setup needed for local development
- All services run on local machine
- Modify ports in code if conflicts occur

---

**Last Updated:** April 2026  
**Version:** 1.0.0  
**Status:** Production-Ready

🚀 **You're all set! Start building!**
