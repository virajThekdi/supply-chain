# 🔗 GITHUB ↔ DATABRICKS DATA PIPELINE SETUP

**Upload CSV files to GitHub + Configure Databricks Bronze Layer to Read From It**

---

## 📍 DATA FILE LOCATION

```
C:\Users\vthek\OneDrive\Documents\supply chain\data\raw\

Files (10 total):
  ├── production_2026_04_06.csv      (12 records)
  ├── production_2026_04_07.csv      (12 records)
  ├── shipments_2026_04_06.csv       (10 records)
  ├── shipments_2026_04_07.csv       (10 records)
  ├── quality_2026_04_06.csv         (12 records)
  ├── quality_2026_04_07.csv         (12 records)
  ├── inventory_2026_04_06.csv       (18 records)
  ├── inventory_2026_04_07.csv       (18 records)
  ├── suppliers_2026_04_06.csv       (11 records)
  └── suppliers_2026_04_07.csv       (11 records)
```

---

## 🚀 GITHUB SETUP (10 MINUTES)

### Step 1: Create GitHub Repository

```powershell
# Go to github.com and create new repo named "supply-chain"
# (or use existing repo)

# Copy SSH or HTTPS URL of your repo
# Example: https://github.com/YOUR_USERNAME/supply-chain.git
```

### Step 2: Initialize Git in Your Project

```powershell
cd "C:\Users\vthek\OneDrive\Documents\supply chain"

# Initialize git
git init

# Configure user
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Supply chain control tower"

# Add remote repository (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/supply-chain.git

# Push to GitHub (set main branch)
git branch -M main
git push -u origin main
```

**If you get authentication errors:**
```powershell
# Option 1: Use Personal Access Token (PAT)
git config --global credential.helper wincred

# Option 2: Setup SSH key (recommended)
# Generate SSH key (if you don't have one):
ssh-keygen -t ed25519 -C "your@email.com"

# Then add to GitHub:
# Settings → SSH and GPG Keys → New SSH Key
# Paste content of ~/.ssh/id_ed25519.pub
```

---

## ✅ VERIFY FILES ON GITHUB

After pushing, visit your GitHub repo:
```
https://github.com/YOUR_USERNAME/supply-chain/tree/main/data/raw
```

You should see all 10 CSV files listed.

---

## 🔗 GITHUB RAW URLS (For Databricks)

Once files are on GitHub, Databricks accesses them via **raw content URLs**:

```
Pattern:
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/FILENAME

Examples:
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/production_2026_04_07.csv
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/shipments_2026_04_07.csv
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/quality_2026_04_07.csv
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/inventory_2026_04_07.csv
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/suppliers_2026_04_07.csv
```

---

## 🌳 FILE STRUCTURE AFTER PUSH

Your GitHub repo will look like:
```
supply-chain/
├── .git
├── .gitignore
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── venv/
├── frontend/
├── scripts/
├── databricks/
│   └── notebooks/
├── data/
│   └── raw/
│       ├── production_2026_04_06.csv    ← GitHub will host these
│       ├── production_2026_04_07.csv
│       ├── shipments_*.csv
│       ├── quality_*.csv
│       ├── inventory_*.csv
│       └── suppliers_*.csv
├── docs/
├── README.md
└── (other files)
```

---

## 📝 CONFIGURE BRONZE NOTEBOOK FOR GITHUB

Update your Databricks notebook to read from GitHub URLs:

```python
# Databricks notebook source
# BRONZE LAYER: Ingest CSV files from GitHub

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from datetime import datetime, timedelta

# GitHub base URL (REPLACE WITH YOUR USERNAME)
GITHUB_USERNAME = "YOUR_USERNAME"
GITHUB_REPO = "supply-chain"
GITHUB_BRANCH = "main"
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/data/raw"

# Date to fetch
today = datetime.now().strftime("%Y_%m_%d")

# PRODUCTION SCHEMA
production_schema = StructType([
    StructField("production_id", StringType()),
    StructField("date", StringType()),
    StructField("plant_id", StringType()),
    StructField("product_id", StringType()),
    StructField("quantity_produced", IntegerType()),
    StructField("machine_id", StringType()),
    StructField("temperature", DoubleType()),
    StructField("energy_consumption", DoubleType()),
    StructField("downtime_minutes", IntegerType())
])

# SHIPMENT SCHEMA
shipment_schema = StructType([
    StructField("shipment_id", StringType()),
    StructField("order_id", StringType()),
    StructField("product_id", StringType()),
    StructField("quantity", IntegerType()),
    StructField("origin", StringType()),
    StructField("destination", StringType()),
    StructField("supplier_id", StringType()),
    StructField("dispatch_date", StringType()),
    StructField("expected_delivery_date", StringType()),
    StructField("actual_delivery_date", StringType()),
    StructField("delay_days", IntegerType()),
    StructField("status", StringType())
])

# QUALITY SCHEMA
quality_schema = StructType([
    StructField("quality_id", StringType()),
    StructField("date", StringType()),
    StructField("product_id", StringType()),
    StructField("batch_id", StringType()),
    StructField("defects_count", IntegerType()),
    StructField("defect_type", StringType()),
    StructField("defect_rate", DoubleType())
])

# INVENTORY SCHEMA
inventory_schema = StructType([
    StructField("inventory_id", StringType()),
    StructField("date", StringType()),
    StructField("product_id", StringType()),
    StructField("warehouse_id", StringType()),
    StructField("opening_stock", IntegerType()),
    StructField("produced", IntegerType()),
    StructField("shipped", IntegerType()),
    StructField("closing_stock", IntegerType())
])

# SUPPLIER SCHEMA
supplier_schema = StructType([
    StructField("supplier_id", StringType()),
    StructField("supplier_name", StringType()),
    StructField("material_type", StringType()),
    StructField("delivery_date", StringType()),
    StructField("expected_date", StringType()),
    StructField("delay_days", IntegerType()),
    StructField("quality_rating", IntegerType())
])

# ============================================================
# READ FROM GITHUB
# ============================================================

# Production
prod_url = f"{GITHUB_BASE_URL}/production_{today}.csv"
print(f"Reading production from: {prod_url}")
prod_df = spark.read.schema(production_schema).option("header", "true").csv(prod_url)

# Shipments
ship_url = f"{GITHUB_BASE_URL}/shipments_{today}.csv"
print(f"Reading shipments from: {ship_url}")
ship_df = spark.read.schema(shipment_schema).option("header", "true").csv(ship_url)

# Quality
qual_url = f"{GITHUB_BASE_URL}/quality_{today}.csv"
print(f"Reading quality from: {qual_url}")
qual_df = spark.read.schema(quality_schema).option("header", "true").csv(qual_url)

# Inventory
inv_url = f"{GITHUB_BASE_URL}/inventory_{today}.csv"
print(f"Reading inventory from: {inv_url}")
inv_df = spark.read.schema(inventory_schema).option("header", "true").csv(inv_url)

# Suppliers
sup_url = f"{GITHUB_BASE_URL}/suppliers_{today}.csv"
print(f"Reading suppliers from: {sup_url}")
sup_df = spark.read.schema(supplier_schema).option("header", "true").csv(sup_url)

# ============================================================
# WRITE TO DELTA (BRONZE LAYER)
# ============================================================

# Production → Delta
prod_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .partitionBy("date") \
    .save("/mnt/data/bronze/production")

# Shipments → Delta
ship_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .partitionBy("date") \
    .save("/mnt/data/bronze/shipments")

# Quality → Delta
qual_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .partitionBy("date") \
    .save("/mnt/data/bronze/quality")

# Inventory → Delta
inv_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .partitionBy("date") \
    .save("/mnt/data/bronze/inventory")

# Suppliers → Delta
sup_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .partitionBy("date") \
    .save("/mnt/data/bronze/suppliers")

# ============================================================
# VERIFY
# ============================================================

display(prod_df.limit(5))
display(ship_df.limit(5))
print(f"✓ Bronze ingestion complete")
print(f"  Production: {prod_df.count()} records")
print(f"  Shipments: {ship_df.count()} records")
print(f"  Quality: {qual_df.count()} records")
print(f"  Inventory: {inv_df.count()} records")
print(f"  Suppliers: {sup_df.count()} records")
```

---

## 🔄 AUTOMATE GITHUB PUSH (Daily)

### Option 1: GitHub Action (Automated)

Create `.github/workflows/sync-data.yml`:

```yaml
name: "Daily Data Sync to GitHub"

on:
  schedule:
    - cron: '5 8 * * *'  # 8:05 AM UTC (after data generation)
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Generate data
        run: |
          pip install pandas numpy python-dotenv
          python scripts/generate_daily_data.py
      
      - name: Commit and push
        run: |
          git config user.name "Data Bot"
          git config user.email "bot@github.com"
          git add data/raw/*.csv
          
          if ! git diff --cached --exit-code > /dev/null; then
            git commit -m "Data: $(date +%Y-%m-%d) daily generation"
            git push origin main
          fi
```

### Option 2: Manual Push (Every morning)

```powershell
cd "C:\Users\vthek\OneDrive\Documents\supply chain"

# Generate today's data
python scripts/generate_daily_data.py

# Add and push
git add data/raw/production_*.csv data/raw/shipments_*.csv data/raw/quality_*.csv data/raw/inventory_*.csv data/raw/suppliers_*.csv
git commit -m "Data: $(Get-Date -Format 'yyyy-MM-dd') daily generation"
git push origin main
```

---

## 🔌 DATABRICKS WORKFLOW

```
1. YOUR MACHINE
   └─→ Run: python scripts/generate_daily_data.py
   └─→ Creates: data/raw/production_*.csv, etc.

2. GITHUB
   └─→ Push CSV files
   └─→ URL: https://raw.githubusercontent.com/...

3. DATABRICKS (Daily 8:00 AM UTC)
   
   Job: Bronze Ingestion
   ├─ Read from GitHub URLs
   ├─ Parse CSV schemas
   ├─ Write to Delta Lake (/mnt/data/bronze/*)
   
   Job: Silver Transformation
   ├─ Read from Bronze
   ├─ Clean & validate
   ├─ Write to Delta (/mnt/data/silver/*)
   
   Job: Gold Aggregation
   ├─ Read from Silver
   ├─ Create KPI tables
   ├─ Write to Delta (/mnt/data/gold/*)

4. DASHBOARDS
   └─→ Query Gold tables
   └─→ Real-time visuals
```

---

## 📋 STEP-BY-STEP: PUSH TO GITHUB NOW

### Current Step (You are here)

```powershell
# 1. Open PowerShell in project folder
cd "C:\Users\vthek\OneDrive\Documents\supply chain"

# 2. Initialize git (if not already done)
git init

# 3. Configure git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 4. Add all files
git add .

# 5. Create commit
git commit -m "Initial commit: Supply chain control tower with data"

# 6. Add GitHub remote (replace USERNAME/REPO)
git remote add origin https://github.com/YOUR_USERNAME/your-repo-name.git

# 7. Push to GitHub
git branch -M main
git push -u origin main

# 8. Verify in browser
# Visit: https://github.com/YOUR_USERNAME/your-repo-name/tree/main/data/raw
```

### Next Day (For Daily Updates)

```powershell
cd "C:\Users\vthek\OneDrive\Documents\supply chain"

# Generate new data
python scripts/generate_daily_data.py

# Push to GitHub
git add data/raw/
git commit -m "Data: $(Get-Date -Format 'yyyy-MM-dd')"
git push origin main
```

---

## 🎯 WHAT DATABRICKS READS FROM GITHUB

**Pattern:**
```
https://raw.githubusercontent.com/{USERNAME}/{REPO}/{BRANCH}/data/raw/{FILENAME}
```

**Real Example:**
```
https://raw.githubusercontent.com/myname/supply-chain/main/data/raw/production_2026_04_07.csv
https://raw.githubusercontent.com/myname/supply-chain/main/data/raw/shipments_2026_04_07.csv
https://raw.githubusercontent.com/myname/supply-chain/main/data/raw/quality_2026_04_07.csv
https://raw.githubusercontent.com/myname/supply-chain/main/data/raw/inventory_2026_04_07.csv
https://raw.githubusercontent.com/myname/supply-chain/main/data/raw/suppliers_2026_04_07.csv
```

**Databricks reads these like a file:**
```python
df = spark.read.csv("https://raw.githubusercontent.com/.../production_2026_04_07.csv", header=True)
```

---

## ✅ CHECKLIST

```
SETUP (One-time):
  ☐ Create GitHub repository
  ☐ Initialize git locally
  ☐ Configure git user name/email
  ☐ Add remote origin
  ☐ Push all files to GitHub
  ☐ Verify files appear on GitHub.com
  
DATABRICKS CONFIGURATION:
  ☐ Update Bronze notebook with your GitHub USERNAME
  ☐ Copy modified Bronze notebook from this guide
  ☐ Paste into Databricks workspace
  ☐ Test notebook (should read from GitHub URLs)
  ☐ Verify Delta tables created in /mnt/data/bronze/
  
DAILY ROUTINE:
  ☐ Python script auto-generates data daily
  ☐ GitHub Actions auto-pushes (if using GitHub Actions)
  ☐ OR manually run: git add . && git commit -m "..." && git push
  ☐ Databricks job runs at 8:00 AM UTC
  ☐ Bronze → Silver → Gold pipeline completes
```

---

## 🆘 TROUBLESHOOTING

### "fatal: not a git repository"
```powershell
# Fix: Initialize git first
git init
```

### "authentication failed"
```powershell
# Generate GitHub Personal Access Token:
# Settings → Developer settings → Personal access tokens

# Then use as password when pushing
# Or setup SSH key for passwordless auth
```

### "Could not resolve host: github.com"
```powershell
# Check internet connection
ping github.com

# If behind corporate proxy, configure git:
git config --global http.proxy [proxy-url]
```

### Databricks "File not found" error
```python
# Check:
# 1. GitHub username is correct in URL
# 2. File exists on GitHub (/main/data/raw/)
# 3. URL format is correct (raw.githubusercontent.com, not github.com)
# 4. Header row is included in CSV
```

### "Rate limit exceeded"
```
GitHub limits unauthenticated requests to 60/hour
Solution: Less frequent reads or use GitHub token in URL:
https://raw.githubusercontent.com/.../file.csv?token=YOUR_TOKEN
```

---

## 📚 FINAL FLOW

```
Local Machine (Daily)
  └─ python scripts/generate_daily_data.py
  └─ Creates: data/raw/production_YYYY_MM_DD.csv (+ 4 more)

    ↓ (Manual or Automated)

GitHub Repository
  └─ Files stored at:
  └─ https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/

    ↓ (Daily 8:00 AM UTC - Databricks Job)

Databricks Bronze Notebook
  └─ Reads from GitHub URLs
  └─ Parses CSV files
  └─ Writes Delta tables: /mnt/data/bronze/*

    ↓ (Daily 8:10 AM UTC)

Databricks Silver Notebook
  └─ Cleans & validates
  └─ Enriches data
  └─ Writes Delta tables: /mnt/data/silver/*

    ↓ (Daily 8:20 AM UTC)

Databricks Gold Notebook
  └─ Aggregates KPIs
  └─ Creates business tables
  └─ Writes Delta tables: /mnt/data/gold/*

    ↓

Real-Time Dashboards
  └─ Query /mnt/data/gold/*
  └─ Display KPI metrics
  └─ Alert on anomalies
```

---

## 🚀 READY?

**To start right now:**

1. **Edit Bronze notebook** with your GitHub username
2. **Push your project to GitHub** (10 minutes)
3. **Paste Bronze notebook code** into Databricks
4. **Test it** - should read from GitHub URLs
5. **Setup daily job** - automates rest

---

**Next**: DATABRICKS_SETUP.md for complete Databricks workflow

**Key URL**, format you'll use:
```
https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw/
```

Replace `YOUR_USERNAME` with your actual GitHub username!
