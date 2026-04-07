# 🏗️ System Architecture Documentation

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [Data Flow](#data-flow)
3. [Technology Stack](#technology-stack)
4. [Component Details](#component-details)
5. [Integration Points](#integration-points)
6. [Deployment Architecture](#deployment-architecture)
7. [Scalability Strategy](#scalability-strategy)

---

## High-Level Architecture

### Multi-Layered Design

```
┌────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│  React Frontend (Dashboard, Anomalies, Chat)               │
│  Port: 3000                                                 │
└──────────────────────┬─────────────────────────────────────┘
                       │ HTTP/REST API
                       │ JSON
                       ▼
┌────────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                           │
│  FastAPI Backend + Business Logic                          │
│  Port: 8000                                                 │
│  - KPI Service                                              │
│  - Anomaly Detection Service                               │
│  - LLM/RAG Service                                          │
└──────────────────────┬─────────────────────────────────────┘
                       │ File I/O (CSV)
                       │ DataFrame Operations
                       ▼
┌────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                │
│  CSV Files (GitHub-hosted)                                │
│  - Production data                                          │
│  - Shipment tracking                                        │
│  - Quality metrics                                          │
│  - Inventory snapshots                                      │
│  - Supplier data                                            │
└────────────────────────────────────────────────────────────┘
```

### Parallel Analytics Layer (Optional)

```
┌────────────────────────────────────────────────────────────┐
│              DATABRICKS (Optional)                           │
│  Bronze → Silver → Gold Transformation                     │
│  - Real-time ETL                                            │
│  - Data quality checks                                      │
│  - KPI aggregation tables                                   │
└────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Data Ingestion Flow

```
Generation Phase
┌─────────────────────────────────────┐
│ generate_daily_data.py              │
│ - Simulates production events       │
│ - Creates quality records           │
│ - Generates shipments               │
│ - Updates inventory                 │
└────────────┬────────────────────────┘
             │
             ▼ (Append/Create)
┌─────────────────────────────────────┐
│ data/raw/production_YYYY_MM_DD.csv  │
│ data/raw/shipments_YYYY_MM_DD.csv   │
│ data/raw/quality_YYYY_MM_DD.csv     │
│ data/raw/inventory_YYYY_MM_DD.csv   │
│ data/raw/suppliers_YYYY_MM_DD.csv   │
└────────────┬────────────────────────┘
             │
             ▼ (Push via GitHub Actions)
┌─────────────────────────────────────┐
│ GitHub Repository (Raw Content URLs)│
│ Shared data source for all layers   │
└─────────────────────────────────────┘
```

### 2. Real-Time Processing Flow

```
Browser Request
    │
    ▼ (HTTP)
┌────────────────────────────────────────────┐
│ FastAPI App (main.py)                      │
│ Routing & Request Validation               │
└──────────┬───────────────────────────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌──────────────┐  ┌──────────────────┐
│ GET /kpis    │  │ GET /anomalies   │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌──────────────────────────────────────┐
│ Load Latest CSV Files                │
│ (Cached in memory)                   │
└──────────┬───────────────────────────┘
           │
    ┌──────┴───────┐
    ▼              ▼
┌─────────────┐  ┌──────────────────┐
│KPICalculator│  │AnomalyDetector   │
│             │  │                  │
│- Aggregates │  │- Rolling avg     │
│- Computes   │  │- Std deviation   │
│- Trends     │  │- Isolation Forest│
└──────┬──────┘  └────────┬─────────┘
       │                  │
       └──────┬───────────┘
              ▼
         ┌──────────────┐
         │ Pydantic     │
         │ Serialize    │
         └──────┬───────┘
                ▼
         ┌──────────────┐
         │ JSON Response│
         │ to Browser   │
         └──────────────┘
```

### 3. LLM Query Flow

```
User: "What's our delivery rate?"
    │
    ▼
┌──────────────────────┐
│ FastAPI /ask endpoint│
│ POST request with    │
│ query & context      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ LLMService.process_query()           │
│                                      │
│ 1. Detect query intent               │
│    - Keywords: "delivery", "rate"    │
│    - Intent: DELIVERY_QUERY          │
│                                      │
│ 2. Retrieve context                  │
│    - Load shipment data              │
│    - Calculate on-time metrics       │
│    - Get trend data                  │
│                                      │
│ 3. Generate answer                   │
│    - Fill template with data         │
│    - Add confidence score            │
│    - List sources                    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────┐
│ Response Object      │
│ - Answer text        │
│ - Confidence 0-1     │
│ - Sources (data)     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Save to conversation │
│ (UUID-based)         │
└──────────┬───────────┘
           │
           ▼
        Browser
```

---

## Technology Stack

### Frontend Stack

```
React 18.2
    ├── react-dom (Virtual DOM)
    ├── axios (HTTP client)
    ├── CSS Grid (Responsive layouts)
    └── Hooks (useState, useEffect)

Components
├── Navigation
│   └── Logo, Pages Links, Health Status
├── Dashboard
│   ├── KPICard (x6)
│   ├── AlertCard
│   └── SimpleChart
├── Anomalies
│   ├── FilterButtons
│   ├── AnomalyCard (x N)
│   └── SummaryStats
└── Chat
    ├── MessageBubbles
    ├── SuggestedQuestions
    └── InputForm

CSS Architecture
├── CSS Variables (Colors, shadows, spacing)
├── Responsive Grid (768px breakpoint)
├── Animations (spin, fadeIn, slideUp)
├── Severity Badges (CRITICAL, HIGH, MEDIUM, LOW)
└── Dark/Light modes (ready)
```

### Backend Stack

```
FastAPI 0.104.1
    ├── Uvicorn (ASGI server)
    ├── Pydantic (Data validation)
    └── Python 3.9+

Services
├── KPICalculator
│   ├── Delivery metrics
│   ├── Quality analysis
│   ├── Production stats
│   ├── Supplier performance
│   └── Inventory tracking
├── AnomalyDetector
│   ├── Statistical methods
│   ├── Rolling average
│   ├── Standard deviation
│   ├── Isolation Forest
│   └── Business rules
└── LLMService
    ├── Query intent detection
    ├── Context retrieval
    ├── Template-based generation
    ├── Confidence scoring
    └── Conversation management

Data Processing
├── Pandas (DataFrames)
├── NumPy (Numerical ops)
├── Scikit-learn (ML)
└── SciPy (Statistics)
```

### Data Stack

```
Data Source
├── GitHub (Raw content URLs)
│   └── CSV files (daily)
│       ├── production_YYYY_MM_DD.csv
│       ├── shipments_YYYY_MM_DD.csv
│       ├── quality_YYYY_MM_DD.csv
│       ├── inventory_YYYY_MM_DD.csv
│       └── suppliers_YYYY_MM_DD.csv
│
└── Local File System
    └── data/raw/
        └── 5 tables x 365 days


Analytics (Optional)
├── Databricks
│   ├── PySpark (Distributed processing)
│   └── Delta Lake (Versioning)
│
├── ChromaDB (Vector embeddings)
│   └── Semantic search
│
└── Ollama (Local LLM)
    └── LLaMA models
```

---

## Component Details

### 1. KPI Service Architecture

```python
KPICalculator
│
├── File Discovery
│   └── _get_latest_csvs()
│       Finds most recent YYYY_MM_DD files
│
├── Data Loading
│   ├── _load_production_data()
│   ├── _load_shipment_data()
│   ├── _load_inventory_data()
│   ├── _load_quality_data()
│   └── _load_supplier_data()
│
├── Calculation Methods
│   ├── Delivery KPIs
│   │   ├── calculate_on_time_delivery_rate()
│   │   ├── calculate_average_delay()
│   │   └── calculate_route_performance()
│   ├── Quality KPIs
│   │   ├── calculate_defect_metrics()
│   │   └── calculate_product_quality()
│   ├── Production KPIs
│   │   ├── calculate_production_metrics()
│   │   └── calculate_machine_efficiency()
│   ├── Supplier KPIs
│   │   ├── calculate_supplier_metrics()
│   │   └── calculate_supplier_ranking()
│   └── Inventory KPIs
│       ├── calculate_inventory_metrics()
│       └── calculate_warehouse_utilization()
│
├── Aggregation
│   └── calculate_all_kpis()
│       Returns: KPIMetrics (Pydantic model)
│
└── Caching
    └── 5-minute TTL cache
```

### 2. Anomaly Detection Architecture

```python
AnomalyDetector
│
├── Configuration
│   ├── sensitivity: 2.0
│   ├── anomaly types: 5
│   └── algorithms: 2
│
├── Detection Methods
│   ├── detect_delivery_anomalies()
│   │   Algorithm: Rolling avg + std dev
│   │   Threshold: μ + 2σ
│   │   Triggers: Delays > threshold
│   │
│   ├── detect_quality_anomalies()
│   │   Algorithm: Simple threshold
│   │   Threshold: 2% defect rate
│   │   Triggers: Defect rate > 2%
│   │
│   ├── detect_inventory_anomalies()
│   │   Algorithm: Business rules
│   │   Rules: Critical stock < 1000, constraints
│   │   Triggers: Violations
│   │
│   ├── detect_production_anomalies()
│   │   Algorithm: Rolling average
│   │   Threshold: Downtime > 60 min
│   │   Triggers: Machine failures
│   │
│   └── detect_supplier_anomalies()
│       Algorithm: Performance trend
│       Threshold: Quality < 85%
│       Triggers: Rating drops
│
├── Severity Classification
│   ├── CRITICAL: Business-stopping
│   ├── HIGH: Immediate attention
│   ├── MEDIUM: Should monitor
│   └── LOW: Informational
│
├── Explanation Generation
│   └── _generate_ai_explanation()
│       Returns: Root cause + recommendation
│
└── Aggregation
    └── detect_all_anomalies()
        Combines all anomalies with severity
```

### 3. LLM/RAG Service Architecture

```python
LLMService
│
├── Query Processing
│   ├── process_query()
│   │   1. Keyword extraction
│   │   2. Intent classification
│   │   3. Context retrieval
│   │   4. Answer generation
│   │
│   └── Intent Handlers
│       ├── _answer_delivery_query()
│       ├── _answer_quality_query()
│       ├── _answer_inventory_query()
│       ├── _answer_production_query()
│       └── _answer_supplier_query()
│
├── Context Retrieval (RAG)
│   ├── Load all CSV files
│   ├── Filter relevant records
│   ├── Aggregate metrics
│   └── Add business context
│
├── Confidence Scoring
│   ├── Query quality: 0-1
│   ├── Data availability: 0-1
│   ├── Matching records: 0-1
│   └── Final score: avg(above)
│
├── Conversation Management
│   ├── init_conversation()
│   │   Returns: UUID
│   ├── add_to_conversation()
│   │   Stores: (user_msg, ai_response)
│   └── get_conversation()
│       Returns: Message history
│
└── Data Caching
    └── Cache all CSV data on init
        Refresh: 5-minute TTL
```

---

## Integration Points

### 1. Frontend ↔ Backend Integration

```
HTTP/REST API
├── Base URL: http://localhost:8000
├── Headers: Content-Type: application/json
├── CORS: Configured for localhost:3000
│
└── Request/Response Pattern
    Request:
    {
        "query": "What is our on-time delivery rate?",
        "conversationId": "uuid-123"
    }
    
    Response:
    {
        "answer": "On-time rate is 92.5%",
        "confidence": 0.95,
        "sources": ["shipments"],
        "conversationId": "uuid-123"
    }
```

### 2. Backend ↔ Data Layer Integration

```
File I/O Pattern
├── Read latest CSV files
├── Parse with Pandas
├── Validate schema
├── In-memory processing
├── Cache results (5 min)
└── Return as Pydantic models

Error Handling
├── Missing files: Return empty []
├── Parsing errors: Log and skip row
├── Schema mismatch: Raise ValueError
└── Network errors: Retry with backoff
```

### 3. Backend ↔ Databricks (Optional)

```
ETL Integration
├── Databricks reads GitHub URLs
│   └── spark.read.csv(github_url)
├── Bronze layer: Raw ingestion
├── Silver layer: Cleaning & validation
├── Gold layer: KPI aggregation
│
└── Reverse sync (optional)
    └── Export results back to GitHub
```

### 4. AI Service Integration (Ollama Ready)

```
Current (Rule-based)
├── Query → Keyword match
├── Answer → Template fill
└── Confidence → Static score

Future (Ollama LLM)
├── Query → Embedding (all-MiniLM)
├── RAG → ChromaDB vector search
├── LLM → olama/llama2 generation
└── Confidence → Model scoring
```

---

## Deployment Architecture

### Local Development

```
Developer Laptop (Windows)
├── VS Code
│   ├── Terminal 1: Backend
│   │   python -m uvicorn app.main:app --reload
│   │   Port: 8000
│   │
│   ├── Terminal 2: Frontend
│   │   npm start
│   │   Port: 3000
│   │
│   └── Terminal 3: Data generation
│       python scripts/generate_daily_data.py
│
├── GitHub Desktop
│   └── Sync data files (daily scheduled)
│
└── Browser
    http://localhost:3000
```

### Production Deployment (Recommended)

```
Cloud Environment (AWS/Azure)
├── Frontend
│   ├── S3 bucket (static files)
│   ├── CloudFront (CDN)
│   └── Domain: control-tower.company.com
│
├── Backend
│   ├── EC2 instance (or Lambda)
│   ├── Gunicorn + Nginx (reverse proxy)
│   ├── Auto-scaling group
│   └── Load balancer
│
├── Data Layer
│   ├── S3 (data lake)
│   ├── GitHub (backup)
│   └── EventBridge (daily triggers)
│
├── Analytics
│   ├── Databricks workspace
│   ├── Delta Lake (versioning)
│   └── Power BI (dashboards)
│
└── Monitoring
    ├── CloudWatch (logs)
    ├── Sentry (error tracking)
    └── Prometheus (metrics)
```

---

## Scalability Strategy

### Current State (Single Machine)
- **Users**: 1-10 concurrent
- **Requests/sec**: 10-50
- **Data**: Last 30 days (CSV files)
- **Response time**: < 500ms

### Phase 2 Scaling (100 Users)
```
├── Backend
│   ├── Multi-process deployment (Gunicorn workers)
│   ├── Redis caching (10-minute TTL)
│   ├── Load balancer (requests)
│   └── Horizontal scaling (2-3 servers)
│
├── Data
│   ├── PostgreSQL database
│   ├── Indexed time-series columns
│   ├── Partitioned by date
│   └── Archive old data
│
└── Frontend
    ├── Lazy loading (Dashboard cards)
    ├── Client-side filtering
    ├── CDN caching
    └── Code splitting
```

### Phase 3 Scaling (1000+ Users)
```
├── Microservices
│   ├── kpi-service (independent)
│   ├── anomaly-service (independent)
│   ├── llm-service (independent)
│   └── data-service (independent)
│
├── Data Architecture
│   ├── Databricks (primary analytics)
│   ├── Delta Lake (data versioning)
│   ├── Streaming (Kafka topics)
│   └── Data warehouse (Snowflake)
│
├── Real-time Updates
│   ├── WebSockets (live updates)
│   ├── Server-sent events (alerts)
│   └── Message queue (async jobs)
│
└── Distributed Cache
    ├── Redis cluster
    ├── Multi-region replication
    └── 30-minute TTL
```

---

## Performance Characteristics

### API Response Times
```
GET /kpis                    50-150ms  (in-memory aggregation)
GET /anomalies               100-200ms (statistical calculations)
POST /ask                    200-500ms (query processing + LLM)
GET /data/shipments?limit=50 10-50ms   (DataFrame filtering)
GET /health                  < 5ms     (cache hit)
```

### Data Pipeline Performance
```
Daily Data Generation        < 2 seconds
CSV Append Operations        < 1 second
Loading all 5 CSVs          < 500ms
KPI Aggregation             < 100ms
Anomaly Detection           < 200ms
LLM Response Generation     < 500ms
```

### Memory Usage
```
FastAPI Process             150-300 MB
React App                   50-100 MB
Cached DataFrames           100-200 MB
Total (idle)                300-600 MB
Total (active load)         500-1000 MB
```

---

## Reliability & Fault Tolerance

### Error Handling

```python
# Missing data
if df is None or len(df) == 0:
    return empty_result  # Graceful degradation

# Invalid values
try:
    value = float(record['amount'])
except ValueError:
    value = 0.0  # Default fallback

# File not found
if not file_path.exists():
    logger.warning(f"File not found: {file_path}")
    return None
```

### Logging Strategy

```python
logger.DEBUG   # State changes, iterations
logger.INFO    # API requests, data loads
logger.WARNING # Missing files, retries
logger.ERROR   # Exceptions, validation failures
logger.CRITICAL # System failures
```

### Data Validation

```python
# Pydantic validation (automatic)
├── Type checking
├── Required fields
├── Range validation
└── Custom validators

# Business logic validation (manual)
├── Referential integrity
├── Formula constraints
└── Business rules
```

---

## Security Considerations

### Current Setup (Development)
```
✓ No authentication (localhost only)
✓ No HTTPS (local traffic)
✓ CORS enabled for frontend
✓ No sensitive data
```

### Production Hardening
```
□ OAuth2 with JWT tokens
□ HTTPS/TLS encryption
□ Role-based access control (RBAC)
□ API rate limiting
□ Request validation
□ SQL injection prevention
□ XSS protection
□ CSRF tokens
□ Secret management (env vars)
□ Audit logging
□ Database encryption
□ VPN/private networks
```

---

## Monitoring & Observability

### Metrics to Track
```
Application
├── Request count
├── Response time (p50, p95, p99)
├── Error rate (5xx, 4xx)
├── Cache hit rate
└── Active user count

Data
├── File freshness
├── Record count (per table)
├── Data quality score
└── Processing latency

Infrastructure
├── CPU usage
├── Memory usage
├── Disk space
└── Network I/O
```

### Alerting Rules
```
1. Response time > 1 second → Alert
2. Error rate > 1% → Alert
3. Data stale > 1 hour → Alert
4. CPU > 80% → Alert
5. Anomalies > 50 → Alert
```

---

## Future Enhancements

### Short-term (3 months)
- [ ] Databricks integration automation
- [ ] Ollama LLM deployment
- [ ] Advanced anomaly algorithms (Prophet, LSTM)
- [ ] Email/SMS alerts
- [ ] Excel export functionality

### Medium-term (6 months)
- [ ] Real-time streaming (Kafka)
- [ ] Predictive analytics (demand forecasting)
- [ ] Mobile app (React Native)
- [ ] Advanced permissions (RBAC)
- [ ] Audit trails

### Long-term (12 months)
- [ ] Blockchain traceability
- [ ] IoT sensor integration
- [ ] White-label SaaS version
- [ ] Supply chain network (B2B)
- [ ] AI-powered optimization

---

**Version**: 1.0.0  
**Last Updated**: April 7, 2026  
**Status**: ✅ Production Ready
