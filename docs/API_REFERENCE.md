# 📚 API Reference Documentation

**Supply Chain Control Tower - Complete API Specification**

---

## Table of Contents
1. [Authentication](#authentication)
2. [Base URL & Headers](#base-url--headers)
3. [Error Handling](#error-handling)
4. [KPI Endpoints](#kpi-endpoints)
5. [Anomaly Endpoints](#anomaly-endpoints)
6. [Chat/LLM Endpoints](#chat--llm-endpoints)
7. [Data Endpoints](#data-endpoints)
8. [System Endpoints](#system-endpoints)
9. [Webhooks](#webhooks-optional)
10. [Rate Limiting](#rate-limiting)

---

## Authentication

### Current Status: None Required
Development setup operates with **no authentication**. All endpoints are publicly accessible on localhost.

### Production Deployment
```
Authorization: Bearer {JWT_TOKEN}

Token Format:
{
  "sub": "user_id",
  "role": "admin|analyst|viewer",
  "exp": 1234567890
}
```

---

## Base URL & Headers

### Development
```
Base URL: http://localhost:8000
Environment: Development/Testing
CORS: Enabled for localhost:3000
```

### Production
```
Base URL: https://api.control-tower.company.com
Environment: Production
CORS: Restricted to *.company.com
```

### Required Headers
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}  # Production only
```

### Optional Headers
```
X-Request-ID: {uuid}           # For tracing
X-User-Context: {user_id}      # For enterprise features
User-Agent: {client_name}      # For analytics
```

---

## Error Handling

### HTTP Status Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal error |
| 503 | Service Unavailable | Temporary downtime |

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Parameter 'severity' must be one of: CRITICAL, HIGH, MEDIUM, LOW",
    "details": {
      "parameter": "severity",
      "value": "URGENT",
      "allowed": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    },
    "timestamp": "2026-04-07T10:30:00Z",
    "request_id": "req_123abc"
  }
}
```

---

## KPI Endpoints

### GET /kpis
**Get all KPI metrics**

#### Request
```http
GET /kpis HTTP/1.1
Host: localhost:8000
Accept: application/json
```

#### Query Parameters
```
days: integer (optional)  # Last N days (default: 1)
groupby: string (optional)  # aggregate|daily|weekly (default: aggregate)
```

#### Response (200 OK)
```json
{
  "timestamp": "2026-04-07T10:30:00Z",
  "delivery": {
    "on_time_delivery_rate": 92.5,
    "average_delay": 0.8,
    "on_time_count": 37,
    "delayed_count": 3,
    "total_shipments": 40,
    "delayed_routes": ["APAC→US", "EU→APAC"]
  },
  "quality": {
    "average_defect_rate": 0.42,
    "total_batches": 12,
    "most_common_defect": "BUBBLE",
    "defects_by_product": {
      "PROD_GLASS_A1": 0.15,
      "PROD_GLASS_B2": 0.35,
      "PROD_GLASS_C3": 0.78
    }
  },
  "production": {
    "total_output": 54000,
    "machine_efficiency": 87.3,
    "average_downtime": 12.5,
    "energy_consumption": 18750,
    "by_plant": {
      "PLANT_US_01": 18000,
      "PLANT_EU_01": 18000,
      "PLANT_APAC_01": 18000
    }
  },
  "supplier": {
    "average_quality_rating": 88.2,
    "on_time_delivery_rate": 89.1,
    "supplier_count": 11,
    "at_risk_suppliers": ["SUP_006", "SUP_009"]
  },
  "inventory": {
    "total_stock": 156800,
    "average_turnover": 4.2,
    "critical_stock_items": 2,
    "by_warehouse": {
      "WH_US_01": 52200,
      "WH_EU_01": 52300,
      "WH_APAC_01": 52300
    }
  },
  "alerts": {
    "critical_count": 2,
    "high_count": 5,
    "total_alerts": 12
  }
}
```

#### Example
```bash
curl -X GET "http://localhost:8000/kpis" \
  -H "Content-Type: application/json"
```

---

### GET /kpis/delivery
**Get delivery KPI metrics**

#### Response (200 OK)
```json
{
  "on_time_delivery_rate": 92.5,
  "average_delay_days": 0.8,
  "on_time_count": 37,
  "delayed_count": 3,
  "total_shipments": 40,
  "delayed_by_percentage": 7.5,
  "route_performance": [
    {
      "route": "US→EU",
      "on_time_rate": 100.0,
      "shipments": 10
    },
    {
      "route": "US→APAC",
      "on_time_rate": 80.0,
      "shipments": 10
    },
    {
      "route": "EU→US",
      "on_time_rate": 90.0,
      "shipments": 10
    }
  ]
}
```

---

### GET /kpis/quality
**Get quality KPI metrics**

#### Response (200 OK)
```json
{
  "average_defect_rate": 0.42,
  "total_batches": 12,
  "highest_defect_rate": 0.78,
  "lowest_defect_rate": 0.15,
  "most_common_defect": "BUBBLE",
  "defect_distribution": {
    "CRACK": 2,
    "BUBBLE": 5,
    "DISCOLORATION": 2,
    "DIMENSION_OFF": 2,
    "SURFACE_SCRATCH": 1,
    "OTHER": 0
  },
  "defects_by_product": {
    "PROD_GLASS_A1": {
      "defect_rate": 0.15,
      "batches": 4
    },
    "PROD_GLASS_B2": {
      "defect_rate": 0.35,
      "batches": 4
    },
    "PROD_GLASS_C3": {
      "defect_rate": 0.78,
      "batches": 4
    }
  }
}
```

---

### GET /kpis/production
**Get production KPI metrics**

#### Response (200 OK)
```json
{
  "total_output": 54000,
  "machine_efficiency": 87.3,
  "average_downtime": 12.5,
  "total_energy_consumption": 18750,
  "efficiency_status": "GOOD",
  "by_plant": [
    {
      "plant_id": "PLANT_US_01",
      "output": 18000,
      "efficiency": 86.5,
      "downtime": 12.3,
      "energy": 6250
    }
  ],
  "by_product": [
    {
      "product_id": "PROD_GLASS_A1",
      "quantity": 18000,
      "machines_used": 3
    }
  ]
}
```

---

### GET /kpis/supplier
**Get supplier KPI metrics**

#### Response (200 OK)
```json
{
  "average_quality_rating": 88.2,
  "on_time_delivery_rate": 89.1,
  "total_suppliers": 11,
  "active_suppliers": 11,
  "at_risk_suppliers": 2,
  "top_performers": [
    {
      "supplier_id": "SUP_001",
      "quality_rating": 96,
      "on_time_rate": 100,
      "material_type": "Raw Materials"
    }
  ],
  "at_risk": [
    {
      "supplier_id": "SUP_006",
      "quality_rating": 78,
      "on_time_rate": 75,
      "material_type": "Components"
    }
  ]
}
```

---

### GET /kpis/inventory
**Get inventory KPI metrics**

#### Response (200 OK)
```json
{
  "total_stock": 156800,
  "average_inventory_turnover": 4.2,
  "critical_stock_count": 2,
  "warehouse_utilization": 78.3,
  "by_warehouse": [
    {
      "warehouse_id": "WH_US_01",
      "stock": 52200,
      "utilization": 78.3
    }
  ],
  "critical_items": [
    {
      "product_id": "PROD_GLASS_B2",
      "warehouse": "WH_EU_01",
      "stock": 450,
      "status": "CRITICAL"
    }
  ]
}
```

---

## Anomaly Endpoints

### GET /anomalies
**Get all detected anomalies**

#### Query Parameters
```
severity: string (optional)  # CRITICAL|HIGH|MEDIUM|LOW
type: string (optional)      # DELAY|QUALITY|INVENTORY|PRODUCTION|SUPPLIER
limit: integer (default: 100)
offset: integer (default: 0)
```

#### Response (200 OK)
```json
{
  "anomalies": [
    {
      "id": "anom_abc123",
      "type": "DELAY",
      "severity": "HIGH",
      "title": "Excessive delay to APAC",
      "description": "Shipment SHP_001 delayed by 4 days",
      "metric_value": 4,
      "threshold": 2.5,
      "status": "ACTIVE",
      "detected_at": "2026-04-07T08:30:00Z",
      "root_cause": "Customs clearance delays",
      "recommended_action": "Contact customs broker",
      "affected_entities": ["SHP_001", "ORD_042"],
      "confidence": 0.95
    }
  ],
  "summary": {
    "total_anomalies": 12,
    "critical_count": 2,
    "high_count": 5,
    "medium_count": 3,
    "low_count": 2
  },
  "page": 1,
  "page_size": 100
}
```

#### Example
```bash
curl "http://localhost:8000/anomalies?severity=CRITICAL&limit=10"
```

---

### GET /anomalies/by-type/{type}
**Get anomalies by type**

#### Path Parameters
```
type: DELAY | QUALITY | INVENTORY | PRODUCTION | SUPPLIER
```

#### Response (200 OK)
```json
{
  "anomaly_type": "DELAY",
  "count": 3,
  "anomalies": [
    {
      "id": "anom_001",
      "title": "Route US→APAC delay",
      "severity": "HIGH",
      "description": "Average delay: 4 days",
      "affected_shipments": 2
    }
  ]
}
```

---

### GET /anomalies/{id}
**Get specific anomaly details**

#### Response (200 OK)
```json
{
  "id": "anom_abc123",
  "type": "DELAY",
  "severity": "HIGH",
  "title": "Excessive delay to APAC",
  "description": "Shipment SHP_001 delayed by 4 days",
  "detected_at": "2026-04-07T08:30:00Z",
  "root_cause_analysis": {
    "primary_cause": "Customs clearance delays",
    "secondary_factors": ["Port congestion", "Documentation issues"],
    "probability": 0.85
  },
  "recommended_actions": [
    {
      "action": "Contact customs broker",
      "priority": "HIGH",
      "estimated_impact": "Expedite by 1-2 days"
    }
  ],
  "affected_records": {
    "shipments": ["SHP_001"],
    "orders": ["ORD_042"],
    "customers": ["CUST_015"]
  },
  "history": [
    {
      "timestamp": "2026-04-05T10:00:00Z",
      "status": "DETECTED",
      "note": "Initial detection"
    }
  ]
}
```

---

### POST /anomalies/acknowledge
**Mark anomaly as acknowledged**

#### Request Body
```json
{
  "anomaly_id": "anom_abc123",
  "acknowledged_by": "user@company.com",
  "action_taken": "Contacted customer",
  "notes": "ETA updated to April 10"
}
```

#### Response (200 OK)
```json
{
  "id": "anom_abc123",
  "status": "ACKNOWLEDGED",
  "acknowledged_at": "2026-04-07T10:35:00Z",
  "acknowledged_by": "user@company.com"
}
```

---

## Chat / LLM Endpoints

### POST /ask
**Query the AI assistant**

#### Request Body
```json
{
  "query": "What is our on-time delivery rate?",
  "conversationId": "conv_xyz789",
  "context": {
    "product": "PROD_GLASS_A1",
    "timeframe": "last_7_days"
  }
}
```

#### Response (200 OK)
```json
{
  "conversationId": "conv_xyz789",
  "messageId": "msg_123",
  "query": "What is our on-time delivery rate?",
  "answer": "Based on the latest data, your on-time delivery rate is 92.5%. Out of 40 shipments, 37 were delivered on schedule.",
  "confidence": 0.95,
  "sources": [
    {
      "type": "SHIPMENT_DATA",
      "records_used": 40,
      "date_range": "2026-04-01 to 2026-04-07"
    }
  ],
  "follow_up_questions": [
    "Which routes have the most delays?",
    "How does this compare to last month?",
    "What are the main causes of delays?"
  ],
  "generated_at": "2026-04-07T10:40:00Z"
}
```

#### Example
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me defects by product",
    "conversationId": "conv_123"
  }'
```

---

### POST /conversations
**Create new conversation**

#### Request Body
```json
{
  "title": "Q1 Quality Review",
  "metadata": {
    "user": "analyst@company.com",
    "team": "Operations"
  }
}
```

#### Response (201 Created)
```json
{
  "conversationId": "conv_xyz789",
  "title": "Q1 Quality Review",
  "created_at": "2026-04-07T10:00:00Z",
  "messages": []
}
```

---

### GET /conversations/{conversationId}
**Get conversation history**

#### Response (200 OK)
```json
{
  "conversationId": "conv_xyz789",
  "title": "Q1 Quality Review",
  "created_at": "2026-04-07T10:00:00Z",
  "messages": [
    {
      "role": "user",
      "content": "What is our defect rate?",
      "timestamp": "2026-04-07T10:05:00Z"
    },
    {
      "role": "assistant",
      "content": "Your average defect rate is 0.42%",
      "timestamp": "2026-04-07T10:05:30Z",
      "confidence": 0.92
    }
  ]
}
```

---

### DELETE /conversations/{conversationId}
**Delete conversation**

#### Response (204 No Content)
```
(empty)
```

---

## Data Endpoints

### GET /data/shipments
**Get shipment records**

#### Query Parameters
```
limit: integer (default: 50, max: 1000)
offset: integer (default: 0)
status: string (PENDING|IN_TRANSIT|DELIVERED|DELAYED|CANCELLED)
date_from: ISO8601 date
date_to: ISO8601 date
product: string (product ID)
```

#### Response (200 OK)
```json
{
  "shipments": [
    {
      "shipment_id": "SHP_001",
      "order_id": "ORD_001",
      "product_id": "PROD_GLASS_A1",
      "quantity": 500,
      "origin": "US",
      "destination": "EU",
      "supplier_id": "SUP_001",
      "dispatch_date": "2026-04-01",
      "expected_delivery_date": "2026-04-05",
      "actual_delivery_date": "2026-04-05",
      "delay_days": 0,
      "status": "DELIVERED"
    }
  ],
  "total": 1250,
  "limit": 50,
  "offset": 0
}
```

---

### GET /data/quality
**Get quality records**

#### Response (200 OK)
```json
{
  "quality_records": [
    {
      "quality_id": "QA_001",
      "date": "2026-04-07",
      "product_id": "PROD_GLASS_A1",
      "batch_id": "BATCH_001",
      "defects_count": 2,
      "defect_type": "BUBBLE",
      "defect_rate": 0.20
    }
  ],
  "total": 156
}
```

---

### GET /data/production
**Get production records**

#### Response (200 OK)
```json
{
  "production_records": [
    {
      "production_id": "PROD_001",
      "date": "2026-04-07",
      "plant_id": "PLANT_US_01",
      "product_id": "PROD_GLASS_A1",
      "quantity_produced": 6000,
      "machine_id": "MACHINE_LINE_01",
      "temperature": 856,
      "energy_consumption": 2150,
      "downtime_minutes": 15
    }
  ],
  "total": 84
}
```

---

### GET /data/inventory
**Get inventory records**

#### Response (200 OK)
```json
{
  "inventory_records": [
    {
      "inventory_id": "INV_001",
      "date": "2026-04-07",
      "product_id": "PROD_GLASS_A1",
      "warehouse_id": "WH_US_01",
      "opening_stock": 5000,
      "produced": 6000,
      "shipped": 500,
      "closing_stock": 10500
    }
  ],
  "total": 18
}
```

---

### GET /data/suppliers
**Get supplier records**

#### Response (200 OK)
```json
{
  "suppliers": [
    {
      "supplier_id": "SUP_001",
      "supplier_name": "Global Raw Materials Inc",
      "material_type": "Raw Materials",
      "delivery_date": "2026-04-05",
      "expected_date": "2026-04-05",
      "delay_days": 0,
      "quality_rating": 96
    }
  ],
  "total": 11
}
```

---

## System Endpoints

### GET /health
**Health check**

#### Response (200 OK)
```json
{
  "status": "HEALTHY",
  "timestamp": "2026-04-07T10:50:00Z",
  "uptime_seconds": 3600,
  "data": {
    "freshness": {
      "last_production_data": "2026-04-07T10:30:00Z",
      "last_shipment_data": "2026-04-07T10:30:00Z",
      "last_quality_data": "2026-04-07T10:30:00Z"
    },
    "cached_until": "2026-04-07T10:35:00Z"
  },
  "services": {
    "kpi_calculator": "OK",
    "anomaly_detector": "OK",
    "llm_service": "OK"
  }
}
```

---

### GET /docs
**Interactive API documentation (Swagger UI)**

```
URL: http://localhost:8000/docs
Browser-based API explorer
Test endpoints directly
```

---

### GET /redoc
**Alternative API documentation (ReDoc)**

```
URL: http://localhost:8000/redoc
Read-only documentation
Organized by tags
```

---

### GET /openapi.json
**OpenAPI specification**

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Supply Chain Control Tower API",
    "version": "1.0.0"
  },
  "paths": { ... }
}
```

---

## Webhooks (Optional)

### Anomaly Alert Webhook

**POST** to customer-specified URL when anomaly detected

```json
{
  "event": "anomaly.detected",
  "timestamp": "2026-04-07T10:45:00Z",
  "data": {
    "anomaly_id": "anom_abc123",
    "type": "DELAY",
    "severity": "CRITICAL",
    "title": "Critical shipment delay detected"
  }
}
```

### Setup
```
POST /webhooks/register
{
  "event": "anomaly.detected",
  "url": "https://company.com/webhooks/anomalies",
  "secret": "webhook_secret_key"
}
```

---

## Rate Limiting

### Current Limits (Development)
```
No rate limiting (localhost)
```

### Production Limits (Recommended)
```
Authenticated User:
  - 1000 requests per hour
  - 100 requests per minute

Anonymous:
  - 100 requests per hour
  - 10 requests per minute
```

### Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 985
X-RateLimit-Reset: 1680849600
```

---

## Pagination

### Standard Pagination Format

```
Query Parameters:
  limit: int (default: 50, max: 1000)
  offset: int (default: 0)

Response:
{
  "items": [...],
  "total": 1250,
  "limit": 50,
  "offset": 0,
  "has_more": true,
  "next_offset": 50
}
```

---

## Filtering & Sorting

### Common Query Parameters

```
filter[field]: string       # Exact match
filter[field__gte]: value   # Greater than or equal
filter[field__lte]: value   # Less than or equal
filter[field__in]: val1,val2  # In list

sort_by: field              # Sort field
sort_order: asc|desc        # Sort direction

search: string              # Text search across fields
```

### Example
```
GET /data/shipments?
  filter[status]=DELAYED&
  filter[delay_days__gte]=2&
  sort_by=delay_days&
  sort_order=desc&
  limit=20
```

---

## Content Negotiation

### Accept Header
```
Accept: application/json          # Default
Accept: application/xml           # XML format
Accept: text/csv                  # CSV export
```

### Accept-Encoding
```
Accept-Encoding: gzip, deflate    # Compression
Content-Encoding: gzip            # Response compressed
```

---

## Versioning

### Current Version
```
API Version: 1.0.0
URL Path: /api/v1/ (ready for future versions)
Header: X-API-Version: 1.0.0
```

### Version Migration
```
v1.0 → v2.0: Backward compatible
  New endpoints: /api/v2/...
  Old endpoints: Still available
  Deprecation: 12-month notice
```

---

**API Version**: 1.0.0  
**Last Updated**: April 7, 2026  
**Status**: ✅ Ready for Use
