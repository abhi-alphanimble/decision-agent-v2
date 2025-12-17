# Standard library imports
import asyncio
import json
import os
import time
from typing import Optional

# Third-party imports
import requests
from fastapi import FastAPI, Request, status, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Local imports - Handlers
from .handlers.decision_handlers import (
    handle_propose_command,
    handle_approve_command,
    handle_reject_command,
    handle_show_command,
    handle_myvote_command,
    handle_add_command,
    handle_list_command,
    handle_search_command,
    handle_help_command,
    handle_summarize_command,
    handle_suggest_command,
    handle_config_command,
    handle_sync_zoho_command,
    handle_connect_zoho_command
)
from .handlers.member_handlers import handle_member_joined_channel, handle_member_left_channel

# Local imports - Core
from .command_parser import parse_message, get_help_text, CommandType, DecisionAction
from .database import crud
from .dependencies import get_db, get_db_session, verify_database_connection, run_in_threadpool
from .models import Decision, Vote, ChannelConfig
from .schemas import HealthResponse, RootResponse, StatusResponse, ErrorResponse

# Local imports - Services
from .ai.ai_client import ai_client
from .slack import slack_client
from .integrations.zoho_oauth import router as zoho_oauth_router
from .integrations.dashboard import dashboard_router
from .utils import get_utc_now
from .utils.slack_parsing import parse_slash_command, parse_event_message, parse_member_event

# Database
from database.base import check_db_connection, engine, Base

# Configure logging
from .config import configure_logging, get_context_logger

# Initialize structured logging unless we're running tests (pytest sets
# `PYTEST_CURRENT_TEST`). Avoid configuring global handlers during test
# collection to prevent interference with pytest capture.
if not (os.getenv('PYTEST_CURRENT_TEST') or os.getenv('TESTING')):
    configure_logging(env=os.getenv('ENV', 'development'))

# Use get_context_logger regardless; configure_logging populates the
# implementation in the module. In test mode this will use the default
# lightweight adapter defined in `logging_config.py`.
logger = get_context_logger(__name__)

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

# Include OAuth routers for Zoho CRM integration
app.include_router(zoho_oauth_router)
app.include_router(dashboard_router)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and attach context where possible."""
    start_time = time.time()

    # Try to read body safely for logging (do not consume stream for later handlers)
    try:
        body_bytes = await request.body()
        body_text = body_bytes.decode('utf-8', errors='replace')
    except Exception:
        body_text = ''

    # Redact obvious sensitive values
    redacted = body_text
    for secret_key in ['token', 'secret', 'password', 'access_token']:
        redacted = redacted.replace(secret_key, '[REDACTED]')

    # Extract user/channel if present in form-encoded or json payload
    user_id = None
    channel_id = None
    try:
        content_type = request.headers.get('content-type', '')
        if 'application/x-www-form-urlencoded' in content_type and redacted:
            from urllib.parse import parse_qs
            parsed = parse_qs(redacted)
            user_id = parsed.get('user_id', [None])[0]
            channel_id = parsed.get('channel_id', [None])[0]
        elif 'application/json' in content_type and redacted:
            try:
                parsed = json.loads(redacted)
                # Slack events wrap user in different places
                user_id = parsed.get('user_id') or parsed.get('event', {}).get('user')
                channel_id = parsed.get('channel_id') or parsed.get('event', {}).get('channel')
            except Exception:
                pass
    except Exception:
        pass

    # Bind context to logger for this request
    request_logger = get_context_logger(__name__, user_id=user_id, channel_id=channel_id)
    request_logger.info("Incoming request", extra={"method": request.method, "path": str(request.url.path), "body_preview": redacted[:100]})

    try:
        response = await call_next(request)
    except Exception as exc:
        request_logger.exception("Error while handling request")
        raise

    duration_ms = round((time.time() - start_time) * 1000, 2)
    request_logger.info("Request completed", extra={"status_code": response.status_code, "duration_ms": duration_ms})
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
            "timestamp": get_utc_now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting up Slack Decision Agent API...")
    
    # Ensure database tables exist before handling requests with retry logic
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting database connection (attempt {attempt}/{max_retries})...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables are up to date")
            break
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"⚠️ Database connection attempt {attempt} failed: {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"❌ Failed to ensure database tables exist after {max_retries} attempts: {e}", exc_info=True)
                raise

    # Quick connectivity check
    if check_db_connection():
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
    """Health check endpoint with status of all services."""
    # Check database
    db_connected = check_db_connection()
    
    # Check AI client
    ai_status = "ready" if getattr(ai_client, 'initialized', False) and getattr(ai_client, 'model', None) else "not_configured"
    
    # Check Slack client
    slack_status = "not_configured"
    if hasattr(slack_client, 'client') and slack_client.client is not None:
        slack_status = "ready"
    elif hasattr(slack_client, 'signing_secret') and slack_client.signing_secret:
        slack_status = "partial"  # Has signing secret but no client (maybe missing token)
    
    # Overall health - database is critical, others are optional
    is_healthy = db_connected
    
    response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": get_utc_now(),
        "database": "connected" if db_connected else "disconnected",
        "ai": ai_status,
        "slack": slack_status
    }
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "status": response["status"],
            "timestamp": response["timestamp"].isoformat(),
            "database": response["database"],
            "ai": response["ai"],
            "slack": response["slack"]
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
        "server_time": get_utc_now(),
        "database_status": db_status,
        "total_decisions": total_decisions,
        "total_votes": total_votes
    }


# ============================================================================
# SYNC HELPER FUNCTIONS (run in thread pool to avoid blocking async event loop)
# ============================================================================

def _handle_member_event_sync(event_type: str, user_id: str, user_name: str, channel_id: str, team_id: str = "") -> None:
    """
    Synchronous handler for member events. Runs in thread pool.
    
    Args:
        event_type: Type of event (member_joined_channel, member_left_channel)
        user_id: Slack user ID
        user_name: User's display name
        channel_id: Slack channel ID
        team_id: Slack team/workspace ID for multi-workspace support
    """
    with get_db_session() as db:
        if event_type == "member_joined_channel":
            handle_member_joined_channel(user_id, user_name, channel_id, db, team_id)
        elif event_type == "member_left_channel":
            handle_member_left_channel(user_id, user_name, channel_id, db, team_id)


def _handle_decision_command_sync(
    parsed: "ParsedCommand",
    user_id: str,
    user_name: str,
    channel_id: str,
    team_id: str = ""
) -> dict:
    """
    Synchronous handler for decision commands. Runs in thread pool.
    
    This function contains all database operations and runs in a thread pool
    to avoid blocking the async event loop.
    
    Args:
        parsed: Parsed command data
        user_id: Slack user ID
        user_name: User's display name
        channel_id: Slack channel ID
        team_id: Slack team/workspace ID for multi-workspace support
    
    Returns:
        Response dict to send back to Slack
    """
    from .command_parser import ParsedCommand, DecisionAction
    
    with get_db_session() as db:
        response = None
        
        if parsed.action == DecisionAction.PROPOSE:
            response = handle_propose_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db,
                team_id=team_id
            )
            
        elif parsed.action == DecisionAction.APPROVE:
            response = handle_approve_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db,
                team_id=team_id
            )
            
        elif parsed.action == DecisionAction.REJECT:
            response = handle_reject_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db,
                team_id=team_id
            )
            
        elif parsed.action == DecisionAction.SHOW:
            response = handle_show_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )
            
        elif parsed.action == DecisionAction.MYVOTE:
            response = handle_myvote_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )
            
        elif parsed.action == DecisionAction.LIST:
            response = handle_list_command(
                parsed=parsed,
                channel_id=channel_id,
                db=db
            )

        elif parsed.action == DecisionAction.ADD:
            response = handle_add_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db,
                team_id=team_id
            )
            
        elif parsed.action == DecisionAction.SEARCH:
            response = handle_search_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )

        elif parsed.action == DecisionAction.CONFIG:
            response = handle_config_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db,
                team_id=team_id
            )

        elif parsed.action == DecisionAction.SUMMARIZE:
            response = handle_summarize_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )

        elif parsed.action == DecisionAction.SUGGEST:
            response = handle_suggest_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )

        elif parsed.action == DecisionAction.SYNC_ZOHO:
            response = handle_sync_zoho_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db,
                team_id=team_id
            )

        elif parsed.action == DecisionAction.CONNECT_ZOHO:
            response = handle_connect_zoho_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db,
                team_id=team_id
            )

        else:
            response = {
                "text": f"⏳ Command `{parsed.action}` is coming soon!",
                "response_type": "ephemeral"
            }
        
        return response or {"text": "Command processed", "response_type": "ephemeral"}


# ============================================================================
# ASYNC EVENT PROCESSOR
# ============================================================================

async def process_slack_event(event_data: dict):
    """
    Process Slack event in background.
    
    Database operations are run in a thread pool to avoid blocking the event loop.
    Multi-workspace support: team_id is extracted and passed to handlers.
    """
    try:
        logger.info(f"Processing event: {event_data}")
        
        # Extract team_id for multi-workspace support
        team_id = event_data.get("team_id", "")
        
        # Handle member events (member_joined_channel, member_left_channel)
        if event_data.get("type") in ["member_joined_channel", "member_left_channel"]:
            user_id = event_data.get("user") or event_data.get("user_id", "")
            channel_id = event_data.get("channel") or event_data.get("channel_id", "")
            event_type = event_data.get("type")

            # Get user info using workspace-specific client
            user_name = "Unknown"
            if team_id:
                try:
                    with get_db_session() as db:
                        from .slack.client import get_client_for_team
                        ws_client = get_client_for_team(team_id, db)
                        if ws_client:
                            user_info = ws_client.get_user_info(user_id)
                            user_name = user_info.get("real_name", user_info.get("name", "Unknown"))
                except Exception as e:
                    logger.warning(f"Could not get user info for {user_id}: {e}")

            # Run sync DB operation in thread pool
            await run_in_threadpool(
                _handle_member_event_sync,
                event_type, user_id, user_name, channel_id, team_id
            )
            return

        # Handle slash command
        if event_data.get("command"):
            raw_text = event_data.get("raw_text", "")
            user_id = event_data.get("user_id", "")
            user_name = event_data.get("user_name", "")
            channel_id = event_data.get("channel_id", "")
            response_url = event_data.get("response_url", "")
            team_id = event_data.get("team_id", "")  # Get team_id from slash command
            
            # Parse command (sync but fast, no DB)
            parsed = parse_message(raw_text)

            # Normalize action to DecisionAction enum
            try:
                if parsed.action and isinstance(parsed.action, str):
                    parsed.action = DecisionAction(parsed.action)
            except Exception:
                pass

            logger.info(f"✅ Parsed: {parsed.model_dump()}")
            
            if not parsed.is_valid:
                logger.warning(f"❌ Invalid: {parsed.error_message}")
                if response_url:
                    try:
                        requests.post(response_url, json={
                            "text": f"❌ Error: {parsed.error_message}",
                            "response_type": "ephemeral"
                        })
                    except Exception as e:
                        logger.debug(f"Failed to send error response: {e}")
                return
            
            # Handle HELP (no DB needed)
            if parsed.command_type == CommandType.HELP:
                help_text = get_help_text()
                logger.info(f"📖 Help command - sending help text")
                if response_url:
                    try:
                        resp = requests.post(response_url, json={
                            "text": help_text,
                            "response_type": "ephemeral"
                        })
                        logger.info(f"📖 Help response status: {resp.status_code}")
                    except Exception as e:
                        logger.error(f"❌ Failed to send help response: {e}")
                return
            
            # Handle DECISION commands (DB operations in thread pool)
            if parsed.command_type == CommandType.DECISION:
                # Run all DB operations in thread pool, passing team_id
                response = await run_in_threadpool(
                    _handle_decision_command_sync,
                    parsed, user_id, user_name, channel_id, team_id
                )
                
                # Send response back to Slack
                logger.info(f"📤 Attempting to send response to Slack. response_url={bool(response_url)}")
                if response_url and response is not None:
                    try:
                        response_text = response.get('text', '')
                        logger.info(f"📤 Sending to Slack: {response_text[:100]}...")
                        slack_response = requests.post(response_url, json=response, timeout=10)
                        logger.info(f"📤 Slack response status: {slack_response.status_code}")
                    except Exception as e:
                        logger.error(f"Error sending response: {e}", exc_info=True)
                else:
                    logger.warning(f"⚠️ Not sending response: response_url={response_url}, response={response}")
            
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        # Try to send error to user
        if event_data.get("response_url"):
            try:
                requests.post(event_data["response_url"], json={
                    "text": f"❌ An error occurred: {str(e)}",
                    "response_type": "ephemeral"
                })
            except Exception as notify_err:
                logger.debug(f"Failed to notify user of error: {notify_err}")


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
                event_type = event.get('type')
                team_id = payload.get('team_id', '')
                logger.info(f"Received event: {event_type} from team {team_id}")

                # App lifecycle events
                if event_type == 'app_uninstalled':
                    background_tasks.add_task(handle_app_uninstalled, team_id)
                    return {"ok": True}
                
                if event_type == 'tokens_revoked':
                    tokens = event.get('tokens', {})
                    background_tasks.add_task(handle_tokens_revoked, team_id, tokens)
                    return {"ok": True}

                # Member events (join/leave) -> use dedicated parser
                if event_type in ['member_joined_channel', 'member_left_channel']:
                    parsed_event = parse_member_event(event)
                    if parsed_event:
                        # Add team_id to parsed event for multi-workspace support
                        parsed_event['team_id'] = team_id
                        logger.info(f"Parsed member event: {parsed_event}")
                        background_tasks.add_task(process_slack_event, parsed_event)
                else:
                    # Fallback to standard message/event parser
                    parsed_event = parse_event_message(event)
                    if parsed_event:
                        # Add team_id to parsed event for multi-workspace support
                        parsed_event['team_id'] = team_id
                        logger.info(f"Parsed event: {parsed_event}")
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
                response_text = f"⏳ Processing your command..."
                
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


# Slack Events API endpoint (alias for webhook)
@app.post("/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    """
    Slack Events API endpoint - routes to the same handler as /webhook/slack
    """
    return await slack_webhook(request, background_tasks)

# Slack OAuth installation endpoints
@app.get("/slack/install")
async def slack_install():
    """
    Initiates the Slack OAuth 2.0 installation flow.
    Redirects the user to Slack's authorization URL.
    """
    from app.config import config
    from fastapi.responses import RedirectResponse
    
    # Scopes required for the distributed bot
    # See: https://api.slack.com/scopes
    scopes = [
        # Messaging
        "chat:write",            # Send messages
        "chat:write.public",     # Send messages to channels without joining
        
        # Commands & Events
        "commands",              # Add slash commands
        "app_mentions:read",     # React to @mentions
        
        # Channel history (for context)
        "channels:history",      # Read public channel messages
        "groups:history",        # Read private channel messages
        "im:history",            # Read DM messages
        "mpim:history",          # Read group DM messages
        
        # User & Channel info
        "users:read",            # Get user information
        "channels:read",         # Get channel information
        "groups:read",           # Get private channel information
        "team:read",             # Get workspace information
        
        # Channel membership (for member count)
        "channels:join",         # Join public channels
    ]
    
    # Build redirect URI
    redirect_uri = f"{config.APP_BASE_URL}/slack/install/callback"
    
    # Build the OAuth URL
    oauth_url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={config.SLACK_CLIENT_ID}"
        f"&scope={','.join(scopes)}"
        f"&redirect_uri={redirect_uri}"
    )
    
    return RedirectResponse(url=oauth_url)


@app.get("/slack/install/callback")
async def slack_callback(request: Request, code: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Handles the Slack OAuth 2.0 redirect after a user approves the app installation.
    This is the Redirect URL.
    """
    from .config import config
    from slack_sdk.web import WebClient
    from fastapi.responses import HTMLResponse
    from .utils.workspace import save_installation
    from .templates import SUCCESS_PAGE_HTML
    
    if not code:
        # User denied installation
        error = request.query_params.get("error", "No code received")
        logger.error(f"❌ OAuth failed: {error}")
        return JSONResponse(
            content={"message": f"Installation failed. Reason: {error}"},
            status_code=400
        )

    try:
        # 1. Exchange the temporary code for permanent tokens
        client = WebClient()
        
        # Build redirect URI - must match what's configured in Slack
        redirect_uri = f"{config.APP_BASE_URL}/slack/install/callback"
        
        oauth_response = client.oauth_v2_access(
            client_id=config.SLACK_CLIENT_ID,
            client_secret=config.SLACK_CLIENT_SECRET,
            code=code,
            redirect_uri=redirect_uri,
        )
        
        # 2. Extract the necessary tokens/IDs
        team_id = oauth_response["team"]["id"]
        team_name = oauth_response["team"]["name"]
        bot_token = oauth_response["access_token"]
        bot_user_id = oauth_response["bot_user_id"]
        
        logger.info(f"🔑 Successfully installed in Team ID: {team_id} ({team_name})")
        
        # 3. Save installation with encrypted token
        save_installation(
            db=db,
            team_id=team_id,
            team_name=team_name,
            access_token=bot_token,
            bot_user_id=bot_user_id
        )
        
        # 4. Return success page
        success_html = SUCCESS_PAGE_HTML.format(
            team_name=team_name,
            team_id=team_id
        )
        return HTMLResponse(content=success_html, status_code=200)

    except Exception as e:
        logger.error(f"❌ OAuth Access Error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Failed to complete app installation."
        )


# ============================================================================
# STATIC PAGES (Privacy Policy, Support)
# ============================================================================

@app.get("/privacy")
async def privacy_policy():
    """Privacy Policy page - required for Slack App Directory."""
    from fastapi.responses import HTMLResponse
    from .templates import PRIVACY_POLICY_HTML
    return HTMLResponse(content=PRIVACY_POLICY_HTML, status_code=200)


@app.get("/support")
async def support_page():
    """Support page - required for Slack App Directory."""
    from fastapi.responses import HTMLResponse
    from .templates import SUPPORT_PAGE_HTML
    return HTMLResponse(content=SUPPORT_PAGE_HTML, status_code=200)


# ============================================================================
# APP LIFECYCLE EVENTS (Uninstall, Token Revocation)
# ============================================================================

async def handle_app_uninstalled(team_id: str):
    """
    Handle app_uninstalled event - clean up installation data.
    """
    from .utils.workspace import remove_installation
    
    logger.info(f"🗑️ App uninstalled from team {team_id}")
    
    with get_db_session() as db:
        remove_installation(db, team_id)


async def handle_tokens_revoked(team_id: str, tokens: dict):
    """
    Handle tokens_revoked event - tokens are no longer valid.
    """
    from .utils.workspace import remove_installation
    
    logger.warning(f"🔒 Tokens revoked for team {team_id}: {tokens}")
    
    # If bot tokens are revoked, remove the installation
    if tokens.get("oauth", []) or tokens.get("bot", []):
        with get_db_session() as db:
            remove_installation(db, team_id)

