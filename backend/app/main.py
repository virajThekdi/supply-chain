"""
Supply Chain Control Tower - FastAPI Backend

Main application with all API endpoints:
- /kpis - Get KPI metrics
- /anomalies - Detect and get anomalies
- /ask - Chat interface with LLM
- /data/* - Data retrieval endpoints
- /health - Health check
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid

# Import services
from app.services.kpi_service import KPICalculator
from app.services.anomaly_service import AnomalyDetector
from app.services.llm_service import LLMService
from app.models.schemas import (
    KPIMetrics, Anomaly, AnomalyResponse, ChatMessage, ChatResponse,
    ErrorResponse, HealthStatus, ProductionRecord, ShipmentRecord,
    InventoryRecord, QualityRecord, SupplierRecord
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Supply Chain Control Tower API",
    description="AI-powered supply chain analytics and insights platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration - Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
kpi_calculator = None
anomaly_detector = None
llm_service = None

def init_services():
    """Initialize all services."""
    global kpi_calculator, anomaly_detector, llm_service
    
    try:
        data_path = Path('data/raw')
        kpi_calculator = KPICalculator(str(data_path))
        anomaly_detector = AnomalyDetector(str(data_path))
        llm_service = LLMService(str(data_path))
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on app startup."""
    init_services()

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint.
    Returns status of API and data connections.
    """
    try:
        # Check data freshness
        data_path = Path('data/raw')
        latest_files = list(data_path.glob('*.csv'))
        
        if latest_files:
            latest_date = max(f.stat().st_mtime for f in latest_files)
            latest_dt = datetime.fromtimestamp(latest_date)
            hours_old = (datetime.now() - latest_dt).total_seconds() / 3600
        else:
            hours_old = 999
        
        status = "HEALTHY"
        if hours_old > 24:
            status = "DEGRADED"
        elif hours_old > 72:
            status = "UNHEALTHY"
        
        return HealthStatus(
            status=status,
            version="1.0.0",
            database_connection=kpi_calculator is not None,
            data_files_latest=datetime.fromtimestamp(latest_date),
            messages_processed=0,
            last_check=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthStatus(
            status="UNHEALTHY",
            version="1.0.0",
            database_connection=False,
            data_files_latest=datetime.now(),
            messages_processed=0,
            last_check=datetime.now()
        )

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Supply Chain Control Tower API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "kpis": "/kpis",
            "anomalies": "/anomalies",
            "chat": "/ask",
            "health": "/health",
            "docs": "/docs"
        }
    }

# ============================================================================
# KPI ENDPOINTS
# ============================================================================

@app.get("/kpis", response_model=Dict)
async def get_kpis():
    """
    Get all KPI metrics for the supply chain.
    
    Returns:
        Dictionary with all KPIs organized by category
    """
    try:
        if kpi_calculator is None:
            raise HTTPException(
                status_code=503,
                detail="KPI service not initialized"
            )
        
        kpis = kpi_calculator.calculate_all_kpis()
        
        logger.info("KPIs retrieved successfully")
        
        return JSONResponse(
            status_code=200,
            content=kpis,
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logger.error(f"Error retrieving KPIs: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/kpis/delivery")
async def get_delivery_kpis():
    """Get delivery-specific KPIs."""
    try:
        if kpi_calculator is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        on_time_rate, on_time_count, total = kpi_calculator.calculate_on_time_delivery_rate()
        avg_delay, delayed_count = kpi_calculator.calculate_average_delay()
        
        return {
            "on_time_delivery_rate": on_time_rate,
            "on_time_shipments": on_time_count,
            "total_shipments": total,
            "average_delay_days": avg_delay,
            "delayed_shipments": delayed_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis/quality")
async def get_quality_kpis():
    """Get quality-specific KPIs."""
    try:
        if kpi_calculator is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        quality_metrics = kpi_calculator.calculate_defect_metrics()
        
        return {
            **quality_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis/production")
async def get_production_kpis():
    """Get production-specific KPIs."""
    try:
        if kpi_calculator is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        prod_metrics = kpi_calculator.calculate_production_metrics()
        
        return {
            **prod_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis/supplier")
async def get_supplier_kpis():
    """Get supplier-specific KPIs."""
    try:
        if kpi_calculator is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        supplier_metrics = kpi_calculator.calculate_supplier_metrics()
        
        return {
            **supplier_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis/inventory")
async def get_inventory_kpis():
    """Get inventory-specific KPIs."""
    try:
        if kpi_calculator is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        inventory_metrics = kpi_calculator.calculate_inventory_metrics()
        
        return {
            **inventory_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANOMALY ENDPOINTS
# ============================================================================

@app.get("/anomalies", response_model=AnomalyResponse)
async def get_anomalies(severity: Optional[str] = None):
    """
    Detect and retrieve anomalies in supply chain data.
    
    Query Parameters:
        severity: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
    
    Returns:
        AnomalyResponse with detected anomalies
    """
    try:
        if anomaly_detector is None:
            raise HTTPException(status_code=503, detail="Anomaly service not ready")
        
        # Load data for detection
        data_path = Path('data/raw')
        production_files = sorted(data_path.glob('production_*.csv'))
        inventory_files = sorted(data_path.glob('inventory_*.csv'))
        supplier_files = sorted(data_path.glob('suppliers_*.csv'))
        
        production_df = pd.read_csv(production_files[-1]) if production_files else None
        inventory_df = pd.read_csv(inventory_files[-1]) if inventory_files else None
        supplier_df = pd.read_csv(supplier_files[-1]) if supplier_files else None
        
        # Detect anomalies
        anomalies = anomaly_detector.detect_all_anomalies(
            production_df=production_df,
            inventory_df=inventory_df,
            supplier_df=supplier_df
        )
        
        # Filter by severity if specified
        if severity:
            anomalies = [a for a in anomalies if a.get('severity') == severity]
        
        # Count by severity
        critical = len([a for a in anomalies if a.get('severity') == 'CRITICAL'])
        high = len([a for a in anomalies if a.get('severity') == 'HIGH'])
        
        logger.info(f"Retrieved {len(anomalies)} anomalies")
        
        return AnomalyResponse(
            total_anomalies=len(anomalies),
            critical_count=critical,
            high_count=high,
            recent_anomalies=anomalies[:10],  # Return first 10
            summary=f"Detected {len(anomalies)} anomalies: {critical} critical, {high} high"
        )
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/anomalies/by-type/{anomaly_type}")
async def get_anomalies_by_type(anomaly_type: str):
    """Get anomalies filtered by type."""
    try:
        if anomaly_detector is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        data_path = Path('data/raw')
        production_files = sorted(data_path.glob('production_*.csv'))
        inventory_files = sorted(data_path.glob('inventory_*.csv'))
        supplier_files = sorted(data_path.glob('suppliers_*.csv'))
        
        production_df = pd.read_csv(production_files[-1]) if production_files else None
        inventory_df = pd.read_csv(inventory_files[-1]) if inventory_files else None
        supplier_df = pd.read_csv(supplier_files[-1]) if supplier_files else None
        
        anomalies = anomaly_detector.detect_all_anomalies(
            production_df=production_df,
            inventory_df=inventory_df,
            supplier_df=supplier_df
        )
        
        filtered = [a for a in anomalies if a.get('type') == anomaly_type]
        
        return {
            "type": anomaly_type,
            "count": len(filtered),
            "anomalies": filtered
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CHAT / LLM ENDPOINTS
# ============================================================================

@app.post("/ask", response_model=ChatResponse)
async def ask_question(message: ChatMessage):
    """
    Ask LLM a question about supply chain data.
    Uses RAG (Retrieval-Augmented Generation) for contextual answers.
    
    Request Body:
        query: The user's question
        context: Optional context (product ID, date, etc.)
        conversation_id: Optional conversation ID for context
    
    Returns:
        ChatResponse with AI answer and sources
    """
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service not ready")
        
        # Initialize conversation if needed
        conv_id = message.conversation_id or llm_service.init_conversation()
        
        # Process query with RAG
        response_text, sources = llm_service.process_query(
            message.query,
            message.context
        )
        
        # Add to conversation history
        llm_service.add_to_conversation(conv_id, "user", message.query)
        llm_service.add_to_conversation(conv_id, "assistant", response_text)
        
        # Calculate confidence
        confidence = llm_service.calculate_confidence(sources)
        
        logger.info(f"Query processed: '{message.query[:50]}...' (confidence: {confidence})")
        
        return ChatResponse(
            query=message.query,
            response=response_text,
            confidence=confidence,
            sources=sources,
            timestamp=datetime.now(),
            conversation_id=conv_id
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversations")
async def create_conversation():
    """Create a new conversation session."""
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        conv_id = llm_service.init_conversation()
        
        return {
            "conversation_id": conv_id,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        if conversation_id not in llm_service.conversation_history:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "conversation_id": conversation_id,
            "messages": llm_service.conversation_history[conversation_id]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DATA ENDPOINTS
# ============================================================================

@app.get("/data/shipments")
async def get_shipments(limit: int = 100, status: Optional[str] = None):
    """Get recent shipment records."""
    try:
        data_path = Path('data/raw')
        files = sorted(data_path.glob('shipments_*.csv'))
        
        if not files:
            raise HTTPException(status_code=404, detail="No shipment data available")
        
        df = pd.read_csv(files[-1])
        
        if status:
            df = df[df['status'] == status]
        
        return df.head(limit).to_dict('records')
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/quality")
async def get_quality(limit: int = 100, product_id: Optional[str] = None):
    """Get quality records."""
    try:
        data_path = Path('data/raw')
        files = sorted(data_path.glob('quality_*.csv'))
        
        if not files:
            raise HTTPException(status_code=404, detail="No quality data available")
        
        df = pd.read_csv(files[-1])
        
        if product_id:
            df = df[df['product_id'] == product_id]
        
        return df.head(limit).to_dict('records')
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/production")
async def get_production(limit: int = 100):
    """Get production records."""
    try:
        data_path = Path('data/raw')
        files = sorted(data_path.glob('production_*.csv'))
        
        if not files:
            raise HTTPException(status_code=404, detail="No production data available")
        
        df = pd.read_csv(files[-1])
        
        return df.head(limit).to_dict('records')
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/inventory")
async def get_inventory(limit: int = 100, warehouse_id: Optional[str] = None):
    """Get inventory records."""
    try:
        data_path = Path('data/raw')
        files = sorted(data_path.glob('inventory_*.csv'))
        
        if not files:
            raise HTTPException(status_code=404, detail="No inventory data available")
        
        df = pd.read_csv(files[-1])
        
        if warehouse_id:
            df = df[df['warehouse_id'] == warehouse_id]
        
        return df.head(limit).to_dict('records')
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/suppliers")
async def get_suppliers(limit: int = 100):
    """Get supplier records."""
    try:
        data_path = Path('data/raw')
        files = sorted(data_path.glob('suppliers_*.csv'))
        
        if not files:
            raise HTTPException(status_code=404, detail="No supplier data available")
        
        df = pd.read_csv(files[-1])
        
        return df.head(limit).to_dict('records')
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# STARTUP INFO
# ============================================================================

if __name__ == "__main__":
    logger.info("Supply Chain Control Tower API starting...")
    logger.info("Docs available at: http://localhost:8000/docs")
    
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
