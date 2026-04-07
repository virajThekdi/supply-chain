# 🔄 GitHub Automation Setup Guide

**Automate Daily Data Generation & Deployment**

---

## Table of Contents
1. [Overview](#overview)
2. [Quick Setup (5 minutes)](#quick-setup-5-minutes)
3. [GitHub Actions Workflows](#github-actions-workflows)
4. [Environment Configuration](#environment-configuration)
5. [Local Automation](#local-automation)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Overview

### Automation Strategy

```
Option 1: GitHub Actions (Cloud-hosted)
├─ Runs on GitHub's servers
├─ Triggers: Daily at 8 AM UTC
├─ Jobs: Generate data → Commit → Push
├─ Cost: Free (for public repos)
└─ Best for: Teams, CI/CD

Option 2: Local Task Scheduler (Windows)
├─ Runs on your machine
├─ Triggers: Daily or hourly
├─ Jobs: Generate data → Git push
├─ Cost: Your machine must be on
└─ Best for: Development, testing

Option 3: Cloud VPS (AWS EC2, DigitalOcean, etc.)
├─ Runs on dedicated server
├─ Triggers: Cron schedule
├─ Jobs: Full pipeline
├─ Cost: ~$5-20/month
└─ Best for: Production
```

### This Guide Covers
- ✅ **GitHub Actions** (recommended)
- ✅ **Windows Task Scheduler** (backup)
- ✅ **Cloud deployment** (advanced)

---

## Quick Setup (5 minutes)

### Step 1: Create GitHub Repository

```powershell
# Initialize git repo
cd "C:\supply-chain-control-tower"
git init

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/supply-chain.git

# Create .gitignore
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
env/
*.egg-info/
dist/
build/

# Node.js
node_modules/
npm-debug.log
package-lock.json

# Environment
.env
.env.local
*.pem

# IDE
.vscode
.idea
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Data (keep local, fetch from GitHub Actions)
# data/archive/
"@ | Out-File .gitignore -Encoding UTF8

# Initial commit
git add .
git commit -m "Initial commit: Control Tower setup"
git branch -M main
git push -u origin main
```

---

### Step 2: Create GitHub Actions Workflow

Create `.github/workflows/generate-daily-data.yml`:

```yaml
name: "Daily Data Generation"

on:
  schedule:
    # Run at 8 AM UTC daily (3 AM EST, 12 AM PST)
    - cron: '0 8 * * *'
  
  # Allow manual trigger
  workflow_dispatch:

jobs:
  generate-data:
    runs-on: ubuntu-latest
    
    steps:
      # Step 1: Checkout code
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for commits
      
      # Step 2: Setup Python
      - name: Setup Python 3.10
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      # Step 3: Install dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
      
      # Step 4: Generate data
      - name: Generate daily data
        run: |
          python scripts/generate_daily_data.py --date $(date +%Y-%m-%d)
        env:
          TZ: UTC
      
      # Step 5: Commit and push
      - name: Commit and push data
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/raw/*.csv
          
          if git diff --cached --exit-code > /dev/null; then
            echo "No changes to commit"
          else
            COMMIT_MSG="feat: $(date +%Y-%m-%d) daily data generation"
            git commit -m "$COMMIT_MSG"
            git push origin main
          fi
```

---

### Step 3: Create Repository File

Upload to GitHub in `docs/GITHUB_SETUP.md` for reference.

---

## GitHub Actions Workflows

### Workflow 1: Daily Data Generation (Basic)

```yaml
name: Daily Data Generation
on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM UTC daily

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install & Run
        run: |
          pip install -r backend/requirements.txt
          python scripts/generate_daily_data.py
      
      - name: Push Changes
        run: |
          git config user.name "bot"
          git config user.email "bot@github.com"
          git add data/raw/
          git commit -m "Daily data: $(date +%Y-%m-%d)" || true
          git push
```

### Workflow 2: Weekly Aggregation & Analysis

```yaml
name: Weekly Analysis
on:
  schedule:
    - cron: '0 9 * * MON'  # 9 AM Monday

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      
      - name: Analyze Weekly
        run: |
          pip install pandas numpy
          python scripts/weekly_analysis.py
      
      - name: Generate Report
        run: |
          python scripts/generate_report.py
      
      - name: Push Report
        run: |
          git config user.name "analysis-bot"
          git config user.email "bot@github.com"
          git add reports/
          git commit -m "Weekly analysis: $(date +%Y-%m-%d)" || true
          git push
```

### Workflow 3: Databricks Integration

```yaml
name: Sync to Databricks
on:
  push:
    paths:
      - 'data/raw/**'
    branches:
      - main

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Databricks CLI
        run: pip install databricks-cli
      
      - name: Sync Data
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks workspace import_dir data/raw /supply-chain/data/raw
          python scripts/trigger_databricks_job.py
```

### Workflow 4: Continuous Integration

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      
      - name: Install Dependencies
        run: |
          pip install -r backend/requirements.txt pytest
      
      - name: Run Tests
        run: pytest backend/tests/ -v
      
      - name: Lint Code
        run: |
          pip install flake8
          flake8 backend/ --count --select=E9,F63,F7,F82
  
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker Image
        run: docker build -t supply-chain-api:latest .
      
      - name: Push to Registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push supply-chain-api:latest
```

---

## Environment Configuration

### GitHub Secrets Setup

1. Go to: **Settings → Secrets and variables → Actions**

2. Add these secrets:

```
DATABRICKS_HOST
  Value: https://your-instance.cloud.databricks.com

DATABRICKS_TOKEN
  Value: dapi1234567890abcdefg

DOCKER_USERNAME
  Value: your_dockerhub_username

DOCKER_PASSWORD
  Value: your_dockerhub_token

DATABASE_URL
  Value: postgresql://user:pass@host/db

API_KEY
  Value: secret_api_key_for_webhooks
```

### Workflow File Format

```yaml
# .github/workflows/example.yml

name: Workflow Name

on:
  schedule:
    # Cron format: minute hour day month weekday
    # Examples:
    - cron: '0 * * * *'        # Every hour
    - cron: '0 8 * * *'        # Daily at 8 AM
    - cron: '0 8 * * MON'      # Weekly Monday
    - cron: '0 0 1 * *'        # Monthly 1st
  
  push:
    branches:
      - main
      - develop
    paths:
      - 'backend/**'
      - 'data/**'
  
  pull_request:
  
  workflow_dispatch:          # Manual trigger

jobs:
  job_name:
    runs-on: ubuntu-latest
    
    steps:
      - name: Step 1
        run: echo "Hello"
      
      - name: Step 2
        run: python script.py
        env:
          VAR_NAME: ${{ secrets.SECRET_NAME }}
```

---

## Local Automation

### Option 1: Windows Task Scheduler

#### Step 1: Create PowerShell Script

Create `scripts/schedule_daily_data.ps1`:

```powershell
# Supply Chain Daily Data Automation

$ProjectPath = "C:\Users\vthek\OneDrive\Documents\supply chain"
$LogPath = "$ProjectPath\logs"
$DataScript = "$ProjectPath\scripts\generate_daily_data.py"
$BackendPath = "$ProjectPath\backend"

# Create log directory
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath | Out-Null
}

$LogFile = "$LogPath\$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').log"

# Log start
"[$(Get-Date)] Starting daily data generation" | Tee-Object -FilePath $LogFile

try {
    # Change to backend directory (where venv is)
    Set-Location $BackendPath
    
    # Activate virtual environment
    & "$BackendPath\venv\Scripts\Activate.ps1"
    
    # Generate data
    python $DataScript | Tee-Object -FilePath $LogFile -Append
    
    # Git operations
    Set-Location $ProjectPath
    
    git config user.name "Automated Task"
    git config user.email "automation@localhost"
    git add data/raw/*.csv
    
    $CommitMsg = "chore: $(Get-Date -Format 'yyyy-MM-dd') daily data generation"
    git commit -m $CommitMsg | Tee-Object -FilePath $LogFile -Append
    git push origin main | Tee-Object -FilePath $LogFile -Append
    
    "[$(Get-Date)] Completed successfully" | Tee-Object -FilePath $LogFile -Append
}
catch {
    "[$(Get-Date)] ERROR: $_" | Tee-Object -FilePath $LogFile -Append
    exit 1
}
```

#### Step 2: Create Task

```powershell
# Run PowerShell as Administrator

$TaskName = "Supply_Chain_Daily_Data"
$ScriptPath = "C:\supply-chain-control-tower\scripts\schedule_daily_data.ps1"
$Time = "08:00"  # 8 AM

# Create action
$Action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

# Create trigger (daily at 8 AM)
$Trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At $Time

# Create task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description "Automated supply chain daily data generation" `
    -Action $Action `
    -Trigger $Trigger `
    -RunLevel Highest

# Verify
Get-ScheduledTask -TaskName $TaskName
```

#### Step 3: Test Task

```powershell
# Test immediate execution
Start-ScheduledTask -TaskName "Supply_Chain_Daily_Data"

# Check results
Get-ScheduledTaskInfo -TaskName "Supply_Chain_Daily_Data"

# View logs
Get-Content "C:\supply-chain-control-tower\logs\*.log" -Tail 50
```

---

### Option 2: Python Scheduler (Development)

Create `scripts/local_scheduler.py`:

```python
import schedule
import time
import subprocess
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)

PROJECT_ROOT = Path(__file__).parent.parent

def generate_data():
    """Generate daily data"""
    try:
        logging.info("Starting daily data generation...")
        
        # Run data generation script
        result = subprocess.run(
            ["python", "scripts/generate_daily_data.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Data generation failed: {result.stderr}")
            return
        
        logging.info("Data generation completed")
        
        # Git push
        logging.info("Pushing to GitHub...")
        commands = [
            ["git", "config", "user.name", "Local Scheduler"],
            ["git", "config", "user.email", "scheduler@localhost"],
            ["git", "add", "data/raw/*.csv"],
            ["git", "commit", "-m", f"chore: {datetime.now().strftime('%Y-%m-%d')} daily data"],
            ["git", "push", "origin", "main"]
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True)
            if result.returncode != 0:
                logging.warning(f"Git command failed: {' '.join(cmd)}")
        
        logging.info("Push completed")
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")

# Schedule jobs
schedule.every().day.at("08:00").do(generate_data)  # 8 AM daily

# Keep scheduler running
if __name__ == "__main__":
    logging.info("Local scheduler started")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
```

**Run scheduler:**
```powershell
python scripts/local_scheduler.py

# Or run in background with nohup equivalent
start python scripts/local_scheduler.py
```

---

## Monitoring & Troubleshooting

### GitHub Actions Monitoring

#### View Workflow Runs

```
https://github.com/YOUR_USERNAME/supply-chain/actions
```

#### Check Workflow Status

```yaml
# Add status badge to README.md

![Daily Data Generation](https://github.com/YOUR_USERNAME/supply-chain/workflows/Daily%20Data%20Generation/badge.svg)
```

#### Debug Failed Runs

1. Click workflow run
2. Click job
3. Expand failed step
4. Check logs for errors

#### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "python: command not found" | Python not in PATH | Use `python3` or `pip3` |
| "git: permission denied" | No write access | Add SSH key to Actions |
| "No changes detected" | No data generated | Check generate_daily_data.py logic |
| Workflow never runs | Cron syntax incorrect | Verify cron expression |

---

### Local Task Monitoring

#### Check Task Status

```powershell
Get-ScheduledTask -TaskName "Supply_Chain_Daily_Data" | Select *
Get-ScheduledTaskInfo -TaskName "Supply_Chain_Daily_Data"
```

#### View Task Results

```powershell
# PowerShell history
Get-EventLog -LogName System | Where-Object {$_.Source -eq "Task Scheduler"}

# Log files
Get-ChildItem "C:\supply-chain-control-tower\logs\*.log" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 5
```

#### Disable/Re-enable Task

```powershell
# Disable
Disable-ScheduledTask -TaskName "Supply_Chain_Daily_Data"

# Re-enable
Enable-ScheduledTask -TaskName "Supply_Chain_Daily_Data"

# Delete
Unregister-ScheduledTask -TaskName "Supply_Chain_Daily_Data"
```

---

### Troubleshooting Steps

#### 1. Verify Script Works Manually

```powershell
cd "C:\supply-chain-control-tower"
python scripts/generate_daily_data.py
```

#### 2. Check Dependencies

```bash
pip install -r backend/requirements.txt --verbose
```

#### 3. Test Git Operations

```bash
cd "C:\supply-chain-control-tower"
git config --local user.name "Test User"
git config --local user.email "test@example.com"
git status
```

#### 4. Check File Permissions

```powershell
# Ensure write access to data folder
icacls "C:\supply-chain-control-tower\data" /grant:r "$env:USERNAME`:F"
```

#### 5. Enable Detailed Logging

```python
# In generate_daily_data.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
```

---

## Advanced: Cloud Deployment

### AWS Lambda

```python
# lambda_function.py
import subprocess
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Generate data
    subprocess.run(["python", "generate_daily_data.py"])
    
    # Upload to S3
    date_str = datetime.now().strftime('%Y-%m-%d')
    s3.upload_file(
        f"data/raw/production_{date_str}.csv",
        "supply-chain-data",
        f"raw/production_{date_str}.csv"
    )
    
    return {
        "statusCode": 200,
        "body": "Data generated successfully"
    }
```

### DigitalOcean App

```yaml
# app.yaml
name: supply-chain-automation
services:
- name: data-generator
  github:
    repo: YOUR_USERNAME/supply-chain
    branch: main
  build_command: pip install -r backend/requirements.txt
  run_command: python scripts/generate_daily_data.py
  source_dir: ./
```

---

## Summary Checklist

- [ ] GitHub repository created
- [ ] `.github/workflows/` directory created
- [ ] Workflow YAML files added
- [ ] GitHub secrets configured
- [ ] Local script set up (optional)
- [ ] Windows Task scheduled (optional)
- [ ] First run tested manually
- [ ] Logs monitored
- [ ] Git credentials configured
- [ ] Monitoring dashboard set up

---

**Version**: 1.0.0  
**Last Updated**: April 7, 2026  
**Status**: ✅ Ready for Implementation
