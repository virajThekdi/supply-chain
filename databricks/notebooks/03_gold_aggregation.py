# Databricks notebook source
"""
GOLD LAYER - Business Intelligence & Analytics
===============================================

Purpose:
  - Aggregate cleaned data into business metrics
  - Create KPI tables for reporting
  - Build fact/dimension tables
  - Optimize for BI visualization

Output: Ready-to-use analytics tables
"""

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime

# Configuration
SILVER_PATH = "/mnt/data/silver"
GOLD_PATH = "/mnt/data/gold"
today = datetime.now().strftime("%Y_%m_%d")

# COMMAND ----------

# DELIVERY KPI TABLE
print("Creating delivery KPI table...")
shipment_silver = spark.read.format("delta").load(f"{SILVER_PATH}/shipments/date={today}")

delivery_kpi = shipment_silver.groupby() \
    .agg(
        count("shipment_id").alias("total_shipments"),
        sum(col("on_time_flag")).alias("on_time_shipments"),
        (sum(col("on_time_flag")) / count("shipment_id") * 100).alias("on_time_rate"),
        round(avg(col("delay_days")), 2).alias("avg_delay_days"),
        sum(when(col("delay_days") > 0, 1).otherwise(0)).alias("delayed_count"),
        countDistinct(col("destination")).alias("unique_routes")
    ) \
    .withColumn("report_date", to_date(lit(today), "yyyy_MM_dd")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Gold
delivery_kpi.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{GOLD_PATH}/delivery_kpi")

print(f"✓ Delivery KPI: {delivery_kpi.count()} records")
delivery_kpi.display()

# COMMAND ----------

# QUALITY KPI TABLE
print("Creating quality KPI table...")
quality_silver = spark.read.format("delta").load(f"{SILVER_PATH}/quality/date={today}")

quality_kpi = quality_silver.groupby("product_id") \
    .agg(
        avg("defect_rate").alias("avg_defect_rate"),
        max("defect_rate").alias("max_defect_rate"),
        sum("defects_count").alias("total_defects"),
        count("quality_id").alias("batch_count"),
        collect_list("defect_type")[0].alias("most_common_defect")
    ) \
    .withColumn("quality_status",
               when(col("avg_defect_rate") > 2, "HIGH") \
               .when(col("avg_defect_rate") > 1, "MEDIUM") \
               .otherwise("LOW")) \
    .withColumn("report_date", to_date(lit(today), "yyyy_MM_dd")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Gold
quality_kpi.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{GOLD_PATH}/quality_kpi")

print(f"✓ Quality KPI: {quality_kpi.count()} records")
quality_kpi.display()

# COMMAND ----------

# PRODUCTION KPI TABLE
print("Creating production KPI table...")
production_silver = spark.read.format("delta").load(f"{SILVER_PATH}/production/date={today}")

production_kpi = production_silver.groupby("plant_id") \
    .agg(
        sum("quantity_produced").alias("total_produced"),
        count("production_id").alias("production_runs"),
        round(avg("temperature"), 2).alias("avg_temperature"),
        round(avg("energy_consumption"), 2).alias("avg_energy"),
        round(avg("downtime_minutes"), 2).alias("avg_downtime"),
        round(sum(when(col("downtime_minutes") > 0, col("downtime_minutes")).otherwise(0)), 2) \
            .alias("total_downtime")
    ) \
    .withColumn("efficiency",
               ((col("total_produced") / (col("total_produced") + col("total_downtime") / 60 * 100)) * 100)) \
    .withColumn("report_date", to_date(lit(today), "yyyy_MM_dd")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Gold
production_kpi.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{GOLD_PATH}/production_kpi")

print(f"✓ Production KPI: {production_kpi.count()} records")
production_kpi.display()

# COMMAND ----------

# INVENTORY KPI TABLE
print("Creating inventory KPI table...")
inventory_silver = spark.read.format("delta").load(f"{SILVER_PATH}/inventory/date={today}")

inventory_kpi = inventory_silver.groupby("warehouse_id", "product_id") \
    .agg(
        avg("closing_stock").alias("avg_stock"),
        min("closing_stock").alias("min_stock"),
        max("closing_stock").alias("max_stock"),
        round(avg(col("shipped") / (col("opening_stock") + col("produced"))), 4) \
            .alias("turnover_rate"),
        sum("shipped").alias("total_shipped")
    ) \
    .withColumn("stock_category",
               when(col("avg_stock") < 1000, "CRITICAL") \
               .when(col("avg_stock") < 5000, "LOW") \
               .when(col("avg_stock") > 50000, "EXCESS") \
               .otherwise("NORMAL")) \
    .withColumn("report_date", to_date(lit(today), "yyyy_MM_dd")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Gold
inventory_kpi.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{GOLD_PATH}/inventory_kpi")

print(f"✓ Inventory KPI: {inventory_kpi.count()} records")
inventory_kpi.display()

# COMMAND ----------

# SUPPLIER PERFORMANCE TABLE
print("Creating supplier performance table...")
supplier_silver = spark.read.format("delta").load(f"{SILVER_PATH}/suppliers/date={today}")

supplier_performance = supplier_silver.agg(
    round(avg("quality_rating"), 2).alias("avg_quality_rating"),
    round((sum(col("on_time_flag")) / count("supplier_id") * 100), 2).alias("on_time_rate"),
    round(avg("delay_days"), 2).alias("avg_delay_days"),
    count(distinct("supplier_id")).alias("active_suppliers")
) \
    .withColumn("report_date", to_date(lit(today), "yyyy_MM_dd")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Gold
supplier_performance.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{GOLD_PATH}/supplier_performance")

print(f"✓ Supplier Performance: {supplier_performance.count()} records")
supplier_performance.display()

# COMMAND ----------

# ROUTE PERFORMANCE TABLE
print("Creating route performance table...")
shipment_silver = spark.read.format("delta").load(f"{SILVER_PATH}/shipments/date={today}")

route_performance = shipment_silver.groupby("origin", "destination") \
    .agg(
        count("shipment_id").alias("shipments"),
        sum(col("on_time_flag")).alias("on_time_count"),
        round((sum(col("on_time_flag")) / count("shipment_id") * 100), 2) \
            .alias("on_time_rate"),
        round(avg("delay_days"), 2).alias("avg_delay_days"),
        sum("quantity").alias("total_quantity")
    ) \
    .withColumn("route_status",
               when(col("on_time_rate") < 70, "POOR") \
               .when(col("on_time_rate") < 85, "FAIR") \
               .otherwise("GOOD")) \
    .withColumn("report_date", to_date(lit(today), "yyyy_MM_dd")) \
    .withColumn("load_timestamp", current_timestamp())

# Write to Gold
route_performance.write \
    .mode("overwrite") \
    .format("delta") \
    .save(f"{GOLD_PATH}/route_performance")

print(f"✓ Route Performance: {route_performance.count()} records")
route_performance.display()

# COMMAND ----------

print(f"\n✓ Gold layer aggregation complete for {today}")
print(f"Gold tables available at: {GOLD_PATH}/*")
print("\nAvailable tables:")
print("- delivery_kpi")
print("- quality_kpi")
print("- production_kpi")
print("- inventory_kpi")
print("- supplier_performance")
print("- route_performance")
