
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import time
import logging

from app.schemas import HealthResponse, RootResponse, StatusResponse, ErrorResponse
from app.dependencies import get_db, verify_database_connection
from app.models import Decision, Vote
from database.base import test_connection, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Slack Decision Agent API",
    description="API for managing group decisions and votes via Slack",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with method, path, status code, and duration"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration_ms}ms"
    )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    logger.info("Starting up Slack Decision Agent API...")
    
    # Test database connection
    if test_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed!")
    
    logger.info("Server started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("Shutting down Slack Decision Agent API...")
    engine.dispose()
    logger.info("Database connections closed")

# Root endpoint
@app.get("/", response_model=RootResponse)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Slack Decision Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns 200 if healthy, 503 if database is down.
    """
    db_connected = test_connection()
    
    response = {
        "status": "healthy" if db_connected else "unhealthy",
        "timestamp": datetime.utcnow(),
        "database": "connected" if db_connected else "disconnected"
    }
    
    status_code = status.HTTP_200_OK if db_connected else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": response["status"],
            "timestamp": response["timestamp"].isoformat(),
            "database": response["database"]
        }
    )

# System status endpoint
@app.get("/api/v1/status", response_model=StatusResponse)
async def system_status(db: Session = Depends(get_db)):
    """
    Get detailed system status including database statistics.
    """
    try:
        # Get database statistics
        total_decisions = db.query(Decision).count()
        total_votes = db.query(Vote).count()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        total_decisions = 0
        total_votes = 0
        db_status = "disconnected"
    
    return {
        "api_version": "1.0.0",
        "server_time": datetime.utcnow(),
        "database_status": db_status,
        "total_decisions": total_decisions,
        "total_votes": total_votes
    }
