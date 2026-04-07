# Supply Chain Control Tower - Database Schemas

## Overview
This document defines the exact table schemas for the Supply Chain Control Tower system with data types and relationships.

---

## 1. PRODUCTION TABLE

**Purpose:** Track daily production output, machine performance, and energy consumption.

### Schema

| Column Name | Data Type | Description | Sample Value |
|---|---|---|---|
| `production_id` | STRING (UUID) | Unique identifier for production record | `prod_20260406_001` |
| `date` | DATE | Production date | `2026-04-06` |
| `plant_id` | STRING | Plant/Factory identifier | `PLANT_US_01` |
| `product_id` | STRING | Product code | `PROD_GLASS_A1` |
| `quantity_produced` | INT | Units produced | `5000` |
| `machine_id` | STRING | Machine identifier | `MACHINE_LINE_03` |
| `temperature` | FLOAT | Operating temperature (°C) | `850.5` |
| `energy_consumption` | FLOAT | Energy used (kWh) | `4500.75` |
| `downtime_minutes` | INT | Machine downtime (minutes) | `15` |

### Relationships
- Foreign Key: `product_id` → PRODUCT table
- Foreign Key: `plant_id` → PLANT table
- Foreign Key: `machine_id` → MACHINE table

---

## 2. SHIPMENT TABLE

**Purpose:** Track order fulfillment, delivery status, and delays.

### Schema

| Column Name | Data Type | Description | Sample Value |
|---|---|---|---|
| `shipment_id` | STRING (UUID) | Unique identifier for shipment | `ship_20260406_001` |
| `order_id` | STRING | Purchase order number | `PO_2026_04_001` |
| `product_id` | STRING | Product being shipped | `PROD_GLASS_A1` |
| `quantity` | INT | Quantity shipped | `1000` |
| `origin` | STRING | Origin warehouse/plant | `WAREHOUSE_US_01` |
| `destination` | STRING | Destination warehouse/customer | `WAREHOUSE_EU_02` |
| `supplier_id` | STRING | Supplier identifier (if external) | `SUP_DB_GLASS` |
| `dispatch_date` | DATE | Date shipment left origin | `2026-04-06` |
| `expected_delivery_date` | DATE | Promised delivery date | `2026-04-15` |
| `actual_delivery_date` | DATE | Actual arrival date (nullable) | `2026-04-17` |
| `delay_days` | INT | Days delayed (0 if on-time) | `2` |
| `status` | STRING | Current status | `DELAYED` |

### Valid Status Values
- `PENDING` → Not yet shipped
- `IN_TRANSIT` → Currently being transported
- `DELAYED` → Late delivery expected
- `DELIVERED` → Completed delivery
- `CANCELLED` → Order cancelled

### Relationships
- Foreign Key: `order_id` → ORDER table
- Foreign Key: `product_id` → PRODUCT table
- Foreign Key: `supplier_id` → SUPPLIER table

---

## 3. INVENTORY TABLE

**Purpose:** Daily inventory snapshot across warehouses.

### Schema

| Column Name | Data Type | Description | Sample Value |
|---|---|---|---|
| `inventory_id` | STRING (UUID) | Unique identifier | `inv_20260406_01` |
| `date` | DATE | Inventory snapshot date | `2026-04-06` |
| `product_id` | STRING | Product code | `PROD_GLASS_A1` |
| `warehouse_id` | STRING | Warehouse location | `WAREHOUSE_US_01` |
| `opening_stock` | INT | Stock at start of day | `10000` |
| `produced` | INT | Units produced during day | `5000` |
| `shipped` | INT | Units shipped during day | `3000` |
| `closing_stock` | INT | Stock at end of day | `12000` |

### Formula
```
closing_stock = opening_stock + produced - shipped
```

### Relationships
- Foreign Key: `product_id` → PRODUCT table
- Foreign Key: `warehouse_id` → WAREHOUSE table

---

## 4. SUPPLIER TABLE

**Purpose:** Track supplier performance and delivery reliability.

### Schema

| Column Name | Data Type | Description | Sample Value |
|---|---|---|---|
| `supplier_id` | STRING | Supplier code | `SUP_DB_GLASS` |
| `supplier_name` | STRING | Company name | `DB Glass Manufacturing` |
| `material_type` | STRING | Material supplied | `Raw Glass Sheets` |
| `delivery_date` | DATE | Date material delivered | `2026-04-06` |
| `expected_date` | DATE | Expected delivery date | `2026-04-05` |
| `delay_days` | INT | Days late (0 if on-time) | `1` |
| `quality_rating` | FLOAT | Quality score (0-100) | `92.5` |

### Relationships
- Connects to SHIPMENT table via `supplier_id`

---

## 5. QUALITY TABLE

**Purpose:** Track defects and quality metrics.

### Schema

| Column Name | Data Type | Description | Sample Value |
|---|---|---|---|
| `quality_id` | STRING (UUID) | Unique identifier | `qual_20260406_001` |
| `date` | DATE | Quality check date | `2026-04-06` |
| `product_id` | STRING | Product being checked | `PROD_GLASS_A1` |
| `batch_id` | STRING | Production batch ID | `BATCH_2026_04_06_001` |
| `defects_count` | INT | Number of defective units | `12` |
| `defect_type` | STRING | Type of defect | `CRACK` |
| `defect_rate` | FLOAT | Defect percentage | `0.24` |

### Valid Defect Types
- `CRACK` → Physical cracks
- `BUBBLE` → Air bubbles in material
- `DISCOLORATION` → Color inconsistency
- `DIMENSION_OFF` → Size outside tolerance
- `SURFACE_SCRATCH` → Surface imperfections
- `OTHER` → Unspecified defect

### Relationships
- Foreign Key: `product_id` → PRODUCT table
- Foreign Key: `batch_id` → BATCH table

---

## 6. MASTER TABLES (Reference Data)

### PRODUCT TABLE

| Column | Type | Sample |
|---|---|---|
| `product_id` | STRING | `PROD_GLASS_A1` |
| `product_name` | STRING | `Tempered Glass Panel 2x3` |
| `category` | STRING | `Glass` |
| `unit_price` | FLOAT | `150.00` |

### PLANT TABLE

| Column | Type | Sample |
|---|---|---|
| `plant_id` | STRING | `PLANT_US_01` |
| `plant_name` | STRING | `US Manufacturing Plant - Texas` |
| `location` | STRING | `Houston, TX` |
| `capacity` | INT | `50000` |

### WAREHOUSE TABLE

| Column | Type | Sample |
|---|---|---|
| `warehouse_id` | STRING | `WAREHOUSE_US_01` |
| `warehouse_name` | STRING | `US Central Warehouse` |
| `location` | STRING | `Chicago, IL` |
| `capacity` | INT | `100000` |

---

## 7. KEY RELATIONSHIPS DIAGRAM

```
PRODUCT
  ├─ PRODUCTION (product_id FK)
  ├─ SHIPMENT (product_id FK)
  ├─ INVENTORY (product_id FK)
  └─ QUALITY (product_id FK)

PLANT
  └─ PRODUCTION (plant_id FK)

WAREHOUSE
  └─ INVENTORY (warehouse_id FK)

SUPPLIER
  └─ SHIPMENT (supplier_id FK)
     └─ SUPPLIER performance metrics

ORDER
  └─ SHIPMENT (order_id FK)

BATCH
  └─ QUALITY (batch_id FK)
```

---

## 8. DATA CONSTRAINTS & VALIDATION

### Production Table
- `quantity_produced` ≥ 0
- `temperature` between 0°C and 2000°C
- `energy_consumption` ≥ 0
- `downtime_minutes` ≥ 0

### Shipment Table
- `quantity` ≥ 1
- `expected_delivery_date` ≥ `dispatch_date`
- `actual_delivery_date` NULL until delivered
- `delay_days` = `actual_delivery_date` - `expected_delivery_date`

### Inventory Table
- `opening_stock` ≥ 0
- `produced` ≥ 0
- `shipped` ≤ `opening_stock + produced`
- `closing_stock` = `opening_stock + produced - shipped`
- `closing_stock` ≥ 0

### Quality Table
- `defects_count` ≥ 0
- `defect_rate` between 0 and 100
- If `defects_count` = 0, then `defect_rate` = 0

### Supplier Table
- `quality_rating` between 0 and 100
- `delay_days` ≥ 0

---

## 9. DATA TYPES MAPPING

### Python (Pandas)
```python
{
    'production_id': 'object',
    'date': 'datetime64',
    'plant_id': 'object',
    'product_id': 'object',
    'quantity_produced': 'int64',
    'machine_id': 'object',
    'temperature': 'float64',
    'energy_consumption': 'float64',
    'downtime_minutes': 'int64'
}
```

### PySpark (Databricks)
```python
StructType([
    StructField("production_id", StringType()),
    StructField("date", DateType()),
    StructField("plant_id", StringType()),
    StructField("product_id", StringType()),
    StructField("quantity_produced", IntegerType()),
    StructField("machine_id", StringType()),
    StructField("temperature", FloatType()),
    StructField("energy_consumption", FloatType()),
    StructField("downtime_minutes", IntegerType())
])
```

### SQL (Standard)
```sql
production_id VARCHAR(50) PRIMARY KEY,
date DATE NOT NULL,
plant_id VARCHAR(50) NOT NULL,
product_id VARCHAR(50) NOT NULL,
quantity_produced INT NOT NULL,
machine_id VARCHAR(50),
temperature FLOAT,
energy_consumption FLOAT,
downtime_minutes INT
```

---

## 10. SAMPLE DATA RANGES

### Production
- Daily products: 3,000 - 10,000 units
- Temperature: 800 - 900°C (nominal)
- Energy: 3,500 - 5,500 kWh/day
- Downtime: 0 - 120 minutes/day

### Shipments
- Monthly shipments: 50 - 200 orders
- Typical delivery: 5 - 15 days
- Delays: 0 - 40% of orders
- Routes: US, EU, APAC

### Inventory
- Stock levels: 5,000 - 50,000 units/product
- Turnover: 2-4 times/month

### Quality
- Defect rate: 0.1% - 3%
- Most common: Cracks (35%), Bubbles (25%)

### Supplier
- Suppliers: 15 - 25 active
- On-time rate: 70 - 95%
- Quality: 85 - 98% rating

---

## 11. HISTORICAL TRACKING

Data retention:
- **Raw data**: 3 years
- **Aggregated**: Indefinite
- **Snapshots**: Daily

