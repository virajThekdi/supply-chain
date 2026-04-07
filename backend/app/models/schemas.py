"""
Data models for the Supply Chain Control Tower API.
Uses Pydantic for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class ShipmentStatus(str, Enum):
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"

class DefectType(str, Enum):
    CRACK = "CRACK"
    BUBBLE = "BUBBLE"
    DISCOLORATION = "DISCOLORATION"
    DIMENSION_OFF = "DIMENSION_OFF"
    SURFACE_SCRATCH = "SURFACE_SCRATCH"
    OTHER = "OTHER"

# ============================================================================
# KPI MODELS
# ============================================================================

class KPIMetrics(BaseModel):
    """Overall KPI metrics for the supply chain."""
    
    # Delivery metrics
    on_time_delivery_rate: float = Field(..., description="Percentage of on-time deliveries")
    average_delay_days: float = Field(..., description="Average delay in days for delayed shipments")
    total_delayed_shipments: int = Field(..., description="Total number of delayed shipments")
    
    # Quality metrics
    average_defect_rate: float = Field(..., description="Average defect rate across all batches")
    highest_defect_product: str = Field(..., description="Product with highest defect rate")
    quality_trend: str = Field(..., description="Trend: IMPROVING, STABLE, DECLINING")
    
    # Production metrics
    total_production_volume: int = Field(..., description="Total units produced")
    average_machine_downtime: float = Field(..., description="Average downtime per machine (minutes)")
    production_efficiency: float = Field(..., description="Percentage efficiency vs plan")
    
    # Supplier metrics
    average_supplier_rating: float = Field(..., description="Average supplier quality rating")
    supplier_on_time_rate: float = Field(..., description="Percentage of on-time deliveries by suppliers")
    underperforming_suppliers: List[str] = Field(..., description="Suppliers below threshold")
    
    # Inventory metrics
    average_inventory_turnover: float = Field(..., description="Inventory turnover ratio")
    low_stock_products: List[str] = Field(..., description="Products with stock below threshold")
    inventory_across_warehouses: Dict[str, int] = Field(..., description="Stock levels by warehouse")
    
    # Operational metrics
    date_calculated: date = Field(..., description="Date of KPI calculation")
    data_freshness_hours: float = Field(..., description="Hours since last data update")

class KPIDetail(BaseModel):
    """Detailed KPI information for specific dimensions."""
    
    metric_name: str
    value: float
    unit: str
    threshold: Optional[float] = None
    status: str = Field(..., description="RED, YELLOW, GREEN")
    trend: str = Field(..., description="UP, DOWN, STABLE")
    timestamp: datetime

# ============================================================================
# ANOMALY MODELS
# ============================================================================

class Anomaly(BaseModel):
    """Detected anomaly in supply chain data."""
    
    anomaly_id: str = Field(..., description="Unique anomaly identifier")
    type: str = Field(..., description="QUALITY, DELAY, DEFECT, PERFORMANCE, INVENTORY")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    title: str = Field(..., description="Short description of anomaly")
    description: str = Field(..., description="Detailed explanation")
    affected_entity: str = Field(..., description="Product ID, Supplier ID, or Warehouse ID")
    entity_type: str = Field(..., description="PRODUCT, SUPPLIER, WAREHOUSE, SHIPMENT, MACHINE")
    detected_date: date
    detected_value: float = Field(..., description="The anomalous value")
    normal_range: tuple = Field(..., description="(min, max) of normal range")
    root_cause: Optional[str] = None
    recommended_action: Optional[str] = None
    ai_explanation: Optional[str] = None

class AnomalyResponse(BaseModel):
    """Response containing multiple anomalies."""
    
    total_anomalies: int
    critical_count: int
    high_count: int
    recent_anomalies: List[Anomaly]
    summary: str

# ============================================================================
# CHAT / LLM MODELS
# ============================================================================

class ChatMessage(BaseModel):
    """User message for chat interaction."""
    
    query: str = Field(..., min_length=1, max_length=500, description="User question")
    context: Optional[str] = Field(None, description="Optional context (product ID, date range, etc.)")
    conversation_id: Optional[str] = Field(None, description="For maintaining conversation context")

class ChatResponse(BaseModel):
    """Response from LLM with RAG context."""
    
    query: str
    response: str = Field(..., description="AI-powered answer")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    sources: List[str] = Field(..., description="Data sources used (RAG)")
    timestamp: datetime
    conversation_id: str

# ============================================================================
# DATA TABLE MODELS
# ============================================================================

class ProductionRecord(BaseModel):
    """Production table record."""
    
    production_id: str
    date: date
    plant_id: str
    product_id: str
    quantity_produced: int
    machine_id: str
    temperature: float
    energy_consumption: float
    downtime_minutes: int

class ShipmentRecord(BaseModel):
    """Shipment table record."""
    
    shipment_id: str
    order_id: str
    product_id: str
    quantity: int
    origin: str
    destination: str
    supplier_id: str
    dispatch_date: date
    expected_delivery_date: date
    actual_delivery_date: Optional[date] = None
    delay_days: int
    status: ShipmentStatus

class InventoryRecord(BaseModel):
    """Inventory table record."""
    
    inventory_id: str
    date: date
    product_id: str
    warehouse_id: str
    opening_stock: int
    produced: int
    shipped: int
    closing_stock: int

class QualityRecord(BaseModel):
    """Quality table record."""
    
    quality_id: str
    date: date
    product_id: str
    batch_id: str
    defects_count: int
    defect_type: DefectType
    defect_rate: float

class SupplierRecord(BaseModel):
    """Supplier table record."""
    
    supplier_id: str
    supplier_name: str
    material_type: str
    delivery_date: date
    expected_date: date
    delay_days: int
    quality_rating: float

# ============================================================================
# AGGREGATED METRICS MODELS
# ============================================================================

class ProductMetrics(BaseModel):
    """Metrics for a specific product."""
    
    product_id: str
    product_name: str
    total_produced: int
    total_shipped: int
    current_inventory: int
    defect_rate: float
    on_time_delivery_rate: float
    last_updated: datetime

class SupplierMetrics(BaseModel):
    """Metrics for a specific supplier."""
    
    supplier_id: str
    supplier_name: str
    on_time_rate: float
    average_quality_rating: float
    average_delay_days: float
    last_delivery_date: date
    status: str = Field(..., description="EXCELLENT, GOOD, WARNING, POOR")

class WarehouseMetrics(BaseModel):
    """Metrics for a specific warehouse."""
    
    warehouse_id: str
    warehouse_name: str
    total_capacity: int
    current_stock: int
    utilization_rate: float  # percentage
    number_of_products: int
    turnover_rate: float
    last_updated: datetime

# ============================================================================
# PERIOD-BASED METRICS
# ============================================================================

class DateRangeMetrics(BaseModel):
    """Metrics for a date range."""
    
    start_date: date
    end_date: date
    total_days: int
    total_production: int
    total_shipments: int
    total_defects: int
    average_defect_rate: float
    on_time_rate: float
    average_delay_days: float

class ComparisonMetrics(BaseModel):
    """Compare metrics between two periods."""
    
    period_1_start: date
    period_1_end: date
    period_2_start: date
    period_2_end: date
    
    production_change: float  # percentage change
    defect_rate_change: float
    delivery_rate_change: float
    insights: List[str]

# ============================================================================
# ERROR RESPONSES
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str
    detail: str
    timestamp: datetime
    status_code: int

# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthStatus(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="HEALTHY, DEGRADED, UNHEALTHY")
    version: str
    database_connection: bool
    data_files_latest: datetime
    messages_processed: int
    last_check: datetime
