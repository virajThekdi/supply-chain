# Databricks notebook source
"""
SILVER LAYER - Data Cleaning & Transformation
==============================================

Purpose:
  - Clean and validate data
  - Remove duplicates
  - Handle nulls
  - Apply business logic transformations
  - Enrich with reference data

Output: Clean, validated data ready for analytics
"""

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime

# Configuration
BRONZE_PATH = "/mnt/data/bronze"
SILVER_PATH = "/mnt/data/silver"
today = datetime.now().strftime("%Y_%m_%d")

# COMMAND ----------

# PRODUCTION SILVER LAYER
print("Processing production data...")
production_bronze = spark.read.format("delta").load(f"{BRONZE_PATH}/production/date={today}")

production_silver = production_bronze \
    .dropDuplicates(["production_id"]) \
    .filter(col("quantity_produced") >= 0) \
    .filter(col("temperature").between(0, 2000)) \
    .filter(col("energy_consumption") >= 0) \
    .withColumn("data_quality_score", 
               when(col("downtime_minutes") > 120, 0.7) \
               .when(col("downtime_minutes") > 60, 0.8) \
               .otherwise(0.95)) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Silver
production_silver.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{SILVER_PATH}/production/date={today}")

print(f"✓ Production silver: {production_silver.count()} records")

# COMMAND ----------

# SHIPMENT SILVER LAYER
print("Processing shipment data...")
shipment_bronze = spark.read.format("delta").load(f"{BRONZE_PATH}/shipments/date={today}")

shipment_silver = shipment_bronze \
    .dropDuplicates(["shipment_id"]) \
    .filter(col("quantity") > 0) \
    .filter(col("expected_delivery_date") >= col("dispatch_date")) \
    .withColumn("on_time_flag", 
               when((col("actual_delivery_date").isNotNull()) & 
                    (col("delay_days") == 0), 1).otherwise(0)) \
    .withColumn("delay_category",
               when(col("delay_days") == 0, "On-Time") \
               .when(col("delay_days") <= 3, "Minor Delay") \
               .when(col("delay_days") <= 7, "Major Delay") \
               .otherwise("Critical Delay")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Silver
shipment_silver.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{SILVER_PATH}/shipments/date={today}")

print(f"✓ Shipment silver: {shipment_silver.count()} records")

# COMMAND ----------

# QUALITY SILVER LAYER
print("Processing quality data...")
quality_bronze = spark.read.format("delta").load(f"{BRONZE_PATH}/quality/date={today}")

quality_silver = quality_bronze \
    .dropDuplicates(["quality_id"]) \
    .filter(col("defects_count") >= 0) \
    .filter((col("defect_rate") >= 0) & (col("defect_rate") <= 100)) \
    .withColumn("quality_flag",
               when(col("defect_rate") > 3, "HIGH") \
               .when(col("defect_rate") > 1, "MEDIUM") \
               .otherwise("LOW")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Silver
quality_silver.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{SILVER_PATH}/quality/date={today}")

print(f"✓ Quality silver: {quality_silver.count()} records")

# COMMAND ----------

# INVENTORY SILVER LAYER
print("Processing inventory data...")
inventory_bronze = spark.read.format("delta").load(f"{BRONZE_PATH}/inventory/date={today}")

# Validate: closing_stock = opening_stock + produced - shipped
inventory_silver = inventory_bronze \
    .dropDuplicates(["inventory_id"]) \
    .filter(col("closing_stock") >= 0) \
    .withColumn("inventory_validation",
               when((col("opening_stock") + col("produced") - col("shipped")) == col("closing_stock"), "Pass") \
               .otherwise("Fail")) \
    .withColumn("stock_level",
               when(col("closing_stock") < 1000, "CRITICAL") \
               .when(col("closing_stock") < 5000, "LOW") \
               .when(col("closing_stock") > 50000, "EXCESS") \
               .otherwise("NORMAL")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Silver
inventory_silver.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{SILVER_PATH}/inventory/date={today}")

print(f"✓ Inventory silver: {inventory_silver.count()} records")

# COMMAND ----------

# SUPPLIER SILVER LAYER
print("Processing supplier data...")
supplier_bronze = spark.read.format("delta").load(f"{BRONZE_PATH}/suppliers/date={today}")

supplier_silver = supplier_bronze \
    .dropDuplicates(["supplier_id"]) \
    .filter((col("quality_rating") >= 0) & (col("quality_rating") <= 100)) \
    .filter(col("delay_days") >= 0) \
    .withColumn("supplier_performance",
               when(col("quality_rating") >= 90, "EXCELLENT") \
               .when(col("quality_rating") >= 80, "GOOD") \
               .when(col("quality_rating") >= 70, "ACCEPTABLE") \
               .otherwise("POOR")) \
    .withColumn("on_time_flag",
               when(col("delay_days") == 0, 1).otherwise(0)) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Silver
supplier_silver.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{SILVER_PATH}/suppliers/date={today}")

print(f"✓ Supplier silver: {supplier_silver.count()} records")

# COMMAND ----------

print(f"\n✓ Silver layer processing complete for {today}")
print(f"Silver path: {SILVER_PATH}/*/date={today}")
