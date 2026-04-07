# Databricks notebook source
"""
BRONZE LAYER - Data Ingestion from GitHub
==========================================

Purpose:
  - Load raw CSV data from GitHub
  - Store in Delta format for versioning
  - Create Bronze layer tables

How it works:
  1. Read CSV files from GitHub URLs
  2. Parse schemas
  3. Write to Delta tables in /mnt/data/bronze/
  4. Partition by date for performance
"""

# COMMAND ----------

# ============================================================
# CONFIGURATION - UPDATE WITH YOUR GITHUB USERNAME!
# ============================================================

GITHUB_USERNAME = "YOUR_GITHUB_USERNAME"  # ← CHANGE THIS
GITHUB_REPO = "supply-chain"
GITHUB_BRANCH = "main"
GITHUB_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/data/raw"

# Get today's date for filename
from datetime import datetime
today = datetime.now().strftime("%Y_%m_%d")
yesterday = (datetime.now().replace(day=1) - __import__('datetime').timedelta(days=1)).strftime("%Y_%m_%d")

print(f"GitHub Base URL: {GITHUB_BASE_URL}")
print(f"Loading data for: {today}")

# COMMAND ----------

# ============================================================
# DEFINE SCHEMAS
# ============================================================

from pyspark.sql.types import *

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

quality_schema = StructType([
    StructField("quality_id", StringType()),
    StructField("date", StringType()),
    StructField("product_id", StringType()),
    StructField("batch_id", StringType()),
    StructField("defects_count", IntegerType()),
    StructField("defect_type", StringType()),
    StructField("defect_rate", DoubleType())
])

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

supplier_schema = StructType([
    StructField("supplier_id", StringType()),
    StructField("supplier_name", StringType()),
    StructField("material_type", StringType()),
    StructField("delivery_date", StringType()),
    StructField("expected_date", StringType()),
    StructField("delay_days", IntegerType()),
    StructField("quality_rating", IntegerType())
])

# COMMAND ----------

# ============================================================
# LOAD DATA FROM GITHUB
# ============================================================

# PRODUCTION DATA
print(f"📥 Loading production data for {today}...")
try:
    prod_url = f"{GITHUB_BASE_URL}/production_{today}.csv"
    print(f"   URL: {prod_url}")
    
    production_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .schema(production_schema) \
        .csv(prod_url)
    
    # Write to Delta
    production_df.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy("date") \
        .save("/mnt/data/bronze/production")
    
    print(f"✓ Loaded {production_df.count()} production records")
    display(production_df.limit(3))
except Exception as e:
    print(f"✗ Error: {str(e)}")
    # Try yesterday's data as fallback
    try:
        prod_url_yesterday = f"{GITHUB_BASE_URL}/production_{yesterday}.csv"
        print(f"   Trying yesterday: {prod_url_yesterday}")
        production_df = spark.read \
            .option("header", "true") \
            .schema(production_schema) \
            .csv(prod_url_yesterday)
        production_df.write.format("delta").mode("overwrite").save("/mnt/data/bronze/production")
        print(f"✓ Loaded {production_df.count()} records from yesterday")
    except Exception as e2:
        print(f"✗ Failed: {str(e2)}")

# COMMAND ----------

# SHIPMENT DATA
print(f"📥 Loading shipment data for {today}...")
try:
    ship_url = f"{GITHUB_BASE_URL}/shipments_{today}.csv"
    print(f"   URL: {ship_url}")
    
    shipment_df = spark.read \
        .option("header", "true") \
        .schema(shipment_schema) \
        .csv(ship_url)
    
    shipment_df.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy("date") \
        .save("/mnt/data/bronze/shipments")
    
    print(f"✓ Loaded {shipment_df.count()} shipment records")
    display(shipment_df.limit(3))
except Exception as e:
    print(f"✗ Error: {str(e)}")

# COMMAND ----------

# QUALITY DATA
print(f"📥 Loading quality data for {today}...")
try:
    qual_url = f"{GITHUB_BASE_URL}/quality_{today}.csv"
    print(f"   URL: {qual_url}")
    
    quality_df = spark.read \
        .option("header", "true") \
        .schema(quality_schema) \
        .csv(qual_url)
    
    quality_df.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy("date") \
        .save("/mnt/data/bronze/quality")
    
    print(f"✓ Loaded {quality_df.count()} quality records")
    display(quality_df.limit(3))
except Exception as e:
    print(f"✗ Error: {str(e)}")

# COMMAND ----------

# INVENTORY DATA
print(f"📥 Loading inventory data for {today}...")
try:
    inv_url = f"{GITHUB_BASE_URL}/inventory_{today}.csv"
    print(f"   URL: {inv_url}")
    
    inventory_df = spark.read \
        .option("header", "true") \
        .schema(inventory_schema) \
        .csv(inv_url)
    
    inventory_df.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy("date") \
        .save("/mnt/data/bronze/inventory")
    
    print(f"✓ Loaded {inventory_df.count()} inventory records")
    display(inventory_df.limit(3))
except Exception as e:
    print(f"✗ Error: {str(e)}")

# COMMAND ----------

# SUPPLIER DATA
print(f"📥 Loading supplier data for {today}...")
try:
    sup_url = f"{GITHUB_BASE_URL}/suppliers_{today}.csv"
    print(f"   URL: {sup_url}")
    
    supplier_df = spark.read \
        .option("header", "true") \
        .schema(supplier_schema) \
        .csv(sup_url)
    
    supplier_df.write \
        .format("delta") \
        .mode("overwrite") \
        .partitionBy("date") \
        .save("/mnt/data/bronze/suppliers")
    
    print(f"✓ Loaded {supplier_df.count()} supplier records")
    display(supplier_df.limit(3))
except Exception as e:
    print(f"✗ Error: {str(e)}")

# COMMAND ----------

# ============================================================
# SUMMARY
# ============================================================

print(f"""
✓ ═══════════════════════════════════════════════
✓ BRONZE LAYER INGESTION COMPLETE
✓ ═══════════════════════════════════════════════

Date Processed: {today}
Source: GitHub ({GITHUB_USERNAME}/{GITHUB_REPO})

Tables Created:
  ✓ /mnt/data/bronze/production
  ✓ /mnt/data/bronze/shipments
  ✓ /mnt/data/bronze/quality
  ✓ /mnt/data/bronze/inventory
  ✓ /mnt/data/bronze/suppliers

Next Step: Run 02_silver_transformation notebook
""")

# COMMAND ----------

print("✓ Bronze ingestion ready for Silver transformation")
