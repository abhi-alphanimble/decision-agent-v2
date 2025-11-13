
from fastapi import FastAPI, Request, status, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import time
import logging
import json

from app.schemas import HealthResponse, RootResponse, StatusResponse, ErrorResponse
from app.dependencies import get_db, verify_database_connection
from app.models import Decision, Vote
from app.slack_client import slack_client
from app.slack_utils import parse_slash_command, parse_event_message
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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration_ms}ms")
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
    """Initialize on startup"""
    logger.info("Starting up Slack Decision Agent API...")
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
    """Root endpoint"""
    return {
        "message": "Slack Decision Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
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

# System status
@app.get("/api/v1/status", response_model=StatusResponse)
async def system_status(db: Session = Depends(get_db)):
    """Get system status"""
    try:
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

# Background task for processing Slack events
async def process_slack_event(event_data: dict):
    """Process Slack event in background"""
    try:
        logger.info(f"Processing Slack event: {event_data.get('type')}")
        # Add your event processing logic here
        # This runs after returning 200 OK to Slack
    except Exception as e:
        logger.error(f"Error processing Slack event: {e}")

# Slack webhook endpoint
@app.post("/webhook/slack")
async def slack_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receive webhooks from Slack (slash commands, events, interactions).
    Must respond within 3 seconds per Slack requirements.
    """
    try:
        # Get request body
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # Get headers
        timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
        signature = request.headers.get('X-Slack-Signature', '')
        
        # Verify Slack signature
        if not slack_client.verify_slack_signature(body_str, timestamp, signature):
            logger.warning("Invalid Slack signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse payload
        content_type = request.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            # Event subscription or interactive component
            payload = await request.json()
            
            # Handle URL verification challenge
            if payload.get('type') == 'url_verification':
                logger.info("Handling URL verification challenge")
                return {"challenge": payload.get('challenge')}
            
            # Handle event callback
            if payload.get('type') == 'event_callback':
                event = payload.get('event', {})
                logger.info(f"Received event: {event.get('type')}")
                
                # Parse event
                parsed_event = parse_event_message(event)
                if parsed_event:
                    logger.info(f"Parsed event: {parsed_event}")
                    # Add to background tasks for processing
                    background_tasks.add_task(process_slack_event, parsed_event)
                
                # Return 200 OK immediately
                return {"ok": True}
        
        elif 'application/x-www-form-urlencoded' in content_type:
            # Slash command or interactive component (form-encoded)
            from urllib.parse import parse_qs
            parsed_body = parse_qs(body_str)
            
            # Convert to dict with single values
            payload = {k: v[0] if len(v) == 1 else v for k, v in parsed_body.items()}
            
            # Check if it's a slash command
            if 'command' in payload:
                logger.info(f"Received slash command: {payload.get('command')}")
                
                # Parse command
                parsed_command = parse_slash_command(payload)
                logger.info(f"Parsed command: {parsed_command}")
                
                # Quick acknowledgment response
                response_text = f"Processing your command: `{parsed_command['subcommand']}`"
                
                # Add actual processing to background tasks
                background_tasks.add_task(process_slack_event, parsed_command)
                
                # Return immediate response (within 3 seconds)
                return {
                    "response_type": "ephemeral",
                    "text": response_text
                }
        
        logger.warning(f"Unknown content type: {content_type}")
        return {"ok": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Slack webhook: {e}", exc_info=True)
        # Still return 200 to Slack to avoid retries
        return {"ok": False, "error": str(e)}
