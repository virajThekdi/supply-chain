# 🚀 DATABRICKS SETUP GUIDE

**Complete Guide: Getting Your Data & Pipeline into Databricks**

---

## 📊 Current Status

Your system is **UP & RUNNING**:
- ✅ **FastAPI Backend**: http://localhost:8000
- ✅ **Data Generation**: Working (5 CSV files created daily)
- ✅ **Sample Data**: 10 CSV files in `/data/raw/`
- ✅ **API Documentation**: http://localhost:8000/docs
- ✅ **API Health**: http://localhost:8000/health

---

## 🎯 What to Put on Data Bricks (3-Step Process)

### Step 1: Upload Daily Data Files to Databricks

Your **CSV files** (from `/data/raw/`) need to go to Databricks:

```
📂 CSV Files → Databricks File System → Convert to Delta Tables
   ├── production_YYYY_MM_DD.csv
   ├── shipments_YYYY_MM_DD.csv
   ├── quality_YYYY_MM_DD.csv
   ├── inventory_YYYY_MM_DD.csv
   └── suppliers_YYYY_MM_DD.csv
```

**In Databricks:**
```
/Volumes/
├── control-tower/
│   └── raw-data/
│       ├── production/
│       ├── shipments/
│       ├── quality/
│       ├── inventory/
│       └── suppliers/
```

### Step 2: Upload & Run Databricks Notebooks

Your **3 notebooks** handle the ETL pipeline:

```
📂 Notebooks → Databricks Workspace → Run Pipeline
   ├── 01_bronze_ingestion.py       (Load CSVs → Delta)
   ├── 02_silver_transformation.py  (Clean & Validate)
   └── 03_gold_aggregation.py       (KPI Tables)
```

### Step 3: Schedule Daily Jobs

Set up **Databricks Jobs** to run automatically:

```
Daily (8:00 AM UTC)
├── Job 1: Bronze Ingestion (read CSVs from File System)
├── Job 2: Silver Transformation (clean data)
└── Job 3: Gold Aggregation (create KPIs)
```

---

## 🛠️ Step-by-Step Databricks Setup

### Part 1: Create Databricks Workspace

#### Option A: Azure Databricks
```
1. Go to Azure Portal
2. Create "Azure Databricks Service"
3. Select "Standard" tier
4. Region: East US 2 (or closest to you)
5. Create workspace
```

#### Option B: AWS Databricks
```
1. Go to databricks.com/product/aws
2. Click "Start Free Trial"
3. Login with email
4. Create workspace
5. Select region: us-east-1
```

#### Option C: GCP Databricks
```
1. Go to databricks.com/product/gcp
2. Create account
3. Deploy workspace
```

**Cost**: Free tier available (~$0.30/compute per hour, covers POC)

---

### Part 2: Get Access Credentials

#### Generate Personal Access Token (PAT)

```
1. In Databricks workspace:
   Settings → Admin Console → PAT
   
2. Click "Generate New Token"
   - Lifetime: 180 days
   - Comment: "Control Tower API"
   
3. Copy token (save securely):
   dapi1234567890abcdefghijklmnopqrst
```

**Store this securely in `.env`:**
```
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi1234567890abcdefghijklmnopqrst
```

---

### Part 3: Upload Data Files

#### Method 1: Databricks UI Upload

```
1. In workspace:
   Catalog → Create Volumes → "control-tower"
   
2. Create folders:
   /Volumes/control-tower/raw-data/production/
   /Volumes/control-tower/raw-data/shipments/
   /Volumes/control-tower/raw-data/quality/
   /Volumes/control-tower/raw-data/inventory/
   /Volumes/control-tower/raw-data/suppliers/
   
3. Upload your CSV files (or batch upload)
```

#### Method 2: Python API (Automated)

```python
from databricks.sdk import WorkspaceClient
import os

client = WorkspaceClient(
    host=os.getenv("DATABRICKS_HOST"),
    token=os.getenv("DATABRICKS_TOKEN")
)

# Upload files
for csv_file in Path("data/raw").glob("*.csv"):
    with open(csv_file, "rb") as f:
        client.dbfs.put(
            path=f"/Volumes/control-tower/raw-data/{csv_file.name}",
            contents=f,
            overwrite=True
        )
```

#### Method 3: GitHub Integration (Recommended for Daily Automation)

```
1. In Databricks:
   Settings → Secrets → Create Secret Scope
   Name: github
   
2. Create secret:
   Key: token
   Value: (your GitHub PAT)
   
3. In notebook, mount GitHub:
   import requests
   github_url = "https://raw.githubusercontent.com/YOUR_USERNAME/supply-chain/main/data/raw"
   df = spark.read.csv(f"{github_url}/production_2026_04_07.csv")
```

---

### Part 4: Create Bronze Notebook

**Create new notebook** in Databricks and paste:

```python
# Databricks notebook source
# BRONZE LAYER: Ingest raw CSV files into Delta format

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType

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

# Read production CSV from volumes
prod_df = spark.read.schema(production_schema).csv(
    "/Volumes/control-tower/raw-data/production/"
)

# Write to Delta (Bronze)
prod_df.write \
    .format("delta") \
    .mode("append") \
    .save("/mnt/data/bronze/production")

display(prod_df.limit(5))
```

---

### Part 5: Create Silver Notebook

**Create transformation notebook** with data cleaning:

```python
# Databricks notebook source
# SILVER LAYER: Clean, validate, and enrich data

from pyspark.sql.functions import col, when, isnan, mean, stddev

# Read Bronze data
prod_df = spark.read.format("delta").load("/mnt/data/bronze/production")

# Data Quality: Remove nulls
clean_df = prod_df.filter(
    (col("temperature").isNotNull()) &
    (col("energy_consumption").isNotNull()) &
    (col("downtime_minutes").isNotNull())
)

# Validation: Check ranges
validated_df = clean_df.filter(
    (col("temperature") > 0) &
    (col("temperature") < 2000) &
    (col("energy_consumption") >= 0) &
    (col("downtime_minutes") >= 0)
)

# Add quality flags
enriched_df = validated_df.withColumn(
    "data_quality_score",
    when(
        (col("temperature") > 840) & (col("temperature") < 870),
        1.0
    ).otherwise(0.8)
)

# Write to Silver
enriched_df.write \
    .format("delta") \
    .mode("overwrite") \
    .save("/mnt/data/silver/production")

display(enriched_df)
```

---

### Part 6: Create Gold Notebook (KPIs)

**Create KPI aggregation notebook:**

```python
# Databricks notebook source
# GOLD LAYER: Business KPI tables

from pyspark.sql.functions import col, sum, avg, count, round, date_format

# Read Silver data
prod_df = spark.read.format("delta").load("/mnt/data/silver/production")

# KPI 1: Production KPIs by Plant
production_kpi = prod_df.groupBy("plant_id", "date").agg(
    sum("quantity_produced").alias("total_output"),
    round(avg("temperature"), 2).alias("avg_temperature"),
    round(avg("energy_consumption"), 2).alias("avg_energy"),
    round(avg("downtime_minutes"), 2).alias("avg_downtime"),
    count("*").alias("records")
)

# Write to Gold
production_kpi.write \
    .format("delta") \
    .mode("overwrite") \
    .save("/mnt/data/gold/production_kpi")

display(production_kpi.limit(10))
```

---

## 📅 Schedule Daily Pipeline

### Create Databricks Job

```
1. In workspace:
   Workflows → Create Job
   
2. Configure:
   Name: "Daily Control Tower Pipeline"
   Cluster: Create new (2-4 workers, auto-scaling)
   
3. Add Tasks (in order):
   Task 1: Bronze Notebook
   Task 2: Silver Notebook (depends on Task 1)
   Task 3: Gold Notebook (depends on Task 2)
   
4. Schedule:
   Daily at 8:00 AM UTC
   Timezone: UTC
   
5. Alerts:
   Email on failure
```

### Job Configuration (JSON)

```json
{
  "name": "Daily Control Tower Pipeline",
  "tasks": [
    {
      "task_key": "bronze",
      "notebook_task": {
        "notebook_path": "/Users/me@company.com/01_bronze_ingestion"
      },
      "existing_cluster_id": "cluster-001"
    },
    {
      "task_key": "silver",
      "depends_on": [{"task_key": "bronze"}],
      "notebook_task": {
        "notebook_path": "/Users/me@company.com/02_silver_transformation"
      },
      "existing_cluster_id": "cluster-001"
    },
    {
      "task_key": "gold",
      "depends_on": [{"task_key": "silver"}],
      "notebook_task": {
        "notebook_path": "/Users/me@company.com/03_gold_aggregation"
      },
      "existing_cluster_id": "cluster-001"
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 8 * * ?",
    "timezone_id": "UTC"
  }
}
```

---

## 🔗 Integration: FastAPI ↔️ Databricks

### Query Databricks from API

**Update backend** to read from Databricks Gold tables:

```python
from databricks import sql
import os

def get_kpis_from_databricks():
    with sql.connect(
        server_hostname=os.getenv("DATABRICKS_HOST"),
        http_path="/sql/1.0/warehouses/warehouse-id",
        auth_type="pat",
        personal_access_token=os.getenv("DATABRICKS_TOKEN")
    ) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gold.production_kpi LIMIT 100")
        return cursor.fetchall()
```

---

## 🎯 What to Put on Databricks: Checklist

### ✅ Files to Upload

```
☐ Production CSV files (production_YYYY_MM_DD.csv)
☐ Shipment CSV files (shipments_YYYY_MM_DD.csv)
☐ Quality CSV files (quality_YYYY_MM_DD.csv)
☐ Inventory CSV files (inventory_YYYY_MM_DD.csv)
☐ Supplier CSV files (suppliers_YYYY_MM_DD.csv)
```

### ✅ Notebooks to Create

```
☐ 01_bronze_ingestion.py      (ingest raw files)
☐ 02_silver_transformation.py (clean & validate)
☐ 03_gold_aggregation.py      (KPI tables)
```

### ✅ Infrastructure

```
☐ Create workspace (Azure/AWS/GCP)
☐ Generate PAT token
☐ Create volumes/folders
☐ Create cluster (auto-scaling, 2-4 workers)
☐ Create SQL warehouse
☐ Create jobs & schedules
```

### ✅ Access Control

```
☐ Store credentials in .env
☐ Create service principal (for prod)
☐ Setup audit logging
☐ Enable encryption at rest
```

---

## 💰 Databricks Cost Estimate

| Component | Daily | Monthly | Annual |
|-----------|-------|---------|--------|
| Compute (2 workers, 2 hrs) | $0.60 | $18 | $220 |
| SQL Warehouse (4 hrs) | $2.50 | $75 | $900 |
| Storage (10 GB) | $0.05 | $1.50 | $18 |
| **Total** | **$3.15** | **$94.50** | **$1,138** |

**Free tier available**: Covers first 10k model points (months of testing)

---

## 🚀 Quick Start (30 minutes)

```bash
# 1. Create Databricks account
# 2. Generate PAT token
# 3. Add to .env
DATABRICKS_HOST=https://xxx.cloud.databricks.com
DATABRICKS_TOKEN=dapi...

# 4. Upload your CSV files
# 5. Create 3 notebooks (copy from guide above)
# 6. Test each notebook individually
# 7. Create job with dependencies
# 8. Schedule daily at 8 AM UTC

# 9. Verify output
spark.sql("SELECT * FROM gold.production_kpi LIMIT 5").display()
```

---

## 📞 Troubleshooting

### "Authentication failed"
- Check PAT token is valid and not expired
- Verify host URL format: `https://xxx.cloud.databricks.com`

### "File not found"
- Verify CSV files uploaded to correct path
- Check volume permissions
- Try uploading via UI first

### "SQL parsing error" in notebooks
- Ensure CSV has headers: `header=true`
- Verify schema matches CSV columns
- Check date formats match expected format

### Jobs keep failing
- Check cluster has enough memory (4GB minimum)
- Verify dependencies between tasks
- Check timeout settings (5 min default)
- Review job run logs for details

---

## 📚 Next Steps

1. **This Week**: Setup Databricks workspace + upload data
2. **Next Week**: Create & test 3 notebooks
3. **Week 3**: Setup daily job schedule
4. **Week 4**: Integrate with FastAPI for queries

---

## 🔗 Useful Links

- **Databricks Docs**: https://docs.databricks.com/
- **Delta Format**: https://docs.databricks.com/delta/
- **Databricks SQL**: https://docs.databricks.com/sql/
- **API Reference**: https://docs.databricks.com/api/workspace/
- **Pricing**: https://databricks.com/product/pricing

---

**Status**: ✅ Ready to Deploy  
**Created**: 2026-04-07  
**Environment**: Windows 11 + Python 3.13
